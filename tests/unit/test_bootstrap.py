from subprocess import PIPE

import pytest
import requests

from aws_gate.bootstrap import (
    Plugin,
    MacPlugin,
    bootstrap,
    _check_plugin_version,
    LinuxPlugin,
)
from aws_gate.constants import DEFAULT_GATE_BIN_PATH, PLUGIN_INSTALL_PATH
from aws_gate.exceptions import UnsupportedPlatormError


@pytest.mark.parametrize(
    "platform", [("Linux", "LinuxPlugin"), ("Darwin", "MacPlugin")], ids=lambda x: x[0]
)
def test_bootstrap(mocker, platform):
    mocker.patch("aws_gate.bootstrap.platform.system", return_value=platform[0])
    m = mocker.patch(f"aws_gate.bootstrap.{platform[1]}")

    bootstrap()

    assert m.called


def test_bootstrap_unsupported_platform(mocker):
    mocker.patch("aws_gate.bootstrap.platform.system", return_value="non-existing-os")

    with pytest.raises(UnsupportedPlatormError):
        bootstrap()


def test_check_plugin_version(mocker):
    m = mocker.patch("aws_gate.bootstrap.execute")

    _check_plugin_version()

    assert m.called
    assert m.call_args == mocker.call(
        PLUGIN_INSTALL_PATH, ["--version"], stdout=PIPE, stderr=PIPE
    )


def test_plugin_is_installed(mocker):
    mocker.patch("aws_gate.bootstrap.shutil.which", return_value=PLUGIN_INSTALL_PATH)

    plugin = Plugin()

    assert not plugin.is_installed


def test_plugin_extract_raises_notimplementederror():
    plugin = Plugin()

    with pytest.raises(NotImplementedError):
        plugin.extract()


def test_plugin_download(mocker):
    mocker.patch("aws_gate.bootstrap.os")
    mocker.patch("aws_gate.bootstrap.shutil")
    requests_mock = mocker.patch("aws_gate.bootstrap.requests")

    plugin = Plugin()
    plugin.download()

    assert requests_mock.get.called


def test_plugin_download_exception(mocker):
    mocker.patch("aws_gate.bootstrap.os")
    mocker.patch("aws_gate.bootstrap.shutil")
    mocker.patch(
        "aws_gate.bootstrap.requests.get", side_effect=requests.exceptions.HTTPError
    )
    m = mocker.patch("aws_gate.bootstrap.logger.error")

    plugin = Plugin()
    plugin.download()

    assert m.called


def test_mac_plugin_extract_invalid_zip(mocker):
    mocker.patch("aws_gate.bootstrap.zipfile.is_zipfile", return_value=False)

    plugin = MacPlugin()

    with pytest.raises(ValueError):
        plugin.extract()


def test_mac_plugin_extract_valid(mocker):
    mocker.patch("aws_gate.bootstrap.zipfile.is_zipfile", return_value=True)
    mocker.patch("aws_gate.bootstrap.os.path.split")
    zip_mock = mocker.patch("aws_gate.bootstrap.zipfile.ZipFile")

    plugin = MacPlugin()
    plugin.extract()

    assert zip_mock.called


def test_mac_plugin_install_non_existent_bin_dir(mocker):
    mocker.patch("builtins.open", mocker.mock_open(read_data="data"))
    os_mock = mocker.patch("aws_gate.bootstrap.os")
    mocker.patch("aws_gate.bootstrap.os.path.exists", return_value=False)
    mocker.patch("aws_gate.bootstrap._check_plugin_version", return_value="1.1.23.0")
    shutil_mock = mocker.patch("aws_gate.bootstrap.shutil")

    plugin = MacPlugin()
    plugin.install()

    assert os_mock.makedirs.called
    assert os_mock.makedirs.call_args == mocker.call(DEFAULT_GATE_BIN_PATH)
    assert shutil_mock.copyfileobj.called
    assert os_mock.chmod.called


def test_linux_plugin_extract_valid(mocker):
    mocker.patch("aws_gate.bootstrap.os.path.split")
    tarfile_mock = mocker.patch("aws_gate.bootstrap.tarfile")
    unix_ar_mock = mocker.patch("aws_gate.bootstrap.unix_ar")

    plugin = LinuxPlugin()
    plugin.extract()

    assert unix_ar_mock.open.called
    assert tarfile_mock.open.called
