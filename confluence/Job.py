# Third-party imports
import botocore
import boto3

class Job:
    """
    A class that represents a job in AWS Batch.

    Attributes
    ----------
    array_props: dict
        dictionary of array properties including array size (max 10,000)
    overrides: dict
        dictionary of container overrides including command arguments
    depends_on: list
        list of dictionary job identifiers for jobs that this job depends on
    job_def: str
        the name of the job definition that the job is created from
    name: str
        the name of the job
    propagate_tags: bool
        whether to propagate tags to ECS task associated with job (default False)
    queue: str
        the name of the queue the job will be submitted to
    retry_strategy: dict
        dictionary of retry strategy properties including rety attempts
    tags: dict
        dictionary of key, value pairs that will be used to tag each job

    Methods
    -------
    submit()
        Submits job to AWS Batch job queue for execution.
    """

    def __init__(self, name, job_def, queue, retry_attempts=1):
        """
        Parameters
        ----------
        name: str
            the name of the job
        job_def: str
            the name of the job definition that the job is created from
        queue: str
            the name of the queue the job will be submitted to
        retry_attempts: int, optional
            the number of times to retry a failed job (Default is 1)
        """

        self.array_props = {}
        self.overrides = {}
        self.depends_on = []
        self.job_def = job_def
        self.name = name
        self.propagate_tags = False
        self.queue = queue
        self.retry_strategy = { "attempts": retry_attempts }
        self.tags = {}

    def define_arguments(self, args_list):
        """Define additional arguments that are passed to the container 
        entrypoint during the job submission process.

        Parameters
        ----------
        args_list: list
            list of arguments
        """

        self.overrides["command"] = args_list

    def define_array(self, array_size):
        """Defines an array job with a property of size.

        Parameters
        ----------
        array_size: int
            The size of the job array (max is 10,000)
        """

        self.array_props["size"] = array_size 

    def define_dependencies(self, id_list):
        """Defines a list of job identifiers that the job depends on.

        The job will not run until the jobs referenced in the id_list have 
        completed.

        Parameters
        ----------
        id_list: list
            list of job identifiers the job depends on
        """

        for identifier in id_list:
            self.depends_on.append({ "jobId": identifier })       

    def define_tags(self, tag_dict, will_propagate=False):
        """Defines the tags used for the job and whether they will propagate
        to the ECS task associated with the job.

        Parameters
        ----------
        tag_dict: dict
            dictionary of key, value pairs that are associated with the job
        will_propagate: bool, optional
            whether the job will propagate to the ECS task (default is False)
        """

        self.tags = tag_dict
        self.propagate_tags = will_propagate

    def submit(self):
        """Submits job to AWS Batch job queue.

        Raises
        ------
        botocore.exceptions.ClientError
            if AWS Batch API returns an error response upon job submission

        Returns
        -------
        job_id: int
            unique job identifier for the submitted job
        """

        try:
            batch = boto3.client("batch")
            response = batch.submit_job(
                jobName=self.name,
                jobDefinition=self.job_def,
                jobQueue=self.queue,
                arrayProperties=self.array_props,
                containerOverrides=self.overrides,
                retryStrategy=self.retry_strategy,
                dependsOn=self.depends_on,
                tags=self.tags,
                propagateTags=self.propagate_tags
            )
            return response["jobId"]
        except botocore.exceptions.ClientError as error:
            raise error