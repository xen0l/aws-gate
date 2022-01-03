import csv
import io
import json
import logging

from aws_gate.constants import (
    AWS_DEFAULT_PROFILE,
    AWS_DEFAULT_REGION,
    DEFAULT_LIST_OUTPUT_FIELDS,
    DEFAULT_LIST_HUMAN_FIELDS,
    DEFAULT_LIST_OUTPUT,
)
from aws_gate.decorators import valid_aws_region, valid_aws_profile
from aws_gate.utils import (
    get_aws_client,
    get_aws_resource,
    get_multiple_instance_details,
)

logger = logging.getLogger(__name__)


# pylint: disable=unused-argument
def _serialize_json(data, fields=None):
    return json.dumps(data, indent=4, sort_keys=True)


def _serialize_csv(data, delimiter=",", fields=DEFAULT_LIST_OUTPUT_FIELDS):
    output = io.StringIO()
    writer = csv.DictWriter(output, delimiter=delimiter, fieldnames=fields)
    writer.writerows(data)

    return output.getvalue()


def _serialize_tsv(data, fields=DEFAULT_LIST_OUTPUT_FIELDS):
    return _serialize_csv(data, delimiter="\t", fields=fields)


def _serialize_human(data, fields=DEFAULT_LIST_HUMAN_FIELDS):
    return _serialize_csv(data, delimiter=" ", fields=fields)


def serialize(
    data, output_format=DEFAULT_LIST_OUTPUT, fields=DEFAULT_LIST_OUTPUT_FIELDS
):
    format_dispatcher = {
        "csv": _serialize_csv,
        "tsv": _serialize_tsv,
        "human": _serialize_human,
        "json": _serialize_json,
    }

    filtered_data = []
    for item in data:
        filtered_data_item = {}
        for field in fields:
            if field in item.keys():
                filtered_data_item[field] = item[field]
        filtered_data.append(filtered_data_item)

    return format_dispatcher[output_format](filtered_data, fields=fields)


@valid_aws_profile
@valid_aws_region
def list_instances(
    profile_name=AWS_DEFAULT_PROFILE,
    region_name=AWS_DEFAULT_REGION,
    output_format=DEFAULT_LIST_OUTPUT,
    fields=DEFAULT_LIST_HUMAN_FIELDS,
):
    invalid_fields = list(set(fields) - set(DEFAULT_LIST_OUTPUT_FIELDS))
    if invalid_fields:
        invalid_fields_str = " ".join(invalid_fields)
        default_fields_str = " ".join(DEFAULT_LIST_OUTPUT_FIELDS)

        raise ValueError(
            f'Invalid fields provided: "{invalid_fields_str}". Valid fields: "{default_fields_str}"'  # noqa: B950
        )

    ssm = get_aws_client("ssm", region_name=region_name, profile_name=profile_name)
    ec2 = get_aws_resource("ec2", region_name=region_name, profile_name=profile_name)

    instances_ssm_paginator = ssm.get_paginator("describe_instance_information")
    instances_ssm_response_iterator = instances_ssm_paginator.paginate()

    instance_ids = []
    for response in instances_ssm_response_iterator:
        for instance in response["InstanceInformationList"]:
            instance_ids.append(instance["InstanceId"])

    instance_details = get_multiple_instance_details(instance_ids=instance_ids, ec2=ec2)
    print(
        serialize(instance_details, output_format=output_format, fields=fields).rstrip()
    )
