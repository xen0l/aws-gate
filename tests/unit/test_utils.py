import errno
import os
import subprocess
from subprocess import PIPE

import pytest
from botocore import credentials
from botocore.exceptions import ClientError

from aws_gate import __version__
from aws_gate.constants import DEFAULT_GATE_BIN_PATH
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
        self._available_profiles = [f"profile{i}" for i in range(5)]

    @property
    def available_profiles(self):
        return self._available_profiles


def test_existing_profile(mocker):
    mocker.patch("aws_gate.utils._create_aws_session", return_value=MockSession())

    assert is_existing_profile("profile1")
    assert not is_existing_profile("nonexistentprofile")


def test_create_aws_session(mocker):
    session_mock = mocker.patch(
        "aws_gate.utils.boto3.session", return_value=mocker.MagicMock()
    )

    _create_aws_session(region_name="eu-west-1")

    assert session_mock.Session.called
    assert session_mock.Session.call_args == mocker.call(region_name="eu-west-1")


def test_create_aws_session_user_agent():
    session = _create_aws_session(region_name="eu-west-1")

    # pylint: disable=protected-access
    assert f"aws-gate/{__version__}" in session._session.user_agent()


def test_aws_session_file_cache_is_set():
    session = _create_aws_session(region_name="eu-west-1")

    # pylint: disable=protected-access
    assume_role_provider = session._session.get_component(
        "credential_provider"
    ).get_provider("assume-role")

    assert isinstance(assume_role_provider.cache, credentials.JSONFileCache)
    assert assume_role_provider.cache._working_dir == os.path.join(
        os.path.expanduser("~"), ".aws/cli/cache"
    )


def test_create_aws_session_with_profile(mocker):
    session_mock = mocker.patch(
        "aws_gate.utils.boto3.session", return_value=mocker.MagicMock()
    )
    _create_aws_session(region_name="eu-west-1", profile_name="default")

    assert session_mock.Session.called
    assert session_mock.Session.call_args == mocker.call(
        region_name="eu-west-1", profile_name="default"
    )


def test_create_aws_profile_credentials_from_env_vars(mocker):
    credentials_dict = {
        "AWS_ACCESS_KEY_ID": "a",
        "AWS_SECRET_ACCESS_KEY": "b",
        "AWS_SESSION_TOKEN": "c",
    }
    session_mock = mocker.patch(
        "aws_gate.utils.boto3.session", return_value=mocker.MagicMock()
    )
    mocker.patch.dict(os.environ, credentials_dict)

    _create_aws_session()

    assert session_mock.Session.called
    assert session_mock.Session.call_args == mocker.call(  # noqa: S106
        aws_access_key_id="a", aws_secret_access_key="b", aws_session_token="c"
    )


def test_get_aws_client(mocker):
    mock = mocker.patch(
        "aws_gate.utils._create_aws_session", return_value=mocker.MagicMock()
    )

    get_aws_client(service_name="ec2", region_name="eu-west-1")

    assert mock.called
    assert mock.mock_calls == [mocker.call(profile_name=None, region_name="eu-west-1")]


def test_get_aws_resource(mocker):
    mock = mocker.patch(
        "aws_gate.utils._create_aws_session", return_value=mocker.MagicMock()
    )
    get_aws_resource(service_name="ec2", region_name="eu-west-1")

    assert mock.called


def test_region_validation():
    assert is_existing_region(region_name=AWS_REGIONS[0])
    assert not is_existing_region(region_name="unknown-region-1")


def test_execute(mocker):
    mock_output = mocker.MagicMock(stdout=b"output")
    mocker.patch("aws_gate.utils.subprocess.run", return_value=mock_output)

    assert execute("ls", ["-l"]) == "output"


def test_execute_environment(mocker):
    mock_output = mocker.MagicMock(stdout=b"output")
    m = mocker.patch("aws_gate.utils.subprocess.run", return_value=mock_output)

    execute("ls", ["-l"])

    assert m.call_args_list[0][1]["env"] is not None
    assert DEFAULT_GATE_BIN_PATH in m.call_args_list[0][1]["env"]["PATH"]


def test_execute_command_exited_with_nonzero_rc(mocker):
    mock = mocker.patch(
        "aws_gate.utils.subprocess.run",
        side_effect=subprocess.CalledProcessError(returncode=1, cmd="error"),
    )
    execute("/usr/bin/ls", ["-l"])

    assert mock.called


def test_execute_command_not_found(mocker):
    mocker.patch(
        "aws_gate.utils.subprocess.run",
        side_effect=OSError(errno.ENOENT, os.strerror(errno.ENOENT)),
    )
    with pytest.raises(ValueError):
        execute("/usr/bin/ls", ["-l"])


def test_execute_plugin(mocker):
    mocker.patch("aws_gate.utils.execute", return_value="output")
    output = execute_plugin(["--version"], stdout=PIPE, stderrr=PIPE)

    assert output == "output"


def test_execute_plugin_args(mocker):
    m = mocker.patch("aws_gate.utils.execute", return_value="output")

    execute_plugin(["--version"], stdout=PIPE, stderr=PIPE)

    assert m.called
    assert "['--version']" in str(m.call_args[0])
    assert m.call_args[1]["stdout"] == PIPE
    assert m.call_args[1]["stderr"] == PIPE


def test_fetch_instance_details_from_config(config):
    expected_instance_name = config.get_host()["name"]
    expected_profile = config.get_host()["profile"]
    expeted_region = config.get_host()["region"]

    instance_name, profile, region = fetch_instance_details_from_config(
        config, "instance_name", "profile", "region"
    )

    assert expected_instance_name == instance_name
    assert expected_profile == profile
    assert expeted_region == region


def test_fetch_instance_details_from_config_with_empty_config(empty_config):
    expected_instance_name = "instance_name"
    expected_profile = "profile"
    expeted_region = "region"

    instance_name, profile, region = fetch_instance_details_from_config(
        empty_config, expected_instance_name, expected_profile, expeted_region
    )

    assert expected_instance_name == instance_name
    assert expected_profile == profile
    assert expeted_region == region


def test_get_instance_details_aws_api_exception(ec2_mock, instance_id):
    # https://github.com/surbas/pg2kinesis/blob/master/tests/test_stream.py#L20
    error_response = {"Error": {"Code": "ResourceInUseException"}}
    ec2_mock.configure_mock(
        **{"instances.filter.side_effect": ClientError(error_response, "random_ec2_op")}
    )

    with pytest.raises(AWSConnectionError):
        get_instance_details(instance_id, ec2=ec2_mock)


def test_get_instance_details(instance_id, ec2):
    expected_details = {
        "instance_id": "i-0c32153096cd68a6d",
        "vpc_id": "vpc-1981f29759da4a354",
        "private_dns_name": "ip-10-69-104-49.eu-west-1.compute.internal",
        "private_ip_address": "10.69.104.49",
        "public_dns_name": "ec2-18-201-115-108.eu-west-1.compute.amazonaws.com",
        "public_ip_address": "18.201.115.108",
        "availability_zone": "eu-west-1a",
        "instance_name": "dummy-instance",
    }

    details = get_instance_details(instance_id, ec2=ec2)

    assert details == expected_details
