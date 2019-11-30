import pytest

from aws_gate.ssh import SshSession, ssh


def test_create_ssh_session(ssm_mock, instance_id):
    sess = SshSession(instance_id=instance_id, ssm=ssm_mock)
    sess.create()

    assert ssm_mock.start_session.called


def test_terminate_ssh_session(ssm_mock, instance_id):
    sess = SshSession(instance_id=instance_id, ssm=ssm_mock)

    sess.create()
    sess.terminate()

    assert ssm_mock.terminate_session.called


@pytest.mark.parametrize(
    "test_input", [(False, "-q"), (True, "-vv")], ids=["DEBUG=False", "DEBUG=True"]
)
def test_open_ssh_session(mocker, ssm_mock, instance_id, test_input):
    debug, ssh_cmd_arg = test_input
    mocker.patch("aws_gate.ssh.DEBUG", debug)
    m = mocker.patch("aws_gate.ssh.execute", return_value="output")

    sess = SshSession(instance_id=instance_id, ssm=ssm_mock)
    sess.open()

    assert m.called
    assert ssh_cmd_arg in m.call_args[0][1]


def test_open_ssh_session_with_command(mocker, instance_id, ssm_mock):
    m = mocker.patch("aws_gate.ssh.execute", return_value="output")

    sess = SshSession(instance_id=instance_id, ssm=ssm_mock, command=["ls", "-l"])
    sess.open()

    assert m.called
    assert "--" in m.call_args[0][1]
    assert ["ls", "-l"] == m.call_args[0][1][-2:]


def test_open_ssh_session_host_key_verification(mocker, instance_id, ssm_mock):
    m = mocker.patch("aws_gate.ssh.execute", return_value="output")

    sess = SshSession(instance_id=instance_id, ssm=ssm_mock)
    sess.open()

    assert m.called
    assert "UserKnownHostsFile=/dev/null" in m.call_args[0][1]
    assert "StrictHostKeyChecking=no" in m.call_args[0][1]


def test_open_ssh_session_context_manager(instance_id, ssm_mock):
    with SshSession(instance_id=instance_id, ssm=ssm_mock):
        pass

    assert ssm_mock.start_session.called
    assert ssm_mock.terminate_session.called


def test_ssh_session(
    mocker, instance_id, ssh_key, get_instance_details_response, config
):
    mocker.patch("aws_gate.ssh.get_aws_client")
    mocker.patch("aws_gate.ssh.get_aws_resource")
    mocker.patch("aws_gate.ssh.query_instance", return_value=instance_id)
    ssh_session_mock = mocker.patch("aws_gate.ssh.SshSession")
    mocker.patch("aws_gate.ssh.SshKey", return_value=ssh_key)
    mocker.patch("aws_gate.ssh.SshKeyUploader")
    mocker.patch(
        "aws_gate.ssh.get_instance_details", return_value=get_instance_details_response
    )
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    ssh(
        config=config,
        instance_name=instance_id,
        profile_name="profile",
        region_name="eu-west-1",
    )

    assert ssh_session_mock.called


def test_ssh_exception_invalid_profile(mocker, instance_id, ssh_key, config):
    mocker.patch("aws_gate.ssh.get_aws_client")
    mocker.patch("aws_gate.ssh.get_aws_resource")
    mocker.patch("aws_gate.ssh.query_instance", return_value=None)
    mocker.patch("aws_gate.ssh.SshKey", return_value=ssh_key)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)

    with pytest.raises(ValueError):
        ssh(
            config=config,
            profile_name="invalid-profile",
            instance_name=instance_id,
            region_name="eu-west-1",
        )


def test_ssh_exception_invalid_region(mocker, instance_id, ssh_key, config):
    mocker.patch("aws_gate.ssh.get_aws_client")
    mocker.patch("aws_gate.ssh.get_aws_resource")
    mocker.patch("aws_gate.ssh.query_instance", return_value=None)
    mocker.patch("aws_gate.ssh.SshKey", return_value=ssh_key)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    with pytest.raises(ValueError):
        ssh(
            config=config,
            region_name="invalid-region",
            instance_name=instance_id,
            profile_name="default",
        )


def test_ssh_exception_unknown_instance_id(mocker, instance_id, ssh_key, config):
    mocker.patch("aws_gate.ssh.get_aws_client")
    mocker.patch("aws_gate.ssh.get_aws_resource")
    mocker.patch("aws_gate.ssh.query_instance", return_value=None)
    mocker.patch("aws_gate.ssh.SshKey", return_value=ssh_key)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)

    with pytest.raises(ValueError):
        ssh(
            config=config,
            instance_name=instance_id,
            profile_name="default",
            region_name="eu-west-1",
        )


def test_ssh_without_config(mocker, instance_id, ssh_key, empty_config):
    mocker.patch("aws_gate.ssh.get_aws_client")
    mocker.patch("aws_gate.ssh.get_aws_resource")
    mocker.patch("aws_gate.ssh.query_instance", return_value=None)
    mocker.patch("aws_gate.ssh.SshKey", return_value=ssh_key)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")

    with pytest.raises(ValueError):
        ssh(
            config=empty_config,
            instance_name=instance_id,
            profile_name="default",
            region_name="eu-west-1",
        )
