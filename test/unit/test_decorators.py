
import unittest
from unittest.mock import patch

from aws_gate.decorators import plugin_required, plugin_version


class TestDecorators(unittest.TestCase):
    def test_plugin_required(self):
        with patch('aws_gate.decorators._plugin_exists', return_value=True):
            @plugin_required
            def test_function():
                return 'executed'

            self.assertEqual(test_function(), 'executed')

    def test_plugin_required_plugin_not_installed(self):
        with patch('aws_gate.decorators._plugin_exists', return_value=False):
            @plugin_required
            def test_function():
                return 'executed'

            with self.assertRaises(OSError):
                test_function()

    def test_plugin_version(self):
        with patch('aws_gate.decorators.execute', return_value='1.1.23.0'):
            @plugin_version('1.1.23.0')
            def test_function():
                return 'executed'

            self.assertEqual(test_function(), 'executed')

    def test_plugin_version_bad_version(self):
        with patch('aws_gate.decorators.execute', return_value='1.1.23.0'):
            @plugin_version('1.1.25.0')
            def test_function():
                return 'executed'

            with self.assertRaises(ValueError):
                test_function()
