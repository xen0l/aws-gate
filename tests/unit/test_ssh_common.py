from datetime import timedelta

import pytest
from hypothesis import given, example, settings
from hypothesis.strategies import text, integers, sampled_from

from aws_gate.constants import DEFAULT_GATE_KEY_PATH
from aws_gate.ssh_common import (
    SshKey,
    SUPPORTED_KEY_TYPES,
    KEY_MIN_SIZE,
    SshKeyUploader,
)


@settings(deadline=timedelta(milliseconds=400))
@given(sampled_from(SUPPORTED_KEY_TYPES), integers(min_value=KEY_MIN_SIZE))
def test_initialize_key(key_type, key_size):
    key = SshKey(key_type=key_type, key_size=key_size)

    assert key.key_path == DEFAULT_GATE_KEY_PATH
    assert key.key_type == key_type
    assert key.key_size == key_size


@pytest.mark.parametrize("key_type", SUPPORTED_KEY_TYPES)
def test_initialize_key_as_context_manager(mocker, key_type):
    mocker.patch("aws_gate.ssh_common.os")
    open_mock = mocker.patch("builtins.open", new_callable=mocker.mock_open())

    with SshKey(key_type=key_type):
        assert open_mock.called
        open_mock.assert_called_with(DEFAULT_GATE_KEY_PATH, "wb")


@pytest.mark.parametrize("key_type", SUPPORTED_KEY_TYPES)
def test_ssh_public_key(key_type):
    key = SshKey(key_type=key_type)
    key.generate()

    if key_type == "rsa":
        key_start_str = "ssh-rsa"
    else:
        key_start_str = "ssh-ed25519"

    assert key.public_key.decode().startswith(key_start_str)


@given(integers(max_value=KEY_MIN_SIZE))
@example(0)
@example(-1024)
def test_initialize_key_unsupported_key_size(key_size):
    with pytest.raises(ValueError):
        SshKey(key_size=key_size)


def test_initialize_key_invalid_key_path():
    with pytest.raises(ValueError):
        SshKey(key_path="")


@given(text())
def test_initialize_key_unsupported_key_type(key_type):
    with pytest.raises(ValueError):
        SshKey(key_type=key_type)


def test_ssh_key_file_permissions(mocker):
    mocker.patch("builtins.open", new_callable=mocker.mock_open())
    m = mocker.patch("aws_gate.ssh_common.os.chmod")

    key = SshKey()
    key.generate()
    key.write_to_file()

    assert m.called
    assert mocker.call(DEFAULT_GATE_KEY_PATH, 0o600) == m.call_args_list[0]


def test_delete_key(mocker):
    mocker.patch("builtins.open", new_callable=mocker.mock_open())
    m = mocker.patch("aws_gate.ssh_common.os", new_callable=mocker.MagicMock())

    key = SshKey()
    key.generate()
    key.write_to_file()
    key.delete()

    assert m.remove.called
    assert m.remove.call_args == mocker.call(DEFAULT_GATE_KEY_PATH)


def test_uploader(ec2_ic_mock, ssh_key, instance_id):
    uploader = SshKeyUploader(
        instance_id=instance_id, az="eu-west-1a", ssh_key=ssh_key, ec2_ic=ec2_ic_mock
    )
    uploader.upload()

    assert ec2_ic_mock.send_ssh_public_key.called


def test_uploader_as_context_manager(ec2_ic_mock, ssh_key, instance_id):
    with SshKeyUploader(
        instance_id=instance_id, az="eu-west-1a", ssh_key=ssh_key, ec2_ic=ec2_ic_mock
    ):
        assert ec2_ic_mock.send_ssh_public_key.called


def test_uploader_exception(ec2_ic_mock, ssh_key, instance_id):
    ec2_ic_mock.configure_mock(
        **{"send_ssh_public_key.return_value": {"Success": False, "RequestId": "12345"}}
    )
    with pytest.raises(ValueError):
        uploader = SshKeyUploader(
            instance_id=instance_id,
            az="eu-west-1a",
            ssh_key=ssh_key,
            ec2_ic=ec2_ic_mock,
        )
        uploader.upload()
