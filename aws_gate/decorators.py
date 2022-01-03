import platform
import logging
import os
from subprocess import PIPE

from packaging.version import parse as parse_version
from wrapt import decorator

from aws_gate.constants import PLUGIN_INSTALL_PATH, PLUGIN_NAME
from aws_gate.utils import execute_plugin, is_existing_profile, is_existing_region

logger = logging.getLogger(__name__)


def _plugin_exists(plugin_path):
    return os.path.exists(plugin_path)


def _plugin_exists_in_path():
    return any(
        _plugin_exists(os.path.join(path, PLUGIN_NAME))
        for path in os.environ["PATH"].split(os.path.pathsep)
    )


@decorator
def plugin_required(
    wrapped_function, instance, args, kwargs
):  # pylint: disable=unused-argument
    if (
        not _plugin_exists(PLUGIN_INSTALL_PATH)
        and not _plugin_exists_in_path()
        and not platform.system() == "Windows"
    ):
        raise OSError(f"{PLUGIN_NAME} not found")

    return wrapped_function(*args, **kwargs)


def plugin_version(required_version):
    @decorator
    def wrapper(
        wrapped_function, instance, args, kwargs
    ):  # pylint: disable=unused-argument
        version = execute_plugin(["--version"], stdout=PIPE, stderr=PIPE)
        logger.debug(
            "session-manager-plugin version: %s (required version: %s)",
            version,
            required_version,
        )

        if version and parse_version(version) < parse_version(required_version):
            raise ValueError(f"Invalid plugin version: {version}")

        return wrapped_function(*args, **kwargs)

    return wrapper


@decorator
def valid_aws_profile(
    wrapped_function, instance, args, kwargs
):  # pylint: disable=unused-argument
    if not is_existing_profile(kwargs["profile_name"]):
        raise ValueError(f"Invalid profile provided: {kwargs['profile_name']}")

    return wrapped_function(*args, **kwargs)


@decorator
def valid_aws_region(
    wrapped_function, instance, args, kwargs
):  # pylint: disable=unused-argument
    if not is_existing_region(kwargs["region_name"]):
        raise ValueError(f"Invalid region provided: {kwargs['region_name']}")

    return wrapped_function(*args, **kwargs)
