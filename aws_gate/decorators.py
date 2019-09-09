import os
import functools
import logging

from aws_gate.constants import PLUGIN_INSTALL_PATH
from aws_gate.utils import execute

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
            version = execute(PLUGIN_INSTALL_PATH, ['--version'], capture_output=True)
            logger.debug('session-manager-plugin version: %s (required version: %s)', version, required_version)

            if version and int(version.replace('.', '')) < int(required_version.replace('.', '')):
                raise ValueError('Invalid plugin version: {}'.format(version))

            result = wrapped_function(*args, **kwargs)
            return result
        return _wrapper
    return _outer_wrapper
