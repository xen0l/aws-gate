import pytest

from aws_gate.port_forward import port_forward, SSMPortForwardSession


def test_create_ssm_forward_session(ssm_mock, instance_id):
    sess = SSMPortForwardSession(
        instance_id=instance_id, ssm=ssm_mock, target_host="localhost", target_port=1234
    )
    sess.create()

    assert ssm_mock.start_session.called


def test_terminate_ssm_forward_session(ssm_mock, instance_id):
    sess = SSMPortForwardSession(
        instance_id=instance_id, ssm=ssm_mock, target_host="localhost", target_port=1234
    )

    sess.create()
    sess.terminate()

    assert ssm_mock.terminate_session.called


@pytest.mark.parametrize(
    "target_host",
    [
        None,
        "my-fun-host",
    ],
    ids=["Target is None, Local Forward", "Target is not None, Remote Forward"],
)
def test_open_ssm_forward_session(mocker, instance_id, ssm_mock, target_host):
    m = mocker.patch("aws_gate.session_common.execute_plugin", return_value="output")

    sess = SSMPortForwardSession(
        instance_id=instance_id, ssm=ssm_mock, target_host=target_host, target_port=1234
    )
    sess.open()

    if target_host:
        expected_doc_name = "AWS-StartPortForwardingSessionToRemoteHost"
    else:
        expected_doc_name = "AWS-StartPortForwardingSession"

    assert sess._session_parameters.get("DocumentName") == expected_doc_name
    assert m.called


def test_ssm_forward_session_context_manager(ssm_mock, instance_id):
    with SSMPortForwardSession(
        instance_id=instance_id, ssm=ssm_mock, target_host="localhost", target_port=1234
    ):
        pass

    assert ssm_mock.start_session.called
    assert ssm_mock.terminate_session.called


def test_port_forward(mocker, instance_id, config):
    mocker.patch("aws_gate.port_forward.get_aws_client")
    mocker.patch("aws_gate.port_forward.get_aws_resource")
    mocker.patch("aws_gate.port_forward.query_instance", return_value=instance_id)
    port_forward_mock = mocker.patch(
        "aws_gate.port_forward.SSMPortForwardSession", return_value=mocker.MagicMock()
    )
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")

    port_forward(
        config=config,
        instance_name="instance_name",
        target_host="target_host",
        target_port=22,
        profile_name="default",
        region_name="eu-west-1",
    )

    assert port_forward_mock.called


def test_port_forward_exception_invalid_profile(mocker, instance_id, config):
    mocker.patch("aws_gate.port_forward.get_aws_client")
    mocker.patch("aws_gate.port_forward.get_aws_resource")
    mocker.patch("aws_gate.port_forward.query_instance", return_value=instance_id)
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")

    with pytest.raises(ValueError):
        port_forward(
            config=config,
            instance_name="instance_name",
            target_host="target_host",
            target_port=22,
            profile_name="invalid-default",
            region_name="eu-west-1",
        )


def test_port_forward_exception_invalid_region(mocker, instance_id, config):
    mocker.patch("aws_gate.port_forward.get_aws_client")
    mocker.patch("aws_gate.port_forward.get_aws_resource")
    mocker.patch("aws_gate.port_forward.query_instance", return_value=instance_id)
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    mocker.patch(
        "aws_gate.port_forward.SSMPortForwardSession", return_value=mocker.MagicMock()
    )
    with pytest.raises(ValueError):
        port_forward(
            config=config,
            region_name="not-a-region",
            instance_name="instance_name",
            target_port=22,
            profile_name="default",
            target_host="target_host",
        )


def test_port_forward_exception_unknown_instance_id(mocker, instance_id, config):
    mocker.patch("aws_gate.port_forward.get_aws_client")
    mocker.patch("aws_gate.port_forward.get_aws_resource")
    mocker.patch("aws_gate.port_forward.query_instance", return_value=None)
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    with pytest.raises(ValueError):
        port_forward(
            config=config,
            region_name="ap-southeast-2",
            instance_name=instance_id,
            target_port=22,
            profile_name="default",
            target_host="target_host",
        )


def test_port_forward_exception_without_config(mocker, instance_id, empty_config):
    mocker.patch("aws_gate.port_forward.get_aws_client")
    mocker.patch("aws_gate.port_forward.get_aws_resource")
    mocker.patch("aws_gate.port_forward.query_instance", return_value=None)
    mocker.patch("aws_gate.decorators.is_existing_profile", return_value=True)
    mocker.patch("aws_gate.decorators.is_existing_region", return_value=True)
    mocker.patch("aws_gate.decorators._plugin_exists", return_value=True)
    mocker.patch("aws_gate.decorators.execute_plugin", return_value="1.1.23.0")
    with pytest.raises(ValueError):
        port_forward(
            config=empty_config,
            region_name="ap-southeast-2",
            instance_name=instance_id,
            target_port=22,
            profile_name="default",
            target_host="target_host",
        )
