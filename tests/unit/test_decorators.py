from subprocess import PIPE

import pytest

from aws_gate.decorators import (
    plugin_required,
    plugin_version,
    _plugin_exists,
    valid_aws_profile,
    valid_aws_region,
)


def test_plugin_exists(mocker):
    m = mocker.patch("aws_gate.decorators.os.path.exists")

    _plugin_exists("foo")

    assert m.called
    assert m.call_args == mocker.call("foo")


def test_plugin_required(mocker):
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)

    @plugin_required
    def test_function():
        return "executed"

    assert test_function() == "executed"


def test_plugin_required_plugin_not_installed(mocker):
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=False)

    @plugin_required
    def test_function():
        return "executed"

    with pytest.raises(OSError):
        test_function()


@pytest.mark.parametrize("version", ["1.1.23.0", "1.2.7.0"])
def test_plugin_version(mocker, version):
    m = mocker.patch("aws_gate.decorators.execute_plugin", return_value=version)

    @plugin_version("1.1.23.0")
    def test_function():
        return "executed"

    assert test_function() == "executed"
    assert m.call_args == mocker.call(["--version"], stdout=PIPE, stderr=PIPE)


@pytest.mark.parametrize("version", ["1.1.25.0", "1.2.7.0"])
def test_plugin_version_bad_version(mocker, version):
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")

    @plugin_version(version)
    def test_function():
        return "executed"

    with pytest.raises(ValueError):
        test_function()


def test_valid_aws_profile(mocker):
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    @valid_aws_profile
    def test_function(profile_name):
        return profile_name

    assert test_function(profile_name="profile") == "profile"


def test_valid_aws_profile_invalid_profile(mocker):
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=False)

    @valid_aws_profile
    def test_function(profile_name):
        return profile_name

    with pytest.raises(ValueError):
        test_function(profile_name="invalid-profile")


def test_valid_aws_region(mocker):
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)

    @valid_aws_region
    def test_function(region_name):
        return region_name

    assert test_function(region_name="eu-west-1") == "eu-west-1"


def test_valid_aws_region_invalid_region(mocker):
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=False)

    @valid_aws_region
    def test_function(region_name):
        return region_name

    with pytest.raises(ValueError):
        test_function(region_name="invalid-region")
