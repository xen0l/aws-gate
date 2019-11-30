import os

import boto3
import placebo
import pytest


@pytest.fixture(name="session")
def placebo_session(request):
    session_kwargs = {"region_name": os.environ.get("AWS_DEFAULT_REGION", "eu-west-1")}
    profile_name = os.environ.get("PLACEBO_PROFILE", None)
    if profile_name:
        session_kwargs["profile_name"] = profile_name

    session = boto3.Session(**session_kwargs)

    prefix = request.function.__name__

    base_dir = os.environ.get("PLACEBO_DIR", os.path.join(os.getcwd(), "placebo"))
    record_dir = os.path.join(base_dir, prefix)

    if not os.path.exists(record_dir):
        os.makedirs(record_dir)

    pill = placebo.attach(session, data_path=record_dir)

    if os.environ.get("PLACEBO_MODE") == "record":
        pill.record()
    else:
        pill.playback()

    return session


@pytest.fixture
def ec2(session):
    return session.resource("ec2", region_name="eu-west-1")


@pytest.fixture
def ec2_ic(session):
    return session.resource("ec2-instance-connect", region_name="eu-west-1")


@pytest.fixture
def ssm(session):
    return session.client("ssm", region_name="eu-west-1")


@pytest.fixture
def ec2_mock(mocker):
    return mocker.MagicMock()


@pytest.fixture
def ec2_ic_mock(mocker):
    return mocker.MagicMock()


@pytest.fixture
def ssm_mock(mocker):
    mock = mocker.MagicMock()
    response = {
        "SessionId": "session-020bf6cd31f912b53",
        "TokenValue": "randomtokenvalue",
    }
    mock.configure_mock(
        **{
            "start_session.return_value": response,
            "terminate_session.return_value": response,
        }
    )
    type(mock.meta).endpoint_url = mocker.PropertyMock(return_value="ssm")
    return mock


@pytest.fixture
def instance_id():
    return "i-0c32153096cd68a6d"


@pytest.fixture
def ssh_key(mocker):
    mock = mocker.MagicMock()
    mock.configure_mock(
        **{
            "public_key.return_value": "ssh-rsa ranodombase64string",
            "key_path.return_value": "/home/user/.aws-gate/key",
        }
    )

    return mock


@pytest.fixture
def config(mocker):
    mock = mocker.MagicMock()
    mock.configure_mock(
        **{
            "get_host.return_value": {
                "alias": "test",
                "name": "SSM-test",
                "profile": "default",
                "region": "eu-west-1",
            }
        }
    )

    return mock


@pytest.fixture
def empty_config(mocker):
    mock = mocker.MagicMock()
    mock.configure_mock(**{"get_host.return_value": {}})

    return mock


@pytest.fixture
def get_instance_details_response():
    return {"availability_zone": "eu-west-1a"}
