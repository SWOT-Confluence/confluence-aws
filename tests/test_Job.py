# Standard imports
import unittest
from unittest.mock import patch

# Local imports
from confluence.Job import Job

class TestJob(unittest.TestCase):
    """Tests methods from Job class."""

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

    def test_define_arguments(self):
        """Tests the define_arguments method."""

        job = Job("test_job", "test_def", "test_queue")
        job.define_arguments(["reaches.txt"])
        expected = { "command" : ["reaches.txt"] }
        self.assertEqual(expected, job.overrides)

    def test_define_array(self):
        """Tests the define_array method."""

        job = Job("test_job", "test_def", "test_queue")
        job.define_array(500)
        expected = { "size": 500 }
        self.assertEqual(expected, job.array_props)

    def test_define_dependencies(self):
        """Tests the define_dependencies method."""

        job = Job("test_job", "test_def", "test_queue")
        job.define_dependencies(self.DEPENDENCIES)
        expected = self.EXPECTED_DEPS
        self.assertEqual(expected, job.depends_on)

    def test_define_tags(self):
        """Test define_tags method."""

        job = Job("test_job", "test_def", "test_queue")
        job.define_tags({ "ec2_job": "alg_test_0" })
        expected = { "ec2_job": "alg_test_0" }
        self.assertEqual(expected, job.tags)
        self.assertFalse(job.propagate_tags)

    @patch("confluence.Job.boto3", autospec=True)
    def test_submit_job(self, mock_boto):
        """Test submit_job method."""

        mock_boto.client("batch").submit_job.return_value = {
            "jobArn": "amazon-resource-name",
            "jobName": "test_job",
            "jobId": "dfdf42df-7330-4de3-9ea2-a8880c57c488"
        }
        
        job = Job("test_job", "test_def", "test_queue")
        job.define_arguments(["reaches.txt"])
        job.define_array(500)
        job.define_dependencies(self.DEPENDENCIES)
        job.define_tags({ "ec2_job": "alg_test_0" })
        job.submit()

        expected_dependencies = self.EXPECTED_DEPS
        mock_boto.client("batch").submit_job.assert_called_once_with(
            jobName="test_job",
            jobDefinition="test_def",
            jobQueue="test_queue",
            arrayProperties={ "size": 500 },
            containerOverrides={ "command" : ["reaches.txt"] },
            retryStrategy={ "attempts": 1 },
            dependsOn=expected_dependencies,
            tags={ "ec2_job": "alg_test_0" },
            propagateTags=False
        )