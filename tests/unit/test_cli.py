import argparse
import os
from unittest.mock import MagicMock, create_autospec

import pytest
from marshmallow import ValidationError

from aws_gate.cli import main, _get_profile, _get_region, parse_arguments


def test_cli_param_error():
    with pytest.raises(SystemExit):
        main()


def test_cli_invalid_config(mocker):
    mocker.patch(
        "aws_gate.cli.parse_arguments",
        return_value=mocker.MagicMock(subcommand="bootstrap"),
    )
    mocker.patch(
        "aws_gate.cli.load_config_from_files",
        side_effect=ValidationError(message="error"),
    )

    with pytest.raises(ValueError):
        main()


def test_cli_parse_arguments_unknown_subcommand(mocker):
    parser_mock = mocker.MagicMock()
    parser_mock.configure_mock(
        **{"parse_args.return_value": mocker.MagicMock(subcommand=False)}
    )

    exit_mock = mocker.patch("sys.exit")
    mocker.patch("aws_gate.cli.argparse.ArgumentParser", return_value=parser_mock)

    parse_arguments()

    assert parser_mock.print_help.called
    assert exit_mock.called
    assert exit_mock.call_args == mocker.call(1)


def test_cli_default_profile_from_aws_vault(mocker):
    mocker.patch.dict(os.environ, {"AWS_VAULT": "vault_profile"})
    mocker.patch(
        "aws_gate.cli.parse_arguments", return_value=mocker.MagicMock(subcommand="list")
    )
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)
    mocker.patch("aws_gate.cli.list_instances")
    logger_mock = mocker.patch("aws_gate.cli.logging.getLogger")
    m = mocker.patch("aws_gate.cli._get_profile")

    main()

    assert m.called
    assert m.call_args[1]["default"] == "vault_profile"
    assert logger_mock.called


@pytest.mark.parametrize(
    "args, config, default, expected",
    [
        (
            MagicMock(profile="args_profile", region="args_region"),
            MagicMock(default_profile="config_profile", default_region="config_region"),
            "args_profile",
            "args_profile",
        ),
        (
            create_autospec(argparse.Namespace),
            MagicMock(default_profile="config_profile", default_region="config_region"),
            "config_profile",
            "config_profile",
        ),
        (
            create_autospec(argparse.Namespace),
            MagicMock(default_profile=None),
            "default_profile",
            "default_profile",
        ),
    ],
    ids=["args", "config", "default"],
)
def test_cli_get_profile(args, config, default, expected):
    assert _get_profile(args, config, default) == expected


@pytest.mark.parametrize(
    "args, config, default, expected",
    [
        (
            MagicMock(profile="args_profile", region="args_region"),
            MagicMock(default_profile="config_profile", default_region="config_region"),
            "args_region",
            "args_region",
        ),
        (
            create_autospec(argparse.Namespace),
            MagicMock(default_profile="config_profile", default_region="config_region"),
            "config_region",
            "config_region",
        ),
        (
            create_autospec(argparse.Namespace),
            MagicMock(default_region=None),
            "default_region",
            "default_region",
        ),
    ],
    ids=["args", "config", "default"],
)
def test_cli_get_region(args, config, default, expected):
    assert _get_region(args, config, default) == expected


@pytest.mark.parametrize(
    "subcommand",
    [
        ("bootstrap", "bootstrap"),
        ("list", "list_instances"),
        ("ls", "list_instances"),
        ("session", "session"),
        ("ssh", "ssh"),
        ("ssh-config", "ssh_config"),
        ("ssh-proxy", "ssh_proxy"),
    ],
    ids=lambda x: x[0],
)
def test_cli_subcommand(mocker, subcommand):
    mocker.patch(
        "aws_gate.cli.parse_arguments",
        return_value=mocker.MagicMock(subcommand=subcommand[0]),
    )
    m = mocker.patch("aws_gate.cli.{}".format(subcommand[1]))

    main()

    assert m.called
