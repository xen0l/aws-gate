import io
import unittest
from unittest.mock import patch

from aws_gate.constants import DEFAULT_GATE_KEY_PATH
from aws_gate.ssh_config import ssh_config, PROXY_COMMAND


class TestSSHConfig(unittest.TestCase):
    def test_ssh_config(self):
        expected_output_lines = [
            """Host *.eu-west-1.default""",
            """IdentityFile {}""".format(DEFAULT_GATE_KEY_PATH),
            """IdentitiesOnly yes""",
            """User ec2-user""",
            """Port 22""",
            """ProxyCommand {}""".format(" ".join(PROXY_COMMAND)),
            "\n",
        ]
        expected_output = "\n".join(expected_output_lines)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout, patch(
            "aws_gate.decorators.is_existing_region", return_value=True
        ), patch("aws_gate.decorators.is_existing_profile", return_value=True):
            ssh_config(profile_name="default", region_name="eu-west-1")

            self.assertEqual(mock_stdout.getvalue(), expected_output)

    def test_ssh_config_invalid_profile(self):
        with patch("aws_gate.decorators.is_existing_region", return_value=True):
            with self.assertRaises(ValueError):
                ssh_config(profile_name="invalid-profile", region_name="eu-west-1")

    def test_ssh_config_invalid_region(self):
        with patch("aws_gate.decorators.is_existing_profile", return_value=True):
            with self.assertRaises(ValueError):
                ssh_config(profile_name="default", region_name="invalid-region")


if __name__ == "__main__":
    unittest.main()
