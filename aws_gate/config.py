import logging
import os

import yaml
from yaml.constructor import ConstructorError
from marshmallow import Schema, fields, post_load, ValidationError, validates_schema

from aws_gate.utils import is_existing_profile, is_existing_region

DEFAULT_GATE_DIR = os.path.expanduser('~/.aws-gate')
DEFAULT_GATE_CONFIG_PATH = os.path.join(DEFAULT_GATE_DIR, 'config')
DEFAULT_GATE_CONFIGD_PATH = os.path.join(DEFAULT_GATE_DIR, 'config.d')

logger = logging.getLogger(__name__)


class EmptyConfigurationeError(Exception):
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
    profile = fields.String(required=True, validate=validate_profile)
    region = fields.String(required=True, validate=validate_region)

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        _validate_unknown_fields(self.fields, original_data)


class HostSchema(Schema):
    name = fields.String(required=True)
    profile = fields.String(required=True, validate=validate_profile)
    region = fields.String(required=True, validate=validate_region)

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        _validate_unknown_fields(self.fields, original_data)


class GateConfigSchema(Schema):
    defaults = fields.Dict(DefaultsSchema, required=False, missing=dict(), validate=validate_defaults)
    hosts = fields.List(fields.Nested(HostSchema), required=False, missing=list())

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        _validate_unknown_fields(self.fields, original_data)

    @post_load
    def create_config(self, data):
        return GateConfig(**data)


class GateConfig(object):
    def __init__(self, defaults, hosts):
        self._defaults = defaults
        self._hosts = hosts

    @property
    def hosts(self):
        return self._hosts

    @property
    def defaults(self):
        return self._defaults


def _locate_config_files():
    config_files = []

    if os.path.isdir(DEFAULT_GATE_CONFIGD_PATH):
        configd_files = sorted(os.listdir(DEFAULT_GATE_CONFIGD_PATH))
        for f in configd_files:
            file_path = os.path.join(DEFAULT_GATE_CONFIGD_PATH, f)
            if os.path.isfile(file_path):
                config_files.append(file_path)

    if os.path.isfile(DEFAULT_GATE_CONFIG_PATH):
        config_files.append(DEFAULT_GATE_CONFIG_PATH)

    return config_files


def load_config_from_files(config_files=None):
    if config_files is None:
        config_files = _locate_config_files()

    data = {}
    if config_files:
        for path in config_files:
            try:
                with open(path) as config_file:
                    data = yaml.safe_load(config_file) or {}
            except ConstructorError:
                data = {}

#    if not config_data:
#        raise EmptyConfigurationeError('empty configuration data')

    config = GateConfigSchema(strict=True).load(data).data
    return config
