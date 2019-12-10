import logging
import os

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
    if not _plugin_exists(PLUGIN_INSTALL_PATH) and not _plugin_exists_in_path():
        raise OSError("{} not found".format(PLUGIN_NAME))

    return wrapped_function(*args, **kwargs)


def plugin_version(required_version):
    @decorator
    def wrapper(
        wrapped_function, instance, args, kwargs
    ):  # pylint: disable=unused-argument
        version = execute_plugin(["--version"], capture_output=True)
        logger.debug(
            "session-manager-plugin version: %s (required version: %s)",
            version,
            required_version,
        )

        if version and int(version.replace(".", "")) < int(
            required_version.replace(".", "")
        ):
            raise ValueError("Invalid plugin version: {}".format(version))

        return wrapped_function(*args, **kwargs)

    return wrapper


@decorator
def valid_aws_profile(
    wrapped_function, instance, args, kwargs
):  # pylint: disable=unused-argument
    if not is_existing_profile(kwargs["profile_name"]):
        raise ValueError("Invalid profile provided: {}".format(kwargs["profile_name"]))

    return wrapped_function(*args, **kwargs)


@decorator
def valid_aws_region(
    wrapped_function, instance, args, kwargs
):  # pylint: disable=unused-argument
    if not is_existing_region(kwargs["region_name"]):
        raise ValueError("Invalid region provided: {}".format(kwargs["region_name"]))

    return wrapped_function(*args, **kwargs)
