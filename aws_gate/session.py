import errno
import json
import logging
import subprocess

from aws_gate.query import query_instance
from aws_gate.decorators import plugin_version, plugin_required
from aws_gate.utils import get_aws_client, get_aws_resource, deferred_signals, is_existing_profile, is_existing_region

logger = logging.getLogger(__name__)


class Session:
    def __init__(self, instance_id, region_name='eu-west-1', ssm=None):
        self._instance_id = instance_id
        self._region_name = region_name
        self._ssm = ssm

        self._response = None
        self._session_id = None
        self._token_value = None

    def __enter__(self):
        # create and establish session
        self.create()
        return self

    def __exit__(self, *args):
        # terminate session
        self.terminate()

    def create(self):
        logger.debug('Creating a new session on instance: %s (%s)', self._instance_id, self._region_name)
        self._response = self._ssm.start_session(Target=self._instance_id)
        logger.debug('Received response: %s', self._response)

        self._session_id, self._token_value = self._response['SessionId'], self._response['TokenValue']

    def terminate(self):
        logger.debug('Terminating session: %s', self._session_id)
        response = self._ssm.terminate_session(SessionId=self._session_id)
        logger.debug('Received response: %s', response)

    def open(self):
        with deferred_signals():
            try:
                logger.debug('Executing session-manager-plugin')
                subprocess.check_call(['session-manager-plugin',
                                       json.dumps(self._response),
                                       self._region_name,
                                       'StartSession'])
                logger.debug('session-manager plugin finished successfully')
            except OSError as ex:
                if ex.errno == errno.ENOENT:
                    raise ValueError('session-manager-plugin cannot be found')


@plugin_required
@plugin_version('1.1.23.0')
def session(config, instance_name, profile_name='default', region_name='eu-west-1'):
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
    with Session(instance_id, region_name=region_name, ssm=ssm) as sess:
        sess.open()
