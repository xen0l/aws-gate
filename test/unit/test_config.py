import os
import unittest

from unittest.mock import patch
from marshmallow import ValidationError

from aws_gate.config import GateConfig, EmptyConfigurationeError, load_config_from_files


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
            test_files = [test_path + '.yml']
        return test_files

    def test_empty_config(self):
        with self.assertRaises(EmptyConfigurationeError):
            self._load_config_files([])

    def test_invalid_config(self):
        with self.assertRaises(ValidationError):
            self._load_config_files(config_files=self._locate_test_file())

    def test_config_invalid_yaml(self):
        with self.assertRaises(EmptyConfigurationeError):
            self._load_config_files(config_files=self._locate_test_file())

    def test_valid_config(self):
        expected_config = {
            'defaults': {
                'profile': 'default-profile',
                'region': 'eu-west-1'
            },
            'hosts': [
                {
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

    def test_valid_config_without_defaults(self):
        with self.assertRaises(ValidationError):
            self._load_config_files(config_files=self._locate_test_file())

    def test_configd(self):
        expected_config = {
            'defaults': {
                'profile': 'default-profile',
                'region': 'eu-west-1'
            },
            'hosts': [
                {
                    'name': 'bar',
                    'profile': 'test-profile',
                    'region': 'eu-west-1'
                },
                {
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
