import contextlib
import logging
import signal

import boto3

logger = logging.getLogger(__name__)


def _create_aws_session(region_name=None, profile_name=None):
    logger.debug('Obtaining boto3 session object')
    kwargs = {}
    if region_name is not None:
        kwargs['region_name'] = region_name
    if profile_name is not None:
        kwargs['profile_name'] = profile_name
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
    session = _create_aws_session(region_name='eu-west-1')

    logger.debug('Obtained configured AWS profiles: %s', ' '.join(session.available_profiles))
    return profile_name in session.available_profiles


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
