import os

import boto3
import placebo
import pytest


@pytest.fixture(scope="function")
def placebo_session(request):
    session_kwargs = {"region_name": os.environ.get("AWS_DEFAULT_REGION", "eu-west-1")}
    profile_name = os.environ.get("PLACEBO_PROFILE", None)
    if profile_name:
        session_kwargs["profile_name"] = profile_name

    session = boto3.Session(**session_kwargs)

    # prefix = request.function.__name__

    base_dir = os.environ.get("PLACEBO_DIR", os.path.join(os.getcwd(), "placebo"))
    # record_dir = os.path.join(base_dir, prefix)
    record_dir = os.path.join(base_dir)

    if not os.path.exists(record_dir):
        os.makedirs(record_dir)

    pill = placebo.attach(session, data_path=record_dir)

    if os.environ.get("PLACEBO_MODE") == "record":
        pill.record()
    else:
        pill.playback()

    return session


@pytest.fixture
def ec2(placebo_session):
    return placebo_session.resource("ec2", region_name="eu-west-1")


@pytest.fixture
def ssm(placebo_session):
    return placebo_session.client("ssm", region_name="eu-west-1")
