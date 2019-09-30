import json
import logging

from aws_gate.constants import AWS_DEFAULT_PROFILE, AWS_DEFAULT_REGION, DEFAULT_OS_USER
from aws_gate.decorators import plugin_version, plugin_required, valid_aws_profile, valid_aws_region
from aws_gate.query import query_instance
from aws_gate.session_common import BaseSession
from aws_gate.ssh_common import SshKey
from aws_gate.utils import get_aws_client, get_aws_resource, execute_plugin, fetch_instance_details

logger = logging.getLogger(__name__)


class SshProxySession(BaseSession):
    def __init__(self, instance_id, ssm=None, region_name=AWS_DEFAULT_REGION, profile_name=AWS_DEFAULT_PROFILE,
                 port='22', user=DEFAULT_OS_USER):
        self._instance_id = instance_id
        self._region_name = region_name
        self._profile_name = profile_name is not None or ''
        self._ssm = ssm
        self._port = port
        self._user = user

        self._session_parameters = {
            'Target': self._instance_id,
            'DocumentName': 'AWS-StartSSHSession',
            'Parameters': {
                'portNumber': [str(self._port)]
            }
        }

    def open(self):
        execute_plugin([json.dumps(self._response),
                        self._region_name,
                        'StartSession',
                        self._profile_name,
                        json.dumps(self._session_parameters),
                        self._ssm.meta.endpoint_url])


@plugin_required
@plugin_version('1.1.23.0')
@valid_aws_profile
@valid_aws_region
def ssh_proxy(config, instance_name, user=DEFAULT_OS_USER, port=22, key_type='rsa', key_size=2048,
              profile_name=AWS_DEFAULT_PROFILE, region_name=AWS_DEFAULT_REGION):
    instance, profile, region = fetch_instance_details(config, instance_name, profile_name, region_name)

    ssm = get_aws_client('ssm', region_name=region, profile_name=profile)
    ec2 = get_aws_resource('ec2', region_name=region, profile_name=profile)

    instance_id = query_instance(name=instance, ec2=ec2)
    if instance_id is None:
        raise ValueError('No instance could be found for name: {}'.format(instance))

    logger.info('Opening SSH proxy session on instance %s (%s) via profile %s', instance_id, region_name, profile_name)
    with SshKey(key_type=key_type, key_size=key_size):
        with SshProxySession(instance_id, region_name=region_name, profile_name=profile, ssm=ssm, port=port,
                             user=user) as ssh_proxy_session:
            ssh_proxy_session.open()
