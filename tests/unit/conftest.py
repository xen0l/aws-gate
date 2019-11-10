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
def instance_id():
    return "i-0c32153096cd68a6d"
