import json
import pytest

from aws_gate.list import list_instances, serialize


def test_list(mocker, ec2, ssm, capsys):
    mocker.patch("aws_gate.list.get_aws_resource", return_value=ec2)
    mocker.patch("aws_gate.list.get_aws_client", return_value=ssm)
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    expected_data = [
        "i-0c32153096cd68a6d",
        "dummy-instance",
        "eu-west-1a",
        "vpc-1981f29759da4a354",
        "10.69.104.49\n",
    ]
    expected = " ".join(expected_data)

    list_instances(profile_name="default", region_name="eu-west-1")
    out, _ = capsys.readouterr()

    assert out == expected


def test_list_invalid_profile():
    with pytest.raises(ValueError):
        list_instances(profile_name="invalid-profile", region_name="eu-west-1")


def test_list_invalid_region(mocker):
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    with pytest.raises(ValueError):
        list_instances(profile_name="default", region_name="invalid-region")


def test_list_invalid_field(mocker):
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    with pytest.raises(ValueError):
        list_instances(
            profile_name="default", region_name="eu-west-1", fields=["invalid-field"]
        )


@pytest.mark.parametrize(
    "output_format, fields, data, expected",
    [
        (
            "json",
            ["foo"],
            [{"foo": "bar"}],
            json.dumps([{"foo": "bar"}], sort_keys=True, indent=4),
        ),
        (
            "json",
            ["foo", "bar"],
            [{"foo": "bar", "bar": "foo"}],
            json.dumps([{"foo": "bar", "bar": "foo"}], sort_keys=True, indent=4),
        ),
        ("human", ["foo"], [{"foo": "bar"}], "bar\r\n"),
        ("human", ["foo", "bar"], [{"foo": "bar", "bar": "foo"}], "bar foo\r\n"),
        ("tsv", ["foo"], [{"foo": "bar"}], "bar\r\n"),
        ("tsv", ["foo", "bar"], [{"foo": "bar", "bar": "foo"}], "bar\tfoo\r\n"),
        ("csv", ["foo"], [{"foo": "bar"}], "bar\r\n"),
        ("csv", ["foo", "bar"], [{"foo": "bar", "bar": "foo"}], "bar,foo\r\n"),
    ],
    ids=[
        "{}-{}".format(type_, number)
        for type_ in ["json", "human", "tsv", "csv"]
        for number in ["single", "many"]
    ],
)
def test_serializer(output_format, fields, data, expected):
    assert serialize(data=data, output_format=output_format, fields=fields) == expected
