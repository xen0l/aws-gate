import logging

from aws_gate.utils import get_aws_client, get_aws_resource

logger = logging.getLogger(__name__)


def list_instances(profile_name=None, region_name='eu-west-1'):
    ssm = get_aws_client('ssm', region_name=region_name, profile_name=profile_name)
    ec2 = get_aws_resource('ec2', region_name=region_name, profile_name=profile_name)

    instances_ssm_paginator = ssm.get_paginator('describe_instance_information')
    instances_ssm_response_iterator = instances_ssm_paginator.paginate()

    instance_ids = []
    for response in instances_ssm_response_iterator:
        for instance in response['InstanceInformationList']:
            instance_ids.append(instance['InstanceId'])

    for instance in ec2.instances.filter(InstanceIds=instance_ids):
        instance_name = ""
        for tags in instance.tags:
            if tags["Key"] == 'Name':
                instance_name = tags["Value"]
        print("{} - {}".format(instance.instance_id, instance_name))
