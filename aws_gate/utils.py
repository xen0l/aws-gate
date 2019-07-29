import os
import contextlib
import logging
import signal
import subprocess

import boto3


logger = logging.getLogger(__name__)

# This list is maintained by hand as new regions are not added that often. This should be removed once, we find a
# better way how to obtain region list without the need to contact AWS EC2 API
AWS_REGIONS = ['ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2',
               'ca-central-1', 'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3',
               'sa-east-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']


def _create_aws_session(region_name=None, profile_name=None):
    logger.debug('Obtaining boto3 session object')
    kwargs = {}
    if region_name is not None:
        kwargs['region_name'] = region_name
    if profile_name is not None:
        kwargs['profile_name'] = profile_name

    # https://github.com/boto/boto3/issues/598
    if 'AWS_ACCESS_KEY_ID' in os.environ:
        kwargs['aws_access_key_id'] = os.environ['AWS_ACCESS_KEY_ID']
    if 'AWS_SECRET_ACCESS_KEY' in os.environ:
        kwargs['aws_secret_access_key'] = os.environ['AWS_SECRET_ACCESS_KEY']
    if 'AWS_SESSION_TOKEN' in os.environ:
        kwargs['aws_session_token'] = os.environ['AWS_SESSION_TOKEN']

    session = boto3.session.Session(**kwargs)

    return session


def get_aws_client(service_name, region_name, profile_name=None):
    session = _create_aws_session(region_name=region_name, profile_name=profile_name)

    logger.debug('Obtaining %s client', service_name)
    return session.client(service_name=service_name)


def get_aws_resource(service_name, region_name, profile_name=None):
    session = _create_aws_session(region_name=region_name, profile_name=profile_name)

    logger.debug('Obtaining %s boto3 resource', service_name)
    return session.resource(service_name=service_name)


def is_existing_profile(profile_name):
    session = _create_aws_session()

    logger.debug('Obtained configured AWS profiles: %s', ' '.join(session.available_profiles))
    return profile_name in session.available_profiles


def is_existing_region(region_name):
    return region_name in AWS_REGIONS


def get_default_region():
    session = _create_aws_session()

    return session.region_name


@contextlib.contextmanager
def deferred_signals(signal_list=None):
    if signal_list is None:
        signal_list = [signal.SIGHUP, signal.SIGINT, signal.SIGTERM]

    for deferred_signal in signal_list:
        signal_name = signal.Signals(deferred_signal).name
        logger.debug('Deferring signal: %s', signal_name)
        signal.signal(deferred_signal, signal.SIG_IGN)

    try:
        yield
    finally:
        for deferred_signal in signal_list:
            signal_name = signal.Signals(deferred_signal).name
            logger.debug('Restoring signal: %s', signal_name)
            signal.signal(deferred_signal, signal.SIG_DFL)


def execute(path, args, capture_output=True):
    ret = None
    try:
        logger.debug('Executing "%s"', ' '.join([path] + args))
        result = subprocess.run([path] + args, capture_output=capture_output)
    except subprocess.CalledProcessError as e:
        logger.error('Command "%s" exited with %s', ' '.join([path] + args), e.returncode)

    if result.stdout:
        ret = result.stdout.decode()
        ret = ret.rstrip()

    return ret
