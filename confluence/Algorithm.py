# Third-party imports
import botocore

# Local imports
from confluence.Job import Job

class Algorithm:
    """
    A class that represents an algorithm requiring execution in Confluence.

    An Algorithm usually needs to be submitted to AWS Batch as a set of jobs. An
    Algorithm creates Job objects to handle the submission operation.

    Attributes
    ----------
    array_size: int
        size of the AWS Batch job array for each job
    arguments: list
        list of arguments that are submitted to a job
    job_ids: list
        list of job identifiers for jobs submitted to AWS Batch
    jobs: list
        list of Job objects that handle submission to AWS Batch
    name: str
        name of the algorithm
    num_jobs: int
        number of jobs to be created
    
    Methods
    -------
    create_jobs(stage, dependencies)
        creates jobs that can be submitted to AWS Batch
    submit_jobs()
        submits jobs to AWS Batch
    """

    def __init__(self, name, num_jobs, array_size, arguments):
        """
        Parameters
        ----------
        name: str
            name of algorithm
        num_jobs: int
            the number of jobs to be created
        array_size: int
            the size of the AWS Batch job array for each job
        arguments: list
            list of arguments that are submitted for each job
        """

        self.array_size = array_size
        self.arguments = arguments
        self.job_ids = []
        self.jobs = []
        self.name = name
        self.num_jobs = num_jobs

    def create_jobs(self, stage):
        """Create Job objects that are responsible for running the algorithm
        in AWS Batch.

        Parameters
        ----------
            stage: str
                name of the stage that the algorithm is a part of
        """

        for i in range(self.num_jobs):
            job = Job(name=f"{stage}_{self.name}_{i}", job_def=self.name,
                queue=stage)
            if (len(self.arguments) > 0): job.define_arguments(self.arguments)
            if (self.array_size > 0): job.define_array(self.array_size)
            job.define_tags(tag_dict={ "job": f"{stage}_{self.name}_{i}" },
                will_propagate=True)
            self.jobs.append(job)

    def submit_jobs(self, dependencies):
        """Submits jobs to AWS Batch job queue.

        Parameters
        ----------
        dependencies: list
            list of job identifiers that the Algorithm's jobs depend on
        
        Raises
        ------
        botocore.exceptions.ClientError
            if AWS Batch API returns an error response upon job submission
        """

        for job in self.jobs:
            try:
                job.define_dependencies(dependencies)
                job_id = job.submit()
                self.job_ids.append(job_id)
            except botocore.exceptions.ClientError as error:
                raise error