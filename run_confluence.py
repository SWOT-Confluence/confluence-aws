"""Run Confluence

This script runs the Confluence workflow and submits jobs to AWS Batch.

Arguements:
  -c: Path to YAML configuration file
  -s: Indicates simulated data run
  -k: Unique SSM encryption key identifier

PyYAML must be installed in the environment prior to execution.

It requires the following classes: Confluence, Stage, Algorithm and Job all 
contained within the Confluence module.

This script can also be imported as a module and contains the following 
functions:
    * create_logger - creates a logger object used to log status
    * main - the main entrypoint of the script
    
Example execution: python3 run_confluence.py -c /path/to/confluence.yaml
"""

# Standard imports
import argparse
from datetime import datetime
import logging
from pathlib import Path
import sys

# Third-party imports
import boto3
import botocore
import yaml

# Local imports
from confluence.Confluence import Confluence

def create_args():
    """Create and return argparser with arguments."""

    arg_parser = argparse.ArgumentParser(description="Retrieve a list of S3 URIs")
    arg_parser.add_argument("-c",
                            "--configyaml",
                            type=str,
                            help="Path to YAML configuration file")
    arg_parser.add_argument("-s",
                        "--simulated",
                        help="Indication to run on simulated data",
                        action="store_true")
    arg_parser.add_argument("-k",
                            "--ssmkey",
                            type=str,
                            help="Unique SSM encryption key identifier.")
    arg_parser.add_argument("-r",
                        "--renew",
                        help="Indication to enable renew Lambda",
                        action="store_true")
    return arg_parser

def create_logger(log_to_console=True, log_file=None, log_to_file=False):
    """Creates and sets a Logger object to allow logging of status.

    Status is logged to console if log_to_console is set to True and status 
    is logged to file if a log_file is defined and log_to_file is set to True.

    If log_to_file is set to True then a file path must be defined in 
    configuration YAML.

    Default is to log to console and not to file.

    Parameters
    ----------
    log_file: Path, optional
        Path to log file
    log_to_console: boolean, optional
        Whether to log to console
    log_to_file: boolean, optional
        Whether to log to a file referenced in configuration YAML.
    """

    logger = logging.getLogger("confluence_logger")
    logger.setLevel(logging.DEBUG)

    # Console logging
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_format = logging.Formatter("%(asctime)s : %(message)s")
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

    # File logging
    if log_to_file and log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter("%(asctime)s : %(message)s")
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger

def store_s3_creds(key):
    """Get temporary creds for S3-hosted simulated data.
    
    Note data is stored in Confluence AWS and the credentials are determined
    from what ever user account runs this script.
    """
    
    # Retrieve temporary credentials
    client = boto3.client('sts')
    response = client.get_session_token(DurationSeconds=43200)
    creds = {
        "accessKeyId": response["Credentials"]["AccessKeyId"],
        "secretAccessKey": response["Credentials"]["SecretAccessKey"],
        "sessionToken": response["Credentials"]["SessionToken"],
        "expiration": response["Credentials"]["Expiration"].strftime("%Y-%m-%d %H:%M:%S+00:00")
    }
    
    # Store temporary credentials in parameter store    
    ssm_client = boto3.client('ssm', region_name="us-west-2")
    try:
        response = ssm_client.put_parameter(
            Name="s3_creds_key",
            Description="Temporary SWOT S3 bucket key",
            Value=creds["accessKeyId"],
            Type="SecureString",
            KeyId=key,
            Overwrite=True,
            Tier="Standard"
        )
        response = ssm_client.put_parameter(
            Name="s3_creds_secret",
            Description="Temporary SWOT S3 bucket secret",
            Value=creds["secretAccessKey"],
            Type="SecureString",
            KeyId=key,
            Overwrite=True,
            Tier="Standard"
        )
        response = ssm_client.put_parameter(
            Name="s3_creds_token",
            Description="Temporary SWOT S3 bucket token",
            Value=creds["sessionToken"],
            Type="SecureString",
            KeyId=key,
            Overwrite=True,
            Tier="Standard"
        )
        response = ssm_client.put_parameter(
            Name="s3_creds_expiration",
            Description="Temporary SWOT S3 bucket expiration",
            Value=creds["expiration"],
            Type="SecureString",
            KeyId=key,
            Overwrite=True,
            Tier="Standard"
        )
    except botocore.exceptions.ClientError as e:
        raise e
    
def enable_renew():
    """Enable EventBridge schedule that invokes renew Lambda.
    
    Schedule runs every 50 minutes as creds expire every 1 hour.
    """
    
    scheduler = boto3.client("scheduler")
    try:
        # Get schedule
        get_response = scheduler.get_schedule(Name="confluence-renew")
        
        # Update schedule
        update_response = scheduler.update_schedule(
            Name=get_response["Name"],
            GroupName=get_response["GroupName"],
            FlexibleTimeWindow=get_response["FlexibleTimeWindow"],
            ScheduleExpression=get_response["ScheduleExpression"],
            Target=get_response["Target"],
            State="ENABLED"
        )        
    except botocore.exceptions.ClientError as e:
        raise e
    
def handle_error(error, logger):
    """Print out error message and exit."""
    
    logger.error("Error encountered.")
    logger.error(error)
    logger.error("System exiting.")
    sys.exit(1)

def main():
    """Execute Confluence workflow."""

    start = datetime.now()
    # Get command line arguments and config data
    arg_parser = create_args()
    args = arg_parser.parse_args()
    with open(args.configyaml) as yaml_file:
        config_data = yaml.safe_load(yaml_file)

    # Get a logger to log to file
    log_file = Path(config_data["log_file"]) \
        if len(config_data["log_file"]) != 0 else None
    logger = create_logger(log_file=log_file, log_to_file=True)
    
    try:
        # Store temporary creds if simulated run
        if args.simulated:
            logger.info("Storing S3 credentials for run on simulated data.")
            store_s3_creds(args.ssmkey)
            
        # Enable 'renew' Lambda function to renew S3 creds every 50 minutes
        if args.renew:
            enable_renew()
            logger.info("Enabled 'renew' Lambda function. Function will execute every 50 minutes.")
    
    except botocore.exceptions.ClientError as e:
        handle_error(e, logger)

    # Submit AWS Batch jobs
    confluence = Confluence(args.configyaml)
    confluence.create_stages()
    confluence.execute_stages(logger)

    end = datetime.now()
    logger.info(f"Total execution time: {end - start}")

if __name__ == "__main__":
    main()