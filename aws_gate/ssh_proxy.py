import json
import logging

from aws_gate.decorators import plugin_version, plugin_required
from aws_gate.session_common import BaseSession
from aws_gate.query import query_instance
from aws_gate.utils import get_aws_client, get_aws_resource, is_existing_profile, is_existing_region, \
    execute_plugin

logger = logging.getLogger(__name__)


class SSHProxySession(BaseSession):
    def __init__(self, instance_id, region_name='eu-west-1', profile_name='default', ssm=None, port='22',
                 user='ec2-user'):
        self._instance_id = instance_id
        self._region_name = region_name
        self._profile_name = profile_name
        self._ssm = ssm
        self._port = port
        self._user = user

        self._parameters = {
            'Target': self._instance_id,
            'DocumentName': 'AWS-StartSSHSession',
            'Parameters': {
                'portNumber': [str(self._port)]
            }
        }

    def open(self):
        execute_plugin([json.dumps(self._response), self._region_name, 'StartSession', self._profile_name,
                        json.dumps(self._parameters), self._ssm.meta.endpoint_url])


@plugin_required
@plugin_version('1.1.23.0')
def ssh_proxy(config, instance_name, profile_name='default', region_name='eu-west-1'):
    if not is_existing_profile(profile_name):
        raise ValueError('Invalid profile provided: {}'.format(profile_name))

    if not is_existing_region(region_name):
        raise ValueError('Invalid region provided: {}'.format(profile_name))

    config_data = config.get_host(instance_name)
    if config_data and config_data['name'] and config_data['profile'] and config_data['region']:
        region = config_data['region']
        profile = config_data['profile']
        instance = config_data['name']
    else:
        region = region_name
        profile = profile_name
        instance = instance_name

    ssm = get_aws_client('ssm', region_name=region, profile_name=profile)
    ec2 = get_aws_resource('ec2', region_name=region, profile_name=profile)

    instance_id = query_instance(name=instance, ec2=ec2)
    if instance_id is None:
        raise ValueError('No instance could be found for name: {}'.format(instance))

    logger.info('Opening session on instance %s (%s) via profile %s', instance_id, region_name, profile_name)
    with SSHProxySession(instance_id, region_name=region_name, profile_name=profile, ssm=ssm) as sess:
        sess.open()
