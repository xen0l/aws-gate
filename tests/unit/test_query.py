import pytest
from botocore.exceptions import ClientError

from aws_gate.query import _query_aws_api, query_instance, AWSConnectionError


def test_query_aws_api_exception(mocker):
    ec2_mock = mocker.MagicMock()

    # https://github.com/surbas/pg2kinesis/blob/master/tests/test_stream.py#L20
    error_response = {"Error": {"Code": "ResourceInUseException"}}
    ec2_mock.configure_mock(
        **{"instances.filter.side_effect": ClientError(error_response, "random_ec2_op")}
    )

    filters = [{"Name": "ip-address", "Values": ["10.1.1.1"]}]
    with pytest.raises(AWSConnectionError):
        _query_aws_api(filters=filters, ec2=ec2_mock)


@pytest.mark.parametrize(
    "name",
    [
        "10.69.104.49",
        "ec2-18-202-215-108.eu-west-1.compute.amazonaws.com",
        "ip-10-69-104-49.eu-west-1.compute.internal",
        "18.202.215.108",
        "i-0c32153096cd68a6d",
        "Name:dummy-instance",
        "aws:autoscaling:groupName:dummy-v001",
        "dummy-instance",
        "asg:dummy-v001",
    ],
    ids=[
        "private_ip_address",
        "dns_name",
        "private_dns_name",
        "ip_address",
        "id",
        "tag",
        "tag (multiple colons)",
        "name",
        "asg",
    ],
)
def test_query_instance(name, instance_id, ec2):
    assert query_instance(name, ec2=ec2) == instance_id


@pytest.mark.parametrize(
    "name, expected",
    [
        ("dummy-instance", "tag:Name"),
        ("Name:dummy:instance", "tag:Name"),
        ("asg:dummy-v001", "tag:aws:autoscaling:groupName"),
        ("aws:autoscaling:groupName:dummy-v001", "tag:aws:autoscaling:groupName"),
    ],
    ids=["name", "name (colon with identifier)", "asg", "aws:autoscaling:groupName"],
)
def test_query_instance_by_tag_parsing(mocker, name, expected, ec2):
    mock = mocker.patch("aws_gate.query._query_aws_api")

    query_instance(name, ec2=ec2)

    assert mock.called
    assert mock.call_args[1]["filters"][0]["Name"] == expected


def test_query_instance_ec2_unitialized():
    with pytest.raises(ValueError):
        query_instance("18.205.215.108")
