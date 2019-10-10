import errno
import os
import subprocess
import unittest
from unittest.mock import patch, MagicMock, call

from botocore.exceptions import ClientError
from hypothesis import given
from hypothesis.strategies import lists, text
from placebo.utils import placebo_session

from aws_gate.exceptions import AWSConnectionError
from aws_gate.utils import (
    is_existing_profile,
    _create_aws_session,
    get_aws_client,
    get_aws_resource,
    AWS_REGIONS,
    is_existing_region,
    execute,
    execute_plugin,
    fetch_instance_details_from_config,
    get_instance_details,
)


# pylint: disable=too-few-public-methods
class MockSession:
    def __init__(self):
        self._available_profiles = ["profile{}".format(i) for i in range(5)]

    @property
    def available_profiles(self):
        return self._available_profiles


class TestUtils(unittest.TestCase):
    @placebo_session
    def setUp(self, session):
        self.ec2 = session.resource("ec2", region_name="eu-west-1")

        self.instance_id = "i-0c32153096cd68a6d"

        self.config_data = {
            "alias": "test",
            "name": "SSM-test",
            "profile": "default",
            "region": "eu-west-1",
        }

        self.config = MagicMock()
        self.config.configure_mock(**{"get_host.return_value": self.config_data})

        self.empty_config = MagicMock()
        self.empty_config.configure_mock(**{"get_host.return_value": {}})

    def test_existing_profile(self):
        with patch("aws_gate.utils._create_aws_session", return_value=MockSession()):
            self.assertTrue(is_existing_profile("profile1"))
            self.assertFalse(is_existing_profile("nonexistentprofile"))

    def test_create_aws_session(self):
        with patch(
            "aws_gate.utils.boto3.session", return_value=MagicMock()
        ) as session_mock:
            _create_aws_session(region_name="eu-west-1")

            self.assertTrue(session_mock.Session.called)
            self.assertEqual(
                session_mock.Session.call_args, call(region_name="eu-west-1")
            )

    def test_create_aws_session_with_profile(self):
        with patch(
            "aws_gate.utils.boto3.session", return_value=MagicMock()
        ) as session_mock:
            _create_aws_session(region_name="eu-west-1", profile_name="default")

            self.assertTrue(session_mock.Session.called)
            self.assertEqual(
                session_mock.Session.call_args,
                call(region_name="eu-west-1", profile_name="default"),
            )

    def test_create_aws_profile_credentials_from_env_vars(self):
        credentials_dict = {
            "AWS_ACCESS_KEY_ID": "a",
            "AWS_SECRET_ACCESS_KEY": "b",
            "AWS_SESSION_TOKEN": "c",
        }
        with patch(
            "aws_gate.utils.boto3.session", return_value=MagicMock()
        ) as session_mock, patch.dict(os.environ, credentials_dict):
            _create_aws_session()

            self.assertTrue(session_mock.Session.called)
            self.assertEqual(
                session_mock.Session.call_args,
                call(
                    aws_access_key_id="a",
                    aws_secret_access_key="b",
                    aws_session_token="c",
                ),
            )

    def test_get_aws_client(self):
        with patch(
            "aws_gate.utils._create_aws_session", return_value=MagicMock()
        ) as mock:
            get_aws_client(service_name="ec2", region_name="eu-west-1")

            self.assertTrue(mock.called)
            self.assertEqual(
                mock.mock_calls, [call(profile_name=None, region_name="eu-west-1")]
            )

    def test_get_aws_resource(self):
        with patch(
            "aws_gate.utils._create_aws_session", return_value=MagicMock()
        ) as mock:
            get_aws_resource(service_name="ec2", region_name="eu-west-1")

            self.assertTrue(mock.called)

    def test_region_validation(self):
        self.assertTrue(is_existing_region(region_name=AWS_REGIONS[0]))
        self.assertFalse(is_existing_region(region_name="unknown-region-1"))

    @given(text(), lists(text()))
    def test_execute(self, cmd, args):
        mock_output = MagicMock(stdout=b"output")

        with patch("aws_gate.utils.subprocess.run", return_value=mock_output):
            self.assertEqual(execute(cmd, args), "output")

    def test_execute_command_exited_with_nonzero_rc(self):
        with patch(
            "aws_gate.utils.subprocess.run",
            side_effect=subprocess.CalledProcessError(returncode=1, cmd="error"),
        ) as mock:
            execute("/usr/bin/ls", ["-l"])

            self.assertTrue(mock.called)

    def test_execute_command_not_found(self):
        with patch(
            "aws_gate.utils.subprocess.run",
            side_effect=OSError(errno.ENOENT, os.strerror(errno.ENOENT)),
        ):
            with self.assertRaises(ValueError):
                execute("/usr/bin/ls", ["-l"])

    def test_execute_plugin(self):
        with patch("aws_gate.utils.execute", return_value="output"):
            output = execute_plugin(["--version"], capture_output=True)
            self.assertEqual(output, "output")

    def test_execute_plugin_args(self):
        with patch("aws_gate.utils.execute", return_value="output") as m:
            execute_plugin(["--version"], capture_output=True)

            self.assertTrue(m.called)
            self.assertIn("['--version'], capture_output=True", str(m.call_args))

    def test_fetch_instance_details_from_config(self):
        expected_instance_name = self.config_data["name"]
        expected_profile = self.config_data["profile"]
        expeted_region = self.config_data["region"]

        instance_name, profile, region = fetch_instance_details_from_config(
            self.config, "instance_name", "profile", "region"
        )

        self.assertEqual(expected_instance_name, instance_name)
        self.assertEqual(expected_profile, profile)
        self.assertEqual(expeted_region, region)

    def test_fetch_instance_details_from_config_with_empty_config(self):
        expected_instance_name = "instance_name"
        expected_profile = "profile"
        expeted_region = "region"

        instance_name, profile, region = fetch_instance_details_from_config(
            self.empty_config, expected_instance_name, expected_profile, expeted_region
        )

        self.assertEqual(expected_instance_name, instance_name)
        self.assertEqual(expected_profile, profile)
        self.assertEqual(expeted_region, region)

    def test_get_instance_details_aws_api_exception(self):
        ec2_mock = MagicMock()

        # https://github.com/surbas/pg2kinesis/blob/master/tests/test_stream.py#L20
        error_response = {"Error": {"Code": "ResourceInUseException"}}
        ec2_mock.configure_mock(
            **{
                "instances.filter.side_effect": ClientError(
                    error_response, "random_ec2_op"
                )
            }
        )

        with self.assertRaises(AWSConnectionError):
            get_instance_details(self.instance_id, ec2=ec2_mock)

    def test_get_instance_details(self):
        expected_details = {
            "instance_id": "i-0c32153096cd68a6d",
            "vpc_id": "vpc-1981f29759da4a354",
            "private_dns_name": "ip-10-69-104-49.eu-west-1.compute.internal",
            "private_ip_address": "10.69.104.49",
            "public_dns_name": "ec2-18-201-115-108.eu-west-1.compute.amazonaws.com",
            "public_ip_addess": "18.201.115.108",
            "availability_zone": "eu-west-1a",
            "instance_name": "dummy-instance",
        }

        details = get_instance_details(self.instance_id, ec2=self.ec2)

        self.assertEqual(details, expected_details)
