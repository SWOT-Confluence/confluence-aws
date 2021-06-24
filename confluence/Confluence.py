# Standard imports
import csv
import logging
from pathlib import Path
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
        dictionary of data required to run Confluence and create Stage objects
    log_file: Path
        Path to log file
    logger: Logger
        Logger object used to log status of Confluence
    not_terminaged: list
        list of job identifiers that could not be terminated
    stages: list
        list of Stage objects
    submission_file: Path
        Path to file where submission results are written
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

    def __init__(self, config_file):
        """
        Parameters
        ----------
        config_file : Path
            path to YAML file that contains configuration data
        """

        with open(config_file) as yaml_file:
            self.config_data = yaml.safe_load(yaml_file)
        self.log_file = Path(self.config_data["log_file"]) \
            if len(self.config_data["log_file"]) != 0 else None
        self.logger = None
        self.stages = []
        self.submission_file = Path(self.config_data["submission_file"]) \
            if len(self.config_data["submission_file"]) != 0 else None
        self.submitted = []
        self.terminated = []
        self.not_terminated = []

    def create_logger(self, log_to_console=True, log_to_file=False):
        """Creates and sets a Logger object to allow logging of status.

        Status is logged to console if log_to_console is set to True and status 
        is logged to file is log_to_file is set to True.

        If log_to_file is set to True then a file path must be defined in 
        configuration YAML.

        Default is to log to console and not to file.

        Parameters
        ----------
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
            console_format = logging.Formatter("%(asctime)s - %(message)s")
            console_handler.setFormatter(console_format)
            logger.addHandler(console_handler)

        # File logging
        if log_to_file and self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter("%(asctime)s - %(message)s")
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)

        self.logger = logger

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
                if self.submission_file: self.write_submitted()
                self.logger.info(f"All algorithm's jobs for {stage} stage have been submitted.")
            
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

    def write_submitted(self):
        """ Write information on each job that has been submitted to AWS Batch.

        The following information is written to a CSV file taken from config
        yaml: stage name, algorithm name, job name, and job identifier
        """

        with open(self.submission_file, mode='w') as csv_file:
            fieldnames = ["stage", "algorithm", "job_name", "job_id"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for stage in self.stages:
                for alg in stage.algorithms:
                    for job in alg.jobs:
                        writer.writerow({
                            "stage" : stage.name,
                            "algorithm" : alg.name,
                            "job_name": job.name,
                            "job_id": job.job_id
                        })
    
    def set_log_file(self, log_file):
        self.log_file = Path(log_file)
    
    def set_submission_file(self, submission_file):
        self.submission_file = Path(submission_file)
