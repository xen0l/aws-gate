import pytest

from aws_gate.constants import DEFAULT_GATE_KEY_PATH
from aws_gate.ssh_config import ssh_config, PROXY_COMMAND


def test_ssh_config(mocker, capsys):
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

    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    ssh_config(profile_name="default", region_name="eu-west-1")

    out, _ = capsys.readouterr()

    assert out == expected_output


def test_ssh_config_invalid_profile(mocker):
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    with pytest.raises(ValueError):
        ssh_config(profile_name="invalid-profile", region_name="eu-west-1")


def test_ssh_config_invalid_region(mocker):
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)
    with pytest.raises(ValueError):
        ssh_config(profile_name="default", region_name="invalid-region")
