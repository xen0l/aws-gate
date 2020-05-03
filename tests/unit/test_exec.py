# pylint: disable=wrong-import-position
import pytest

from aws_gate.exec import ExecSession, exec  # noqa


def test_create_exec_session(ssm_mock, instance_id):
    sess = ExecSession(instance_id=instance_id, ssm=ssm_mock, command=["ls", "-l"])
    sess.create()

    assert ssm_mock.start_session.called


def test_terminate_exec_session(ssm_mock, instance_id):
    sess = ExecSession(instance_id=instance_id, command=["ls", "-l"], ssm=ssm_mock)

    sess.create()
    sess.terminate()

    assert ssm_mock.terminate_session.called


def test_open_exec_session(mocker, ssm_mock, instance_id):
    m = mocker.patch("aws_gate.session_common.execute_plugin", return_value="output")
    sess = ExecSession(instance_id=instance_id, command=["ls", "-l"], ssm=ssm_mock)
    sess.open()

    assert m.called


def test_exec_session_context_manager(ssm_mock, instance_id):
    with ExecSession(instance_id=instance_id, command=["ls", "-l"], ssm=ssm_mock):
        pass

    assert ssm_mock.start_session.called
    assert ssm_mock.terminate_session.called


def test_exec_session(mocker, instance_id, config):
    mocker.patch("aws_gate.exec.get_aws_client")
    mocker.patch("aws_gate.exec.get_aws_resource")
    mocker.patch("aws_gate.exec.query_instance", return_value=instance_id)
    session_mock = mocker.patch(
        "aws_gate.exec.ExecSession", return_value=mocker.MagicMock()
    )
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    exec(
        config=config,
        instance_name=instance_id,
        command={"ls", "-l"},
        profile_name="profile",
        region_name="eu-west-1",
    )
    assert session_mock.called


def test_exec_session_exception_invalid_profile(mocker, instance_id, config):
    mocker.patch("aws_gate.exec.get_aws_client")
    mocker.patch("aws_gate.exec.get_aws_resource")
    mocker.patch("aws_gate.exec.query_instance", return_value=None)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")

    with pytest.raises(ValueError):
        exec(
            config=config,
            profile_name="invalid-profile",
            instance_name=instance_id,
            command=["ls", "-l"],
        )


def test_exec_session_exception_invalid_region(mocker, instance_id, config):
    mocker.patch("aws_gate.exec.get_aws_client")
    mocker.patch("aws_gate.exec.get_aws_resource")
    mocker.patch("aws_gate.exec.query_instance", return_value=None)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")

    with pytest.raises(ValueError):
        exec(
            config=config,
            region_name="invalid-region",
            instance_name=instance_id,
            profile_name="default",
            command=["ls", "-l"],
        )


def test_exec_session_exception_unknown_instance_id(mocker, instance_id, config):
    mocker.patch("aws_gate.exec.get_aws_client")
    mocker.patch("aws_gate.exec.get_aws_resource")
    mocker.patch("aws_gate.exec.query_instance", return_value=None)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)

    with pytest.raises(ValueError):
        exec(
            config=config,
            instance_name=instance_id,
            command=["ls", "-l"],
            profile_name="profile",
            region_name="eu-west-1",
        )


def test_exec_session_without_config(mocker, instance_id, empty_config):
    mocker.patch("aws_gate.exec.get_aws_client")
    mocker.patch("aws_gate.exec.get_aws_resource")
    mocker.patch("aws_gate.exec.query_instance", return_value=None)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")

    with pytest.raises(ValueError):
        exec(
            config=empty_config,
            instance_name=instance_id,
            command=["ls", "-l"],
            profile_name="profile",
            region_name="eu-west-1",
        )
