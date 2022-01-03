import logging
import os

import yaml
from marshmallow import Schema, fields, post_load, ValidationError
from yaml.constructor import ConstructorError
from yaml.parser import ParserError

from aws_gate.constants import DEFAULT_GATE_CONFIG_PATH, DEFAULT_GATE_CONFIGD_PATH
from aws_gate.utils import is_existing_profile, is_existing_region

logger = logging.getLogger(__name__)


class EmptyConfigurationError(Exception):
    pass


def validate_profile(profile):
    if not is_existing_profile(profile):
        raise ValidationError(f"Invalid profile provided: {profile}")


def validate_region(region):
    if not is_existing_region(region):
        raise ValidationError(f"Invalid region name provided: {region}")


def validate_defaults(data):
    schema = DefaultsSchema()
    schema.load(data)


class DefaultsSchema(Schema):
    profile = fields.String(required=False, validate=validate_profile)
    region = fields.String(required=False, validate=validate_region)


class HostSchema(Schema):
    alias = fields.String(required=True)
    name = fields.String(required=True)
    profile = fields.String(required=True, validate=validate_profile)
    region = fields.String(required=True, validate=validate_region)


class GateConfigSchema(Schema):
    defaults = fields.Nested(
        DefaultsSchema, required=False, missing={}, validate=validate_defaults
    )
    hosts = fields.List(fields.Nested(HostSchema), required=False, missing=[])

    # pylint: disable=no-self-use,unused-argument
    @post_load
    def create_config(self, data, **kwargs):
        return GateConfig(**data)


class GateConfig:
    def __init__(self, defaults, hosts):
        self._defaults = defaults
        self._hosts = hosts

    @property
    def hosts(self):
        return self._hosts

    @property
    def defaults(self):
        return self._defaults

    @property
    def default_region(self):
        if "region" in self._defaults:
            return self._defaults["region"]
        return None

    @property
    def default_profile(self):
        if "profile" in self._defaults:
            return self._defaults["profile"]
        return None

    def get_host(self, name):
        host = [host for host in self._hosts if host["alias"] == name]
        if host:
            return host[0]
        return {}


def _locate_config_files():
    config_files = []

    if os.path.isdir(DEFAULT_GATE_CONFIGD_PATH):
        configd_files = sorted(os.listdir(DEFAULT_GATE_CONFIGD_PATH))
        for f in configd_files:
            file_path = os.path.join(DEFAULT_GATE_CONFIGD_PATH, f)
            if os.path.isfile(file_path):
                logger.debug("Located config file: %s", file_path)
                config_files.append(file_path)

    if os.path.isfile(DEFAULT_GATE_CONFIG_PATH):
        logger.debug("Located config file: %s", DEFAULT_GATE_CONFIG_PATH)
        config_files.append(DEFAULT_GATE_CONFIG_PATH)

    return config_files


def _merge_data(src, dst):
    if isinstance(dst, dict):
        if isinstance(src, dict):
            for key in src:
                if key in dst:
                    dst[key] = _merge_data(src[key], dst[key])
                else:
                    dst[key] = src[key]
        else:
            raise TypeError(
                f"Cannot merge {type(src).__name__} with dict, src={src} dst={dst}"
            )

    elif isinstance(dst, list):
        if isinstance(src, list):
            dst.extend(src)
        else:
            dst.append(src)
    else:
        dst = src

    return dst


def _merge_defaults(config_data):
    for host in config_data.get("hosts", []):
        for key, value in config_data.get("defaults", {}).items():
            if key not in host:
                host[key] = value


def load_config_from_files(config_files=None):
    if config_files is None:
        config_files = _locate_config_files()

    config_data, data = {}, {}
    if config_files:
        for path in config_files:
            try:
                with open(path, "r") as config_file:
                    data = yaml.safe_load(config_file) or {}
            except (ConstructorError, ParserError):
                data = {}
            _merge_data(data, config_data)

        if not config_data:
            raise EmptyConfigurationError("Empty configuration data")

    _merge_defaults(config_data)
    config = GateConfigSchema().load(config_data)
    return config
