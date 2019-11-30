import pytest

from aws_gate.ssh_proxy import SshProxySession, ssh_proxy


def test_create_ssh_proxy_session(ssm_mock, instance_id):
    sess = SshProxySession(instance_id=instance_id, ssm=ssm_mock)
    sess.create()

    assert ssm_mock.start_session.called


def test_terminate_ssh_proxy_session(ssm_mock, instance_id):
    sess = SshProxySession(instance_id=instance_id, ssm=ssm_mock)

    sess.create()
    sess.terminate()

    assert ssm_mock.terminate_session.called


def test_open_ssh_proxy_session(mocker, instance_id, ssm_mock):
    m = mocker.patch("aws_gate.session_common.execute_plugin", return_value="output")

    sess = SshProxySession(instance_id=instance_id, ssm=ssm_mock)
    sess.open()

    assert m.called


def test_ssh_proxy_session_context_manager(ssm_mock, instance_id):
    with SshProxySession(instance_id=instance_id, ssm=ssm_mock):
        pass

    assert ssm_mock.start_session.called
    assert ssm_mock.terminate_session.called


def test_ssh_proxy_session(
    mocker, instance_id, ssh_key, get_instance_details_response, config
):
    mocker.patch("aws_gate.ssh_proxy.get_aws_client")
    mocker.patch("aws_gate.ssh_proxy.get_aws_resource")
    mocker.patch("aws_gate.ssh_proxy.query_instance", return_value=instance_id)
    mocker.patch("aws_gate.ssh_proxy.SshKey", return_value=ssh_key)
    mocker.patch("aws_gate.ssh_proxy.SshKeyUploader", return_value=mocker.MagicMock())
    mocker.patch(
        "aws_gate.ssh_proxy.get_instance_details",
        return_value=get_instance_details_response,
    )
    session_mock = mocker.patch(
        "aws_gate.ssh_proxy.SshProxySession", return_value=mocker.MagicMock()
    )
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    ssh_proxy(
        config=config,
        instance_name=instance_id,
        profile_name="default",
        region_name="eu-west-1",
    )

    assert session_mock.called


def test_ssh_proxy_exception_invalid_profile(mocker, instance_id, ssh_key, config):
    mocker.patch("aws_gate.ssh_proxy.get_aws_client")
    mocker.patch("aws_gate.ssh_proxy.get_aws_resource")
    mocker.patch("aws_gate.ssh_proxy.query_instance", return_value=instance_id)
    mocker.patch("aws_gate.ssh_proxy.SshKey", return_value=ssh_key)
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")

    with pytest.raises(ValueError):
        ssh_proxy(
            config=config,
            profile_name="invalid-profile",
            instance_name=instance_id,
            region_name="eu-west-1",
        )


def test_ssh_proxy_exception_invalid_region(mocker, instance_id, ssh_key, config):
    mocker.patch("aws_gate.ssh_proxy.get_aws_client")
    mocker.patch("aws_gate.ssh_proxy.get_aws_resource")
    mocker.patch("aws_gate.ssh_proxy.query_instance", return_value=instance_id)
    mocker.patch("aws_gate.ssh_proxy.SshKey", return_value=ssh_key)
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")

    with pytest.raises(ValueError):
        ssh_proxy(
            config=config,
            region_name="invalid-region",
            instance_name=instance_id,
            profile_name="default",
        )


def test_ssh_proxy_exception_unknown_instance_id(mocker, ssh_key, instance_id, config):
    mocker.patch("aws_gate.ssh_proxy.get_aws_client")
    mocker.patch("aws_gate.ssh_proxy.get_aws_resource")
    mocker.patch("aws_gate.ssh_proxy.query_instance", return_value=None)
    mocker.patch("aws_gate.ssh_proxy.SshKey", return_value=ssh_key)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)

    with pytest.raises(ValueError):
        ssh_proxy(
            config=config,
            instance_name=instance_id,
            profile_name="default",
            region_name="eu-west-1",
        )


def test_ssh_proxy_without_config(mocker, ssh_key, instance_id, empty_config):
    mocker.patch("aws_gate.ssh_proxy.get_aws_client")
    mocker.patch("aws_gate.ssh_proxy.get_aws_resource")
    mocker.patch("aws_gate.ssh_proxy.query_instance", return_value=None)
    mocker.patch("aws_gate.ssh_proxy.SshKey", return_value=ssh_key)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")

    with pytest.raises(ValueError):
        ssh_proxy(
            config=empty_config,
            instance_name=instance_id,
            profile_name="default",
            region_name="eu-west-1",
        )
