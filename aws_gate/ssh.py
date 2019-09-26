import logging
import json

from aws_gate.constants import PLUGIN_INSTALL_PATH, DEBUG
from aws_gate.ssh_common import GateKey
from aws_gate.query import query_instance
from aws_gate.decorators import plugin_version, plugin_required
from aws_gate.utils import get_aws_client, get_aws_resource, is_existing_profile, is_existing_region, execute
from aws_gate.session_common import BaseSession

logger = logging.getLogger(__name__)


class SSHSession(BaseSession):
    def __init__(self, instance_id, region_name='eu-west-1', profile_name='default', ssm=None, ssh_key=None, port='22',
                 user='ec2-user'):
        self._instance_id = instance_id
        self._region_name = region_name
        self._profile_name = profile_name
        self._ssm = ssm
        self._ssh_key = ssh_key
        self._port = port
        self._user = user

        self._parameters = {
            'Target': self._instance_id,
            'DocumentName': 'AWS-StartSSHSession',
            'Parameters': {
                'portNumber': [str(self._port)]
            }
        }
        self._ssh_cmd = None

    def _build_ssh_command(self):

        import shlex

        def quote_args(args):
            return [shlex.quote(arg) for arg in args]

        cmd = ['ssh', '-l', self._user, '-p', str(self._port), '-F', '/dev/null']

        if DEBUG:
            cmd.append('-vv')
        else:
            cmd.append('-q')

        import shlex
        cmd.append('-o')
        args = ' '.join([shlex.quote(json.dumps(self._response)),
                         self._region_name, 'StartSession', self._profile_name,
                         shlex.quote(json.dumps(self._parameters)), self._ssm.meta.endpoint_url])
        cmd.append('ProxyCommand="{} {}"'.format(PLUGIN_INSTALL_PATH, args))
        cmd.append(self._instance_id)

        return cmd

    def open(self):
        self._ssh_cmd = self._build_ssh_command()

        execute(self._ssh_cmd[0], self._ssh_cmd[1:])

    @property
    def ssh_cmd(self):
        return self._ssh_cmd


@plugin_required
@plugin_version('1.1.23.0')
def ssh(config, instance_name, user='ec2-user', port=22, key_type='rsa', key_size=2048,
        profile_name='default', region_name='eu-west-1'):
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

    logger.info('Opening SSH session on instance %s (%s) via profile %s', instance_id, region_name, profile_name)
    with GateKey(key_type=key_type, key_size=key_size) as ssh_key:
        with SSHSession(instance_id=instance_name, profile_name=profile, user=user, port=port, ssm=ssm,
                        ssh_key=ssh_key) as ssh_session:
            ssh_session.open()
