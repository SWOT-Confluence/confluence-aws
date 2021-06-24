# Standard imports
import logging
import sys

# Third-party imports
import botocore
import boto3
import yaml

# Local imports
from confluence.Stage import Stage

class Confluence:
    """
    A class that orchestrates the components required to submit AWS Batch jobs.

    Confluence creates and executes Stage objects store Algorithm objects
    that invoke Job objects to submit jobs to AWS Batch.

    Attributes
    ----------
    config_data: dict
        dcitionary of data required to run Confluence and create Stage objects
    logger: Logger
        Logger object used to log status of Confluence
    not_terminaged: list
        list of job identifiers that could not be terminated
    stages: list
        list of Stage objects
    submitted: list
        list of Stage objects that have been submitted to AWS Batch
    terminated: list
        list of job identifiers that have been terminated

    Methods
    -------
    create_logger()
        creates Logger object used to log status
    create_stages()
        creates Stage objects
    execute_stages()
        runs the Algorithms stored in Stage objects
    terminate_jobs()
        terminates any running job in AWS Batch
    """

    def __init__(self, config_file, log_file=None):
        """
        Parameters
        ----------
        config_file : Path
            path to YAML file that contains configuration data
        log_file: Path
            path to log file
        """

        with open(config_file) as yaml_file:
            self.config_data = yaml.safe_load(yaml_file)
        self.logger = create_logger(log_file)
        self.stages = []
        self.submitted = []
        self.terminated = []
        self.not_terminated = []

    def create_stages(self):
        """Create Stage objects based on configuration file data."""

        for key in self.config_data["stages"].keys():
            stage = Stage(key)
            self.stages.append(stage)
            stage.create_algorithms(self.config_data["stages"][key])

    def execute_stages(self):
        """Invoke Algorithm objects to submit jobs to AWS Batch for all stages.

        If a job submission fails, the exception is propagated from the Job and
        handled here; all submitted jobs are terminated.
        
        Raises
        ------
        botocore.exceptions.ClientError
            if AWS Batch API returns an error response upon job submission
        """
        for stage in self.stages:
            try:
                index = self.stages.index(stage)
                if index > 0:
                    stage.define_dependencies(self.stages[index-1].algorithms)
                stage.run_algorithms()
                self.submitted.append(stage)
            
            except botocore.exceptions.ClientError as error:
                self.logger.critical(f"Job submission FAILED and all jobs will be TERMINATED.")
                self.logger.critical(f"Job failed with the following error: {error}")

                self.terminate_jobs()
                self.logger.info(f"{len(self.terminated)} jobs terminated.")
                self.logger.info(f"Jobs that could not be terminated and require manual termination: {', '.join(self.not_terminated)}.")
                self.logger.info(f"Program exiting.")
                sys.exit("Job submission failure")

    def terminate_jobs(self):
        """Terminate jobs that have been submitted to AWS Batch.

        Uses self.submitted list to determine submitted jobs. Jobs in SUBMITTED,
        PENDING, or RUNNABLE state are cancelled while jobs in STARTING or 
        RUNNING state are terminated. This transitions the job's state to FAILED.
        """

        batch = boto3.client("batch")
        job_ids = [ job_id for stage in self.submitted \
                        for alg in stage.algorithms \
                            for job_id in alg.job_ids ]
        for job_id in job_ids:
            try:
                status = batch.describe_jobs(jobs=[job_id])["jobs"][0]["status"]
                if status == "SUBMITTED" or status == "PENDING" \
                    or status == "RUNNABLE":
                    
                    batch.cancel_job(jobId=job_id, 
                        reason="Job submission failed")
                    self.terminated.append(job_id)
                
                elif status == "STARTING" or status == "RUNNING":
                    batch.terminate_job(jobId=job_id, 
                        reason="Job submission failed")
                    self.terminated.append(job_id)
                
                else:
                    self.not_terminated.append(job_id)
            
            except botocore.exceptions.ClientError as error:
                self.logger.critical(f"Job termination FAILURE for {job_id}.")
                self.logger.critical("You will need to manually terminate any remaining jobs.")
                self.logger.critical(f"Job failed with the following error: {error}")
                self.logger.critical("Program exiting.")
                sys.exit("Job termination failure")        

def create_logger(log_path=None):
    """Creates a Logger object to allow logging of status.

    Status is logged to console and file if a log path is provided, otherwise
    status is only logged to the console.

    Parameters
    ----------
    log_path: Path, optional
       path to log file

    Returns
    -------
    Logger object
    """

    logger = logging.getLogger("confluence_logger")
    logger.setLevel(logging.DEBUG)

    # Console logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter("%(asctime)s - %(message)s")
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File logging
    if log_path:
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter("%(asctime)s - %(message)s")
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger
