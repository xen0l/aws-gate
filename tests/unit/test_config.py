import os

import pytest
from marshmallow import ValidationError

from aws_gate.config import (
    GateConfig,
    EmptyConfigurationError,
    load_config_from_files,
    _locate_config_files,
    validate_profile,
    validate_region,
    _merge_data,
)
from aws_gate.constants import DEFAULT_GATE_CONFIG_PATH, DEFAULT_GATE_CONFIGD_PATH


def _load_config_files(config_files):
    config = load_config_from_files(config_files=config_files)
    assert isinstance(config, GateConfig)
    return config


@pytest.mark.parametrize(
    "test_input",
    [
        ("config_invalid.yaml", ValidationError),
        ("config_invalid_attribute.yaml", ValidationError),
        ("config_empty.yaml", EmptyConfigurationError),
        ("config_invalid_yaml.yaml", EmptyConfigurationError),
    ],
    ids=lambda x: x[0].split(".")[0],
)
def test_invalid_config(shared_datadir, test_input):
    test_file, exception = test_input
    with pytest.raises(exception):
        config_files = [shared_datadir / test_file]
        _load_config_files(config_files=config_files)


def test_valid_config(shared_datadir, mocker):
    mocker.patch("aws_gate.config.is_existing_profile", return_value=True)
    expected_config = {
        "defaults": {"profile": "default-profile", "region": "eu-west-1"},
        "hosts": [
            {
                "alias": "foobar",
                "name": "foobar",
                "profile": "test-profile",
                "region": "eu-west-1",
            }
        ],
    }

    config = _load_config_files(config_files=[shared_datadir / "config_valid.yaml"])

    assert config.defaults == expected_config["defaults"]
    assert config.hosts == expected_config["hosts"]
    assert config.default_profile == expected_config["defaults"]["profile"]
    assert config.default_region == expected_config["defaults"]["region"]


def test_valid_config_without_hosts(shared_datadir, mocker):
    mocker.patch("aws_gate.config.is_existing_profile", return_value=True)
    expected_config = {
        "defaults": {"profile": "default-profile", "region": "eu-west-1"}
    }

    config = _load_config_files(
        config_files=[shared_datadir / "config_valid_without_hosts.yaml"]
    )

    assert config.defaults == expected_config["defaults"]
    assert config.hosts == []
    assert config.default_profile == expected_config["defaults"]["profile"]
    assert config.default_region == expected_config["defaults"]["region"]


def test_valid_config_without_defaults(shared_datadir):
    with pytest.raises(ValidationError):
        _load_config_files(
            config_files=[shared_datadir / "config_valid_without_defaults.yaml"]
        )


def test_valid_config_without_defaults_mocked(shared_datadir, mocker):
    mocker.patch("aws_gate.config.is_existing_profile", return_value=True)

    config = _load_config_files(
        config_files=[shared_datadir / "config_valid_without_defaults.yaml"]
    )

    assert config.default_profile is None
    assert config.default_region is None


def test_valid_config_with_defaults_in_hosts(shared_datadir, mocker):
    mocker.patch("aws_gate.config.is_existing_profile", return_value=True)

    expected_config = {
        "defaults": {"profile": "default-profile", "region": "eu-west-1"},
        "hosts": [
            {
                "alias": "foobar",
                "name": "foobar",
                "profile": "default-profile",
                "region": "eu-west-1",
            }
        ],
    }

    config = _load_config_files(
        config_files=[shared_datadir / "config_valid_defaults_in_hosts.yaml"]
    )

    assert config.defaults == expected_config["defaults"]
    assert config.hosts == expected_config["hosts"]
    assert config.default_profile == expected_config["defaults"]["profile"]
    assert config.default_region == expected_config["defaults"]["region"]
    assert config.hosts[0]["profile"] == expected_config["defaults"]["profile"]
    assert config.hosts[0]["region"] == expected_config["defaults"]["region"]


def test_configd(shared_datadir, mocker):
    mocker.patch("aws_gate.config.is_existing_profile", return_value=True)

    expected_config = {
        "defaults": {"profile": "default-profile", "region": "eu-west-1"},
        "hosts": [
            {
                "alias": "bar",
                "name": "bar",
                "profile": "test-profile",
                "region": "eu-west-1",
            },
            {
                "alias": "foo",
                "name": "foo",
                "profile": "test-profile",
                "region": "eu-west-1",
            },
        ],
    }
    config_files = [
        os.path.join(shared_datadir, "configd", file)
        for file in sorted(os.listdir(shared_datadir / "configd"))
    ]
    config = _load_config_files(config_files=config_files)

    assert config.defaults == expected_config["defaults"]
    assert config.hosts == expected_config["hosts"]


def test_locate_config_files(mocker):
    mocker.patch("aws_gate.config.os.path.isdir", return_value=True)
    mocker.patch("aws_gate.config.os.listdir", return_value=["foo.yaml"])
    mocker.patch("aws_gate.config.os.path.isfile", return_value=True)
    expected_config_files = [
        os.path.join(DEFAULT_GATE_CONFIGD_PATH, "foo.yaml"),
        DEFAULT_GATE_CONFIG_PATH,
    ]
    assert _locate_config_files() == expected_config_files


def test_config_get_host(shared_datadir, mocker):
    mocker.patch("aws_gate.config.is_existing_profile", return_value=True)

    expected_host = {
        "alias": "foobar",
        "name": "foobar",
        "region": "eu-west-1",
        "profile": "test-profile",
    }

    config = _load_config_files(config_files=[shared_datadir / "config_get_host.yaml"])

    assert config.get_host("foobar") == expected_host
    assert config.get_host("non-existent") == {}


def test_validate_profile(mocker):
    mocker.patch("aws_gate.config.is_existing_profile", return_value=False)
    with pytest.raises(ValidationError):
        validate_profile("test-profile")


def test_validate_region(mocker):
    mocker.patch("aws_gate.config.is_existing_region", return_value=False)
    with pytest.raises(ValidationError):
        validate_region("test-region")


@pytest.mark.parametrize(
    "src, dst, expected",
    [
        ({"foo": "foo"}, {"bar": "bar"}, {"foo": "foo", "bar": "bar"}),
        ([3, 4], [1, 2], [1, 2, 3, 4]),
        (3, [1, 2], [1, 2, 3]),
        ("test", [1, 2], [1, 2, "test"]),
        ("src", "dst", "src"),
    ],
    ids=["dict-dict", "list-list", "int-list", "str-list", "str-str"],
)
def test_merge_config_data(src, dst, expected):
    assert _merge_data(src, dst) == expected


@pytest.mark.parametrize(
    "args",
    [(1, {}), ("test", {}), ([], {}), (set(), {}), (frozenset(), {})],
    ids=lambda x: type(x[0]).__name__,
)
def test_merge_config_data_exception(args):
    src, dst = args
    with pytest.raises(TypeError):
        _merge_data(src, dst)
