import unittest
from unittest.mock import patch, MagicMock, call, mock_open

from aws_gate.exceptions import UnsupportedPlatormError
from aws_gate.config import DEFAULT_GATE_BIN_PATH, PLUGIN_INSTALL_PATH
from aws_gate.bootstrap import Plugin, MacPlugin, bootstrap


class TestBootstrap(unittest.TestCase):
    def test_plugin_is_installed(self):
        with patch('aws_gate.bootstrap.shutil.which', return_value=PLUGIN_INSTALL_PATH):
            plugin = Plugin()
            self.assertFalse(plugin.is_installed)

    def test_plugin_install_raises_notimplementederror(self):
        plugin = Plugin()
        with self.assertRaises(NotImplementedError):
            plugin.install()

    def test_plugin_extract_raises_notimplementederror(self):
        plugin = Plugin()
        with self.assertRaises(NotImplementedError):
            plugin.extract()

    def test_plugin_download(self):
        plugin = Plugin()
        with patch('aws_gate.bootstrap.os'), \
                patch('aws_gate.bootstrap.shutil'), \
                patch('aws_gate.bootstrap.requests', return_value=MagicMock()) as requests_mock:
            plugin.download()

            self.assertTrue(requests_mock.get.called)

    def test_mac_plugin_extract_invalid_zip(self):
        plugin = MacPlugin()
        with patch('aws_gate.bootstrap.zipfile.is_zipfile', return_value=False):
            with self.assertRaises(ValueError):
                plugin.extract()

    def test_mac_plugin_extract_valid(self):
        plugin = MacPlugin()
        with patch('aws_gate.bootstrap.zipfile.is_zipfile', return_value=True), \
                patch('aws_gate.bootstrap.os.path.split'), \
                patch('aws_gate.bootstrap.zipfile.ZipFile', return_value=MagicMock()) as zip_mock:
            plugin.extract()

            self.assertTrue(zip_mock.called)

    def test_mac_plugin_install_non_existent_bin_dir(self):
        plugin = MacPlugin()
        with patch('aws_gate.bootstrap.os') as os_mock, \
                patch('builtins.open', mock_open(read_data='data')), \
                patch('aws_gate.bootstrap.os.path.exists', return_value=False), \
                patch('aws_gate.bootstrap.shutil') as shutil_mock, \
                patch('aws_gate.bootstrap._check_plugin_version', return_value='1.1.23.0'):
            plugin.install()

            self.assertTrue(os_mock.mkdir.called)
            self.assertEqual(os_mock.mkdir.call_args, call(DEFAULT_GATE_BIN_PATH))
            self.assertTrue(shutil_mock.copyfileobj.called)
            self.assertTrue(os_mock.chmod.called)

    def test_bootstrap_unsupported_platform(self):
        with patch('aws_gate.bootstrap.platform.system', return_value='non-existing-os'):
            with self.assertRaises(UnsupportedPlatormError):
                bootstrap()

    def test_bootstrap_darwin(self):
        with patch('aws_gate.bootstrap.platform.system', return_value='Darwin'), \
                patch('aws_gate.bootstrap.MacPlugin', return_value=MagicMock()) as mock:
            bootstrap()

            self.assertTrue(mock.called)
