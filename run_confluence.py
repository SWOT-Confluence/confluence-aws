"""Run Confluence

This script runs the Confluence workflow and submits jobs to AWS Batch.

PyYAML must be installed in the environment prior to execution.

It requires the following classes: Confluence, Stage, Algorithm and Job all 
contained within the Confluence module.

This script can also be imported as a module and contains the following 
functions:
    * create_logger - creates a logger object used to log status
    * main - the main entrypoint of the script
"""

# Standard imports
from datetime import datetime
import logging
from pathlib import Path

# Third-party imports
import yaml

# Local imports
from confluence.Confluence import Confluence

CONFIG_FILE = Path("")

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

def main():
    """Execute Confluence workflow."""

    start = datetime.now()
    with open(CONFIG_FILE) as yaml_file:
        config_data = yaml.safe_load(yaml_file)

    log_file = Path(config_data["log_file"]) \
        if len(config_data["log_file"]) != 0 else None
    logger = create_logger(log_file=log_file, log_to_file=True)

    confluence = Confluence(CONFIG_FILE)
    confluence.create_stages()
    confluence.execute_stages(logger)

    end = datetime.now()
    logger.info(f"Total execution time: {end - start}")

if __name__ == "__main__":
    main()