import functools
import logging
import os

from aws_gate.constants import PLUGIN_INSTALL_PATH
from aws_gate.utils import execute_plugin, is_existing_profile, is_existing_region

logger = logging.getLogger(__name__)


def _plugin_exists(plugin_path):
    return os.path.exists(plugin_path)


def plugin_required(wrapped_function):
    @functools.wraps(wrapped_function)
    def _wrapper(*args, **kwargs):
        if not _plugin_exists(PLUGIN_INSTALL_PATH):
            raise OSError('session-manager-plugin not found')

        result = wrapped_function(*args, **kwargs)
        return result

    return _wrapper


def plugin_version(required_version):
    def _outer_wrapper(wrapped_function):
        @functools.wraps(wrapped_function)
        def _wrapper(*args, **kwargs):
            version = execute_plugin(['--version'], capture_output=True)
            logger.debug('session-manager-plugin version: %s (required version: %s)', version, required_version)

            if version and int(version.replace('.', '')) < int(required_version.replace('.', '')):
                raise ValueError('Invalid plugin version: {}'.format(version))

            result = wrapped_function(*args, **kwargs)
            return result

        return _wrapper

    return _outer_wrapper


def valid_aws_profile(wrapped_function):
    @functools.wraps(wrapped_function)
    def _wrapper(**kwargs):
        if not is_existing_profile(kwargs['profile_name']):
            raise ValueError('Invalid profile provided: {}'.format(kwargs['profile_name']))

        result = wrapped_function(**kwargs)
        return result

    return _wrapper


def valid_aws_region(wrapped_function):
    @functools.wraps(wrapped_function)
    def _wrapper(**kwargs):
        if not is_existing_region(kwargs['region_name']):
            raise ValueError('Invalid region provided: {}'.format(kwargs['region_name']))

        result = wrapped_function(**kwargs)
        return result

    return _wrapper
