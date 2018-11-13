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

    try:
        ec2_instances = list(ec2.instances.filter(Filters=filters))
        logger.debug('Found %s maching instances', len(ec2_instances))
        for i in ec2_instances:
            if i.instance_id:
                logger.debug('Matching instance: %s', i.instance_id)
                ret = i.instance_id
    except botocore.exceptions.ClientError:
        raise AWSConnectionError

    return ret


def getinstanceidbyprivatednsname(name, ec2=None):
    filters = [{
        'Name': 'private-dns-name',
        'Values': [name]
    }]
    return _query_aws_api(filters=filters, ec2=ec2)


def getinstanceidbydnsname(name, ec2=None):
    filters = [{
        'Name': 'dns-name',
        'Values': [name]
    }]
    return _query_aws_api(filters=filters, ec2=ec2)


def getinstanceidbyprivateipaddress(name, ec2=None):
    filters = [{
        'Name': 'private-ip-address',
        'Values': [name]
    }]
    return _query_aws_api(filters=filters, ec2=ec2)


def getinstanceidbyipaddress(name, ec2=None):
    filters = [{
        'Name': 'ip-address',
        'Values': [name]
    }]
    return _query_aws_api(filters=filters, ec2=ec2)


def query_instance(name, ec2=None):

    if ec2 is None:
        raise ValueError('EC2 client is not initialized')

    logger.debug('Querying EC2 API for instance identifier: %s', name)

    identifier_type = None
    func_dispatcher = {
        'dns-name': getinstanceidbydnsname,
        'private-dns-name': getinstanceidbyprivatednsname,
        'ip-address': getinstanceidbyipaddress,
        'private-ip-address': getinstanceidbyprivateipaddress,
    }

    # If we are provided with instance ID directly, we don't need to contact EC2
    # API and can return the value directly.
    if name.startswith('id-') or name.startswith('i-'):
        return name

    if _is_valid_ip(name):
        if not ipaddress.ip_address(name).is_private:
            identifier_type = 'ip-address'
        else:
            identifier_type = 'private-ip-address'
    else:
        if name.endswith('compute.amazonaws.com'):
            identifier_type = 'dns-name'
        elif name.endswith('compute.internal'):
            identifier_type = 'private-dns-name'

    if identifier_type is None:
        raise ValueError('Unknown instance identifier: {}'.format(name))

    return func_dispatcher[identifier_type](name=name, ec2=ec2)
