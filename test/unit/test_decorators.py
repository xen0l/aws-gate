import unittest
from unittest.mock import patch, call

from aws_gate.decorators import (
    plugin_required,
    plugin_version,
    _plugin_exists,
    valid_aws_profile,
    valid_aws_region,
)


class TestDecorators(unittest.TestCase):
    def test_plugin_exists(self):
        with patch("aws_gate.decorators.os.path.exists") as m:
            _plugin_exists("foo")

            self.assertTrue(m.called)
            self.assertEqual(m.call_args, call("foo"))

    def test_plugin_required(self):
        with patch("aws_gate.decorators._plugin_exists", return_value=True):

            @plugin_required
            def test_function():
                return "executed"

            self.assertEqual(test_function(), "executed")

    def test_plugin_required_plugin_not_installed(self):
        with patch("aws_gate.decorators._plugin_exists", return_value=False):

            @plugin_required
            def test_function():
                return "executed"

            with self.assertRaises(OSError):
                test_function()

    def test_plugin_version(self):
        with patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0") as m:

            @plugin_version("1.1.23.0")
            def test_function():
                return "executed"

            self.assertEqual(test_function(), "executed")
            self.assertEqual(m.call_args, call(["--version"], capture_output=True))

    def test_plugin_version_bad_version(self):
        with patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0"):

            @plugin_version("1.1.25.0")
            def test_function():
                return "executed"

            with self.assertRaises(ValueError):
                test_function()

    def test_valid_aws_profile(self):
        with patch("aws_gate.decorators.is_existing_profile", return_value=True):

            @valid_aws_profile
            def test_function(profile_name):
                return profile_name

            self.assertEqual(test_function(profile_name="profile"), "profile")

    def test_valid_aws_profile_invalid_profile(self):
        with patch("aws_gate.decorators.is_existing_profile", return_value=False):

            @valid_aws_profile
            def test_function(profile_name):
                return profile_name

            with self.assertRaises(ValueError):
                test_function(profile_name="invalid-profile")

    def test_valid_aws_region(self):
        with patch("aws_gate.decorators.is_existing_region", return_value=True):

            @valid_aws_region
            def test_function(region_name):
                return region_name

            self.assertEqual(test_function(region_name="eu-west-1"), "eu-west-1")

    def test_valid_aws_region_invalid_region(self):
        with patch("aws_gate.decorators.is_existing_region", return_value=False):

            @valid_aws_region
            def test_function(region_name):
                return region_name

            with self.assertRaises(ValueError):
                test_function(region_name="invalid-region")
