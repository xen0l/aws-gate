import ipaddress
import logging

import botocore.exceptions

from aws_gate.exceptions import AWSConnectionError

logger = logging.getLogger(__name__)


def _is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return False
    return True


def _query_aws_api(filters, ec2=None):
    ret = None

    # We are always interested only in running EC2 instances as we cannot
    # open a session to terminated EC2 instance.
    filters = filters + [{"Name": "instance-state-name", "Values": ["running"]}]

    try:
        ec2_instances = list(ec2.instances.filter(Filters=filters))
        logger.debug("Found %s maching instances", len(ec2_instances))
        for i in ec2_instances:
            if i.instance_id:
                logger.debug("Matching instance: %s", i.instance_id)
                ret = i.instance_id
    except botocore.exceptions.ClientError as e:
        raise AWSConnectionError(e)

    return ret


def getinstanceidbyprivatednsname(name, ec2=None):
    filters = [{"Name": "private-dns-name", "Values": [name]}]
    return _query_aws_api(filters=filters, ec2=ec2)


def getinstanceidbydnsname(name, ec2=None):
    filters = [{"Name": "dns-name", "Values": [name]}]
    return _query_aws_api(filters=filters, ec2=ec2)


def getinstanceidbyprivateipaddress(name, ec2=None):
    filters = [{"Name": "private-ip-address", "Values": [name]}]
    return _query_aws_api(filters=filters, ec2=ec2)


def getinstanceidbyipaddress(name, ec2=None):
    filters = [{"Name": "ip-address", "Values": [name]}]
    return _query_aws_api(filters=filters, ec2=ec2)


def getinstanceidbytag(name, ec2=None):
    # One of the allowed characters in tags is ":", which might break tag
    # parsing. For this reason,we have to differentiate 2 cases for
    # provided name:
    # - aws: special prefixed tags in the form of aws:<service>:<tag_name>:<tag_value>
    # - regular cases in the form <tag_name>:<tag_value>
    if name.startswith("aws:"):
        key, value = ":".join(name.split(":", 3)[:3]), name.split(":", 3)[-1]
    else:
        key, value = name.split(":", 1)

    filters = [{"Name": f"tag:{key}", "Values": [value]}]
    return _query_aws_api(filters=filters, ec2=ec2)


def getinstanceidbyinstancename(name, ec2=None):
    return getinstanceidbytag(f"Name:{name}", ec2=ec2)


def getinstanceidbyautoscalinggroup(name, ec2=None):
    _, asg_name = name.split(":")
    return getinstanceidbytag(f"aws:autoscaling:groupName:{asg_name}", ec2=ec2)


def query_instance(name, ec2=None):
    if ec2 is None:
        raise ValueError("EC2 client is not initialized")

    logger.debug("Querying EC2 API for instance identifier: %s", name)

    identifier_type = None
    func_dispatcher = {
        "dns-name": getinstanceidbydnsname,
        "private-dns-name": getinstanceidbyprivatednsname,
        "ip-address": getinstanceidbyipaddress,
        "private-ip-address": getinstanceidbyprivateipaddress,
        "tag": getinstanceidbytag,
        "name": getinstanceidbyinstancename,
        "asg": getinstanceidbyautoscalinggroup,
    }

    # If we are provided with instance ID directly, we don't need to contact EC2
    # API and can return the value directly.
    # Identifier prefixes:
    # id - human friendly, present in some systems
    # i - regular EC2 instance ID as present in AWS console/logs
    # mi - regular SSM-managed instance ID as present in AWS console/logs
    if name.startswith("id-") or name.startswith("i-") or name.startswith("mi-"):
        return name

    if _is_valid_ip(name):
        if not ipaddress.ip_address(name).is_private:
            identifier_type = "ip-address"
        else:
            identifier_type = "private-ip-address"
    else:
        if name.endswith("compute.amazonaws.com"):
            identifier_type = "dns-name"
        elif name.endswith("compute.internal"):
            identifier_type = "private-dns-name"
        elif name.startswith("asg:"):
            identifier_type = "asg"
        elif ":" in name:
            identifier_type = "tag"
        else:
            identifier_type = "name"

    logger.debug("Identifier type chosen: %s", identifier_type)
    return func_dispatcher[identifier_type](name=name, ec2=ec2)
