# Standard imports
import unittest
from unittest.mock import patch

# Local imports
from confluence.Algorithm import Algorithm

class TestAlgorithm(unittest.TestCase):
    """Tests methods from Algorithm class."""

    DEPENDENCIES = ["f00afeb4-354a-4e80-a226-0021a8b38e32",
                    "397fdcd6-5af3-4003-862f-03fcb6594cce",
                    "81bf7409-2ea3-4baa-93b8-3c2613b172d0",
                    "fa1f2f66-8975-44ea-87f0-ff569e1302d8",
                    "e4bd42df-7330-4de3-9ea2-a8880c57c488"]
    EXPECTED_DEPS = [
            { "jobId": "f00afeb4-354a-4e80-a226-0021a8b38e32" },
            { "jobId": "397fdcd6-5af3-4003-862f-03fcb6594cce" },
            { "jobId": "81bf7409-2ea3-4baa-93b8-3c2613b172d0" },
            { "jobId": "fa1f2f66-8975-44ea-87f0-ff569e1302d8" },
            { "jobId": "e4bd42df-7330-4de3-9ea2-a8880c57c488" }
        ]
    INPUT_FILES = ["reaches_1.txt", "reaches_2.txt", "reaches_3.txt"]

    def test_create_jobs(self):
        """Tests the create_jobs method."""

        alg = Algorithm("test_alg", 3, 500, ["reaches.json"])
        alg.create_jobs("test_flpe")
        self.assertEqual(3, len(alg.jobs))

        job = alg.jobs[1]
        self.assertEqual({ "size": 500 }, job.array_props)
        self.assertEqual({ "command": ["reaches.json"] }, job.overrides)
        self.assertEqual("test_alg", job.job_def)
        self.assertEqual("test_flpe_test_alg_1", job.name)
        self.assertTrue(job.propagate_tags)
        self.assertEqual("test_flpe", job.queue)
        self.assertEqual({ "attempts": 1 }, job.retry_strategy)
        self.assertEqual({ "job": "test_flpe_test_alg_1"}, job.tags)

    @patch("confluence.Job.boto3", autospec=True)
    def test_submit_jobs(self, mock_boto):
        """Test submit_jobs method."""

        mock_boto.client("batch").submit_job.side_effect = [
            { "jobArn": "amazon-resource-name", 
              "jobName": "test_flpe_test_alg_0", 
              "jobId": "d90d061b-c16d-4a47-ba25-260727bac56b" }, 
            { "jobArn": "amazon-resource-name", 
              "jobName": "test_flpe_test_alg_1", 
              "jobId": "134ee8b1-0127-4c4e-aa6d-9bfbcd581aa6" },
            { "jobArn": "amazon-resource-name", 
              "jobName": "test_flpe_test_alg_1", 
              "jobId": "1d4b37c6-7dfb-4301-99f0-6181fe3ba124" }
        ]

        alg = Algorithm("test_alg", 3, 500, self.INPUT_FILES)
        alg.create_jobs("test_flpe")
        alg.submit_jobs(self.DEPENDENCIES)

        self.assertEqual(self.EXPECTED_DEPS, alg.jobs[0].depends_on)
        self.assertEqual(self.EXPECTED_DEPS, alg.jobs[1].depends_on)
        self.assertEqual(self.EXPECTED_DEPS, alg.jobs[2].depends_on)

        expected = ["d90d061b-c16d-4a47-ba25-260727bac56b", 
                    "134ee8b1-0127-4c4e-aa6d-9bfbcd581aa6", 
                    "1d4b37c6-7dfb-4301-99f0-6181fe3ba124"]
        self.assertEqual(expected, alg.job_ids)

        
