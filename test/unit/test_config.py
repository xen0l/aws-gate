import os
import unittest

from unittest.mock import patch
from marshmallow import ValidationError

from aws_gate.config import GateConfig, EmptyConfigurationError, load_config_from_files, _locate_config_files, \
    DEFAULT_GATE_CONFIG_PATH, DEFAULT_GATE_CONFIGD_PATH


class TestConfig(unittest.TestCase):
    def _load_config_files(self, config_files):
        config = load_config_from_files(config_files=config_files)
        self.assertIsInstance(config, GateConfig)
        return config

    def _locate_test_file(self):
        test_dir = os.path.dirname(__file__)
        test_name = self.id().split('.')[-1]
        test_path = os.path.join(test_dir, 'files', test_name)

        if os.path.isdir(test_path):
            test_files = [os.path.join(test_path, f) for f in sorted(os.listdir(test_path))]
        else:
            test_files = [test_path + '.yaml']
        return test_files

    def test_empty_config(self):
        with self.assertRaises(EmptyConfigurationError):
            self._load_config_files(config_files=self._locate_test_file())

    def test_invalid_config(self):
        with self.assertRaises(ValidationError):
            self._load_config_files(config_files=self._locate_test_file())

    def test_config_invalid_yaml(self):
        with self.assertRaises(EmptyConfigurationError):
            self._load_config_files(config_files=self._locate_test_file())

    def test_valid_config(self):
        expected_config = {
            'defaults': {
                'profile': 'default-profile',
                'region': 'eu-west-1'
            },
            'hosts': [
                {
                    'alias': 'foobar',
                    'name': 'foobar',
                    'profile': 'test-profile',
                    'region': 'eu-west-1'
                }
            ]
        }

        with patch('aws_gate.config.is_existing_profile', return_value=True):
            config = self._load_config_files(config_files=self._locate_test_file())

            self.assertEqual(config.defaults, expected_config['defaults'])
            self.assertEqual(config.hosts, expected_config['hosts'])
            self.assertEqual(config.default_profile, expected_config['defaults']['profile'])
            self.assertEqual(config.default_region, expected_config['defaults']['region'])

    def test_valid_config_without_hosts(self):
        expected_config = {
            'defaults': {
                'profile': 'default-profile',
                'region': 'eu-west-1'
            }
        }

        with patch('aws_gate.config.is_existing_profile', return_value=True):
            config = self._load_config_files(config_files=self._locate_test_file())

            self.assertEqual(config.defaults, expected_config['defaults'])
            self.assertEqual(config.hosts, [])
            self.assertEqual(config.default_profile, expected_config['defaults']['profile'])
            self.assertEqual(config.default_region, expected_config['defaults']['region'])

    def test_valid_config_without_defaults(self):
        with self.assertRaises(ValidationError):
            self._load_config_files(config_files=self._locate_test_file())

        with patch('aws_gate.config.is_existing_profile', return_value=True):
            config = self._load_config_files(config_files=self._locate_test_file())

            self.assertEqual(config.default_profile, None)
            self.assertEqual(config.default_region, None)

    def test_configd(self):
        expected_config = {
            'defaults': {
                'profile': 'default-profile',
                'region': 'eu-west-1'
            },
            'hosts': [
                {
                    'alias': 'bar',
                    'name': 'bar',
                    'profile': 'test-profile',
                    'region': 'eu-west-1'
                },
                {
                    'alias': 'foo',
                    'name': 'foo',
                    'profile': 'test-profile',
                    'region': 'eu-west-1'
                }
            ]
        }
        with patch('aws_gate.config.is_existing_profile', return_value=True):
            config = self._load_config_files(config_files=self._locate_test_file())

            self.assertEqual(config.defaults, expected_config['defaults'])
            self.assertEqual(config.hosts, expected_config['hosts'])

    def test_locate_config_files(self):
        with patch('aws_gate.config.os.path.isdir', return_value=True), \
                patch('aws_gate.config.os.listdir', return_value=['foo.yaml']), \
                patch('aws_gate.config.os.path.isfile', return_value=True):

            expected_config_files = [os.path.join(DEFAULT_GATE_CONFIGD_PATH, 'foo.yaml'), DEFAULT_GATE_CONFIG_PATH]
            self.assertEqual(_locate_config_files(), expected_config_files)

    def test_config_get_host(self):
        expected_host = {'alias': 'foobar', 'name': 'foobar', 'region': 'eu-west-1', 'profile': 'test-profile'}
        with patch('aws_gate.config.is_existing_profile', return_value=True):
            config = self._load_config_files(config_files=self._locate_test_file())

            self.assertEqual(config.get_host('foobar'), expected_host)
            self.assertEqual(config.get_host('non-existent'), {})
