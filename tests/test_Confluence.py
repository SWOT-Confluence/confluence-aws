# Standard imports
from enum import auto
from pathlib import Path
import unittest
from unittest.mock import patch

# Third-party imports
import botocore

# Local imports
from confluence.Confluence import Confluence, create_logger
from tests.confluence_response import describe_response, error_response, \
    execute_response, execute_expected

class TestConfluence(unittest.TestCase):
    """Tests methods from Confluence class."""

    CONFIG_FILE = Path(__file__).parent / "data" / "confluence_test.yaml"

    def test_create_stages(self):
        """Tests the create_stages method."""

        confluence = Confluence(self.CONFIG_FILE)
        confluence.create_stages()
        self.assertEqual(7, len(confluence.stages))
        
        stage = confluence.stages[2]
        self.assertEqual(5, len(stage.algorithms))
        self.assertEqual(0, len(stage.dependencies))
        self.assertEqual("flpe", stage.name)
        self.assertEqual(0, len(stage.submitted))

    @patch("confluence.Job.boto3", autospec=True)
    def test_execute_stages(self, mock_boto):
        """Tests the execute_stages method."""

        mock_boto.client("batch").submit_job.side_effect = execute_response
        confluence = Confluence(self.CONFIG_FILE)
        confluence.create_stages()
        confluence.execute_stages()

        self.assertEqual(7, len(confluence.submitted))
        self.assertEqual(11, mock_boto.client("batch").submit_job.call_count)

        stage_total = 0
        [stage_total := stage_total + len(stage.submitted) for stage in confluence.stages]
        self.assertEqual(11, stage_total)

        alg_total = 0
        [alg_total := alg_total + alg.num_jobs for stage in confluence.stages for alg in stage.algorithms]
        self.assertEqual(11, alg_total)

        stage = confluence.stages[3]
        self.assertListEqual(execute_expected, stage.dependencies)
    
    @patch("confluence.Job.boto3", autospec=True)
    @patch("confluence.Confluence.sys", autospec=True)
    @patch("confluence.Confluence.logging", autospec=True)
    @patch.object(Confluence, "terminate_jobs")
    def test_execute_stages_exception(self, mock_terminate, mock_logger, 
        mock_exit, mock_job_boto):
        """Tests execute_stages method when an exception is thrown."""

        error = botocore.exceptions.ClientError(error_response, "Test")
        mock_job_boto.client("batch").submit_job.side_effect = error
        
        exception_config = Path(__file__).parent / "data" / "confluence_test_exception.yaml"
        confluence = Confluence(exception_config)
        confluence.create_stages()
        confluence.execute_stages()
        
        self.assertEqual(1, mock_terminate.call_count)
    
    @patch("confluence.Confluence.boto3", autospec=True)
    @patch("confluence.Job.boto3", autospec=True)
    def test_terminate_jobs(self, mock_job_boto, mock_conf_boto):
        """Tests terminate_jobs method."""

        mock_job_boto.client("batch").submit_job.side_effect = execute_response
        mock_conf_boto.client("batch").describe_jobs.side_effect = describe_response

        confluence = Confluence(self.CONFIG_FILE)
        confluence.create_stages()
        confluence.execute_stages()
        confluence.terminate_jobs()

        self.assertEqual(11, len(confluence.terminated))
        self.assertEqual(0, len(confluence.not_terminated))
        self.assertEqual(6, mock_conf_boto.client("batch").cancel_job.call_count)
        self.assertEqual(5, mock_conf_boto.client("batch").terminate_job.call_count)