import os
import functools

from aws_gate.utils import execute
from aws_gate.config import PLUGIN_INSTALL_PATH


def plugin_required(wrapped_function):
    @functools.wraps(wrapped_function)
    def _wrapper(*args, **kwargs):
        if not os.path.exists(PLUGIN_INSTALL_PATH):
            raise ValueError('session-manager-plugin not found')

        result = wrapped_function(*args, **kwargs)
        return result
    return _wrapper


def plugin_version(required_version):
    def _outer_wrapper(wrapped_function):
        @functools.wraps(wrapped_function)
        def _wrapper(*args, **kwargs):
            version = execute(PLUGIN_INSTALL_PATH, ['--version'])

            if version and int(version.replace('.', '')) < int(required_version.replace('.', '')):
                raise ValueError('Invalid plugin version: {}'.format(version))

            result = wrapped_function(*args, **kwargs)
            return result
        return _wrapper
    return _outer_wrapper
