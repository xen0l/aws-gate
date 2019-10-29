import argparse
import unittest
import os
from unittest.mock import patch, MagicMock, create_autospec, call

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

    def test_get_profile_from_args(self):
        self.assertEqual(
            _get_profile(
                args=self._args, config=self._config, default=self._default_profile
            ),
            "args_profile",
        )

    def test_get_profile_from_config(self):
        self.assertEqual(
            _get_profile(
                args=create_autospec(argparse.Namespace),
                config=self._config,
                default=self._default_profile,
            ),
            "config_profile",
        )

    def test_get_profile_from_default(self):
        self.assertEqual(
            _get_profile(
                args=create_autospec(argparse.Namespace),
                config=MagicMock(default_profile=None),
                default=self._default_profile,
            ),
            "default_profile",
        )

    def test_get_region_from_args(self):
        self.assertEqual(
            _get_region(
                args=self._args, config=self._config, default=self._default_region
            ),
            "args_region",
        )

    def test_get_region_from_config(self):
        self.assertEqual(
            _get_region(
                args=create_autospec(argparse.Namespace),
                config=self._config,
                default=self._default_region,
            ),
            "config_region",
        )

    def test_get_region_from_default(self):
        self.assertEqual(
            _get_region(
                args=create_autospec(argparse.Namespace),
                config=MagicMock(default_region=None),
                default=self._default_region,
            ),
            "default_region",
        )

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

    def test_cli_bootstrap(self):
        with patch(
            "aws_gate.cli.parse_arguments",
            return_value=MagicMock(subcommand="bootstrap"),
        ), patch("aws_gate.cli.bootstrap") as m:
            main()

            self.assertTrue(m.called)

    def test_cli_session(self):
        with patch(
            "aws_gate.cli.parse_arguments", return_value=MagicMock(subcommand="session")
        ), patch("aws_gate.cli.session") as m:
            main()

            self.assertTrue(m.called)

    def test_cli_list(self):
        with patch(
            "aws_gate.cli.parse_arguments", return_value=MagicMock(subcommand="list")
        ), patch("aws_gate.cli.list_instances") as m:
            main()

            self.assertTrue(m.called)

    def test_cli_ssh_config(self):
        with patch(
            "aws_gate.cli.parse_arguments",
            return_value=MagicMock(subcommand="ssh-config"),
        ), patch("aws_gate.cli.ssh_config") as m:
            main()

            self.assertTrue(m.called)

    def test_cli_ssh_proxy(self):
        with patch(
            "aws_gate.cli.parse_arguments",
            return_value=MagicMock(subcommand="ssh-proxy"),
        ), patch("aws_gate.cli.ssh_proxy") as m:
            main()

            self.assertTrue(m.called)

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
            "aws_gate.cli.parse_arguments", return_value=MagicMock(subcommand="list")
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
