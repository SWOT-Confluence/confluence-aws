# Standard imports
import unittest
from unittest.mock import patch

# Local imports
from confluence.Stage import Stage

class TestStage(unittest.TestCase):
    """Tests methods from Stage class."""

    STAGE_DICT = {
        "geobam": { 
            "num_jobs": 2, 
            "array_size": 500, 
            "input_files": ["reaches_1.txt", "reaches_2.txt"]
        }, 
        "hivdi": { 
            "num_jobs": 2, 
            "array_size": 500, 
            "input_files": ["reaches_1.txt", "reaches_2.txt"]
        }, 
        "metroman": { 
            "num_jobs": 2, 
            "array_size": 500, 
            "input_files": ["reaches_1.txt", "reaches_2.txt"]
        }
    }

    def test_create_algorithms(self):
        """Tests the create_algorithms method."""

        stage = Stage("test_stage")
        stage.create_algorithms(self.STAGE_DICT)

        self.assertEqual(3, len(stage.algorithms))

        alg = stage.algorithms[1]
        self.assertEqual(500, alg.array_size)
        self.assertEqual(["reaches_1.txt", "reaches_2.txt"], alg.input_files)
        self.assertEqual(0, len(alg.job_ids))
        self.assertEqual(2, len(alg.jobs))
        self.assertEqual("hivdi", alg.name)
        self.assertEqual(2, alg.num_jobs)

    def test_define_dependencies(self):
        """Tests the define_dependencies method."""

        # Create previous stage that contains dependencies
        stage1 = Stage("test_stage1")
        stage1.create_algorithms(self.STAGE_DICT)
        stage1.algorithms[0].job_ids = ["f00afeb4-354a-4e80-a226-0021a8b38e32",
                    "397fdcd6-5af3-4003-862f-03fcb6594cce"]
        stage1.algorithms[1].job_ids = ["81bf7409-2ea3-4baa-93b8-3c2613b172d0",
                    "fa1f2f66-8975-44ea-87f0-ff569e1302d8"]
        stage1.algorithms[2].job_ids = ["e4bd42df-7330-4de3-9ea2-a8880c57c488",
                    "1d4b37c6-7dfb-4301-99f0-6181fe3ba124"]

        # Create the next stage to test
        stage2 = Stage("test_stage2")
        stage2.define_dependencies(stage1.algorithms)

        expected = [
            "f00afeb4-354a-4e80-a226-0021a8b38e32",
            "397fdcd6-5af3-4003-862f-03fcb6594cce",
            "81bf7409-2ea3-4baa-93b8-3c2613b172d0",
            "fa1f2f66-8975-44ea-87f0-ff569e1302d8",
            "e4bd42df-7330-4de3-9ea2-a8880c57c488",
            "1d4b37c6-7dfb-4301-99f0-6181fe3ba124"
        ]
        
        self.assertListEqual(expected, stage2.dependencies)
    
    @patch("confluence.Job.boto3", autospec=True)
    def test_run_algorithms(self, mock_boto):
        """Tests run_algorithms method."""

        mock_boto.client("batch").submit_job.side_effect = [
            { "jobArn": "amazon-resource-name", 
              "jobName": "test_stage_geobam_0", 
              "jobId": "d90d061b-c16d-4a47-ba25-260727bac56b" }, 
            { "jobArn": "amazon-resource-name", 
              "jobName": "test_stage_geobam_1", 
              "jobId": "134ee8b1-0127-4c4e-aa6d-9bfbcd581aa6" },
            { "jobArn": "amazon-resource-name", 
              "jobName": "test_stage_hivdi_0", 
              "jobId": "1d4b37c6-7dfb-4301-99f0-6181fe3ba124" },
            { "jobArn": "amazon-resource-name", 
              "jobName": "test_stage_hivdi_1", 
              "jobId": "1111161b-c16d-4a47-ba25-260727bac56b" },
            { "jobArn": "amazon-resource-name", 
              "jobName": "test_stage_metroman_0", 
              "jobId": "2222261b-c16d-4a47-ba25-260727bac56b" },
            { "jobArn": "amazon-resource-name", 
              "jobName": "test_stage_metroman_1", 
              "jobId": "3333361b-c16d-4a47-ba25-260727bac56b" },
        ]

        stage1 = Stage("test_stage")
        stage1.dependencies = [
            "f00afeb4-354a-4e80-a226-0021a8b38e32",
            "397fdcd6-5af3-4003-862f-03fcb6594cce",
            "81bf7409-2ea3-4baa-93b8-3c2613b172d0",
        ]
        stage1.create_algorithms(self.STAGE_DICT)
        stage1.run_algorithms()
        
        self.assertEqual(3, len(stage1.submitted))
        self.assertEqual(6, mock_boto.client("batch").submit_job.call_count)

        alg = stage1.algorithms[1]
        expected = ["1d4b37c6-7dfb-4301-99f0-6181fe3ba124", 
                    "1111161b-c16d-4a47-ba25-260727bac56b"]
        self.assertListEqual(expected, alg.job_ids)

        job = alg.jobs[1]
        expected_deps = [
            {"jobId": "f00afeb4-354a-4e80-a226-0021a8b38e32"},
            {"jobId": "397fdcd6-5af3-4003-862f-03fcb6594cce"},
            {"jobId": "81bf7409-2ea3-4baa-93b8-3c2613b172d0"}
        ]
        self.assertListEqual(expected_deps, job.depends_on)