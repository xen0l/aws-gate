import pytest

from aws_gate.list import list_instances


def test_list(mocker, ec2, ssm, capsys):
    mocker.patch("aws_gate.list.get_aws_resource", return_value=ec2)
    mocker.patch("aws_gate.list.get_aws_client", return_value=ssm)
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    list_instances(profile_name="default", region_name="eu-west-1")

    out, _ = capsys.readouterr()

    assert out == "i-0c32153096cd68a6d - dummy-instance\n"


def test_list_invalid_profile():
    with pytest.raises(ValueError):
        list_instances(profile_name="invalid-profile", region_name="eu-west-1")


def test_list_invalid_region(mocker):
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    with pytest.raises(ValueError):
        list_instances(profile_name="default", region_name="invalid-region")
