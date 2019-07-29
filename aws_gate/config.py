import logging
import os

import yaml
from yaml.constructor import ConstructorError
from yaml.parser import ParserError
from marshmallow import Schema, fields, post_load, ValidationError, validates_schema

from aws_gate.utils import is_existing_profile, is_existing_region

DEFAULT_GATE_DIR = os.path.expanduser('~/.aws-gate')
DEFAULT_GATE_CONFIG_PATH = os.path.join(DEFAULT_GATE_DIR, 'config')
DEFAULT_GATE_CONFIGD_PATH = os.path.join(DEFAULT_GATE_DIR, 'config.d')

PLUGIN_NAME = 'session-manager-plugin'
DEFAULT_GATE_BIN_PATH = os.path.join(DEFAULT_GATE_DIR, 'bin')
PLUGIN_INSTALL_PATH = os.path.join(DEFAULT_GATE_BIN_PATH, PLUGIN_NAME)

logger = logging.getLogger(__name__)


class EmptyConfigurationError(Exception):
    pass


def _validate_unknown_fields(expected_fields, original_fields):
    unknown = set(original_fields) - set(expected_fields)
    if unknown:
        raise ValidationError('Unknown field', unknown)


def validate_profile(profile):
    if not is_existing_profile(profile):
        raise ValidationError('Invalid profile provided: {}'.format(profile))


def validate_region(region):
    if not is_existing_region(region):
        raise ValidationError('Invalid region name provided: {}'.format(region))


def validate_defaults(data):
    schema = DefaultsSchema(strict=True)
    schema.load(data)


class DefaultsSchema(Schema):
    profile = fields.String(required=False, validate=validate_profile)
    region = fields.String(required=False, validate=validate_region)

    # pylint: disable=unused-argument
    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        _validate_unknown_fields(self.fields, original_data)


class HostSchema(Schema):
    alias = fields.String(required=True)
    name = fields.String(required=True)
    profile = fields.String(required=True, validate=validate_profile)
    region = fields.String(required=True, validate=validate_region)

    # pylint: disable=unused-argument
    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        _validate_unknown_fields(self.fields, original_data)


class GateConfigSchema(Schema):
    defaults = fields.Dict(DefaultsSchema, required=False, missing=dict(), validate=validate_defaults)
    hosts = fields.List(fields.Nested(HostSchema), required=False, missing=list())

    # pylint: disable=unused-argument
    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        _validate_unknown_fields(self.fields, original_data)

    # pylint: disable=no-self-use
    @post_load
    def create_config(self, data):
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
        if 'region' in self._defaults:
            return self._defaults['region']
        return None

    @property
    def default_profile(self):
        if 'profile' in self._defaults:
            return self._defaults['profile']
        return None

    def get_host(self, name):
        host = [host for host in self._hosts if host['alias'] == name]
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
                logger.debug('Located config file: %s', file_path)
                config_files.append(file_path)

    if os.path.isfile(DEFAULT_GATE_CONFIG_PATH):
        logger.debug('Located config file: %s', DEFAULT_GATE_CONFIG_PATH)
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
            raise TypeError('Cannot merge {} with dict, src={} dst={}'.format(type(src).__name__, src, dst))

    elif isinstance(dst, list):
        if isinstance(src, list):
            dst.extend(src)
        else:
            dst.append(src)
    else:
        dst = src

    return dst


def load_config_from_files(config_files=None):
    if config_files is None:
        config_files = _locate_config_files()

    config_data, data = {}, {}
    if config_files:
        for path in config_files:
            try:
                with open(path, 'r') as config_file:
                    data = yaml.safe_load(config_file) or {}
            except (ConstructorError, ParserError):
                data = {}
            _merge_data(data, config_data)

        if not config_data:
            raise EmptyConfigurationError('Empty configuration data')

    config = GateConfigSchema(strict=True).load(config_data).data
    return config
