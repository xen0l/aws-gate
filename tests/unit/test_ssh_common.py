import unittest
from datetime import timedelta
from unittest.mock import patch, mock_open, MagicMock, call

from hypothesis import given, example, settings
from hypothesis.strategies import text, integers, sampled_from

from aws_gate.constants import DEFAULT_GATE_KEY_PATH
from aws_gate.ssh_common import (
    SshKey,
    SUPPORTED_KEY_TYPES,
    KEY_MIN_SIZE,
    SshKeyUploader,
)


class TestSSHCommon(unittest.TestCase):
    def setUp(self):
        self.ssh_key = MagicMock()
        self.ssh_key.configure_mock(
            **{"public_key.return_value": "ssh-rsa ranodombase64string"}
        )

    @settings(deadline=timedelta(milliseconds=400))
    @given(sampled_from(SUPPORTED_KEY_TYPES), integers(min_value=KEY_MIN_SIZE))
    def test_initialize_key(self, key_type, key_size):
        key = SshKey(key_type=key_type)

        self.assertTrue(key.key_path, DEFAULT_GATE_KEY_PATH)
        self.assertTrue(key.key_type, key_type)
        self.assertTrue(key.key_size, key_size)

    @settings(deadline=timedelta(milliseconds=400))
    @given(sampled_from(SUPPORTED_KEY_TYPES))
    def test_ssh_public_key(self, key_type):
        key = SshKey(key_type=key_type)
        key.generate()

        if key_type == "rsa":
            key_start_str = "ssh-rsa"
        else:
            key_start_str = "ssh-ed25519"

        self.assertTrue(key.public_key.decode().startswith(key_start_str))

    @given(text())
    def test_initialize_key_unsupported_key_type(self, key_type):
        with self.assertRaises(ValueError):
            SshKey(key_type=key_type)

    @given(integers(max_value=KEY_MIN_SIZE))
    @example(0)
    @example(-1024)
    def test_initialize_key_unsupported_key_size(self, key_size):
        with self.assertRaises(ValueError):
            SshKey(key_size=key_size)

    def test_initialize_key_invalid_key_path(self):
        with self.assertRaises(ValueError):
            SshKey(key_path="")

    @settings(deadline=timedelta(milliseconds=400))
    @given(sampled_from(SUPPORTED_KEY_TYPES))
    def test_initialize_key_as_context_manager(self, key_type):
        with patch("builtins.open", new_callable=mock_open()) as open_mock, patch(
            "aws_gate.ssh_common.os"
        ):
            with SshKey(key_type=key_type):
                self.assertTrue(open_mock.called)
                open_mock.assert_called_with(DEFAULT_GATE_KEY_PATH, "wb")

    def test_ssh_key_file_permissions(self):
        with patch("builtins.open", new_callable=mock_open()), patch(
            "aws_gate.ssh_common.os.chmod"
        ) as m:
            key = SshKey()
            key.generate()
            key.write_to_file()

            self.assertTrue(m.called)
            self.assertEqual(call(DEFAULT_GATE_KEY_PATH, 0o600), m.call_args)

    def test_delete_key(self):
        with patch("builtins.open", new_callable=mock_open()), patch(
            "aws_gate.ssh_common.os", new_callable=MagicMock()
        ) as m:
            key = SshKey()
            key.generate()
            key.write_to_file()
            key.delete()

            self.assertTrue(m.remove.called)
            self.assertEqual(m.remove.call_args, call(DEFAULT_GATE_KEY_PATH))

    def test_uploader(self):
        ec2_ic_mock = MagicMock()

        uploader = SshKeyUploader(
            instance_id="i-1234567890",
            az="eu-west-1a",
            ssh_key=self.ssh_key,
            ec2_ic=ec2_ic_mock,
        )
        uploader.upload()

        self.assertTrue(ec2_ic_mock.send_ssh_public_key.called)

    def test_uploader_as_context_manager(self):
        ec2_ic_mock = MagicMock()
        with SshKeyUploader(
            instance_id="i-1234567890",
            az="eu-west-1a",
            ssh_key=self.ssh_key,
            ec2_ic=ec2_ic_mock,
        ):
            self.assertTrue(ec2_ic_mock.send_ssh_public_key.called)

    def test_uploader_exception(self):
        ec2_ic_mock = MagicMock()
        ec2_ic_mock.configure_mock(
            **{
                "send_ssh_public_key.return_value": {
                    "Success": False,
                    "RequestId": "12345",
                }
            }
        )

        uploader = SshKeyUploader(
            instance_id="i-1234567890",
            az="eu-west-1a",
            ssh_key=self.ssh_key,
            ec2_ic=ec2_ic_mock,
        )
        with self.assertRaises((ValueError)):
            uploader.upload()
