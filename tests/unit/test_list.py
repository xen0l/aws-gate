import io
import unittest
from unittest.mock import patch

from placebo.utils import placebo_session

from aws_gate.list import list_instances


class TestList(unittest.TestCase):
    @placebo_session
    def setUp(self, session):
        self.ec2 = session.resource("ec2", region_name="eu-west-1")
        self.ssm = session.client("ssm", region_name="eu-west-1")

    def test_list_instances(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout, patch(
            "aws_gate.list.get_aws_resource", return_value=self.ec2
        ), patch("aws_gate.list.get_aws_client", return_value=self.ssm), patch(
            "aws_gate.decorators.is_existing_region", return_value=True
        ), patch(
            "aws_gate.decorators.is_existing_profile", return_value=True
        ):
            list_instances(profile_name="default", region_name="eu-west-1")
            self.assertEqual(
                mock_stdout.getvalue(), "i-0c32153096cd68a6d - dummy-instance\n"
            )

    def test_list_instances_invalid_profile(self):
        with patch("aws_gate.decorators.is_existing_region", return_value=True):
            with self.assertRaises(ValueError):
                list_instances(profile_name="invalid-profile", region_name="eu-west-1")

    def test_list_instances_invalid_region(self):
        with patch("aws_gate.decorators.is_existing_profile", return_value=True):
            with self.assertRaises(ValueError):
                list_instances(profile_name="default", region_name="invalid-region")
