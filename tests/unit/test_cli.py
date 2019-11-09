import argparse
import os
import unittest
from unittest.mock import patch, MagicMock, create_autospec, call

import pytest
from marshmallow import ValidationError

from aws_gate.cli import main, _get_profile, _get_region, parse_arguments


class TestCli(unittest.TestCase):
    def setUp(self):
        self._args = MagicMock(profile="args_profile", region="args_region")
        self._config = MagicMock(
            default_profile="config_profile", default_region="config_region"
        )
        self._default_region = "default_region"
        self._default_profile = "default_profile"

    def test_cli_param_error(self):
        with self.assertRaises(SystemExit):
            main()

    def test_cli_invalid_config(self):
        with patch(
            "aws_gate.cli.parse_arguments",
            return_value=MagicMock(subcommand="bootstrap"),
        ), patch(
            "aws_gate.cli.load_config_from_files",
            side_effect=ValidationError(message="error"),
        ):
            with self.assertRaises(ValueError):
                main()

    def test_cli_parse_arguments_unknown_subcommand(self):
        parser_mock = MagicMock()
        parser_mock.configure_mock(
            **{"parse_args.return_value": MagicMock(subcommand=False)}
        )

        with patch(
            "aws_gate.cli.argparse.ArgumentParser", return_value=parser_mock
        ), patch("sys.exit") as exit_mock:
            parse_arguments()

            self.assertTrue(parser_mock.print_help.called)
            self.assertTrue(exit_mock.called)
            self.assertEqual(exit_mock.call_args, call(1))

    def test_cli_default_profile_from_aws_vault(self):
        with patch.dict(os.environ, {"AWS_VAULT": "vault_profile"}), patch(
            "aws_gate.cli.parse_arguments",
            return_value=MagicMock(subcommand="list_instances"),
        ), patch("aws_gate.decorators.is_existing_region", return_value=True), patch(
            "aws_gate.decorators.is_existing_profile", return_value=True
        ), patch(
            "aws_gate.cli.list_instances"
        ), patch(
            "aws_gate.cli.logging.getLogger"
        ) as logger_mock, patch(
            "aws_gate.cli._get_profile"
        ) as m:
            main()

            self.assertTrue(m.called)
            self.assertEqual(m.call_args[1]["default"], "vault_profile")

            self.assertTrue(logger_mock.called)


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
def test_get_profile(args, config, default, expected):
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
def test_get_region(args, config, default, expected):
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
        "aws_gate.cli.parse_arguments", return_value=MagicMock(subcommand=subcommand[0])
    )
    m = mocker.patch("aws_gate.cli.{}".format(subcommand[1]))

    main()

    assert m.called
