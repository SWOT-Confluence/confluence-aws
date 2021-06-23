# Third-party imports
import botocore

# Local imports
from confluence.Algorithm import Algorithm

class Stage:
    """
    A class that represents a stage in the Confluence workflow.

    A Stage creates the Algorithm objects needed to submit AWS Batch jobs that
    require execution for the entire stage.

    Attributes
    ----------
    algorithms: list
        list of Algorithm objects that will be executed
    dependencies: list
        list of job identifiers that the stage depends on
    name: str
        name of the stage
    submitted: list
        list of Algorithm objects that have been submitted to AWS Batch

    Methods
    -------
    create_algorithms()
        creates a list of Algorithm objects
    define_dependencies(alg_list)
        create a list of job identifiers that the Stage depends on
    run_algorithms()
        invokes each Algorithm so that its jobs are submitted to AWS Batch
    """

    def __init__(self, name):
        """
        Parameters
        ----------
        name: str
            name of the stage
        """

        self.algorithms = []
        self.dependencies = []
        self.name = name
        self.submitted = []

    def create_algorithms(self, stage_dict):
        """Create Algorithm objects.

        stage_dict containes the number of jobs, array size, and input file 
        names (list) needed to complete an execution of the algorithm.

        Parameters
        ----------
        stage_dict: dict
            dictionary of data needed to create Algorithm objects
        """

        for key in stage_dict.keys():
            algorithm = Algorithm(name=key, 
                num_jobs=stage_dict[key]["num_jobs"],
                array_size=stage_dict[key]["array_size"], 
                input_files=stage_dict[key]["input_files"])
            self.algorithms.append(algorithm)
            algorithm.create_jobs(self.name)

    def define_dependencies(self, alg_list):
        """Define dependencies by extracting job identifiers from alg_list.

        Parameters
        ----------
        alg_list: list
            list of Algorithm objects
        """
        
        for alg in alg_list:
            self.dependencies.extend(alg.job_ids)

    def run_algorithms(self):
        """Invokes each Algorithm so that all associated jobs are submitted to 
        AWS Batch.

        Raises
        ------
        botocore.exceptions.ClientError
            if AWS Batch API returns an error response upon job submission
        """

        for alg in self.algorithms:
            try:
                alg.submit_jobs(self.dependencies)
                self.submitted.append(alg)
            except botocore.exceptions.ClientError as error:
                raise error