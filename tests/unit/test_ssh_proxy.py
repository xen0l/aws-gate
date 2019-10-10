import unittest
from unittest.mock import patch, MagicMock

from aws_gate.ssh_proxy import SshProxySession, ssh_proxy


class TestSSHProxySession(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.config.configure_mock(
            **{
                "get_host.return_value": {
                    "alias": "test",
                    "name": "SSM-test",
                    "profile": "default",
                    "region": "eu-west-1",
                }
            }
        )
        self.empty_config = MagicMock()
        self.empty_config.configure_mock(**{"get_host.return_value": {}})

        self.ssm = MagicMock()
        self.instance_id = "i-0c32153096cd68a6d"
        self.ssh_key = MagicMock()
        self.ssh_key.configure_mock(**{"key_path.return_value": "/tmp/key"})  # nosec

        self.response = {
            "SessionId": "session-020bf6cd31f912b53",
            "TokenValue": "randomtokenvalue",
        }

        self.region_name = "eu-west-1"

        self.get_instance_details_response = {"availability_zone": "eu-west-1a"}

    def test_create_ssh_proxy_session(self):
        with patch.object(self.ssm, "start_session", return_value=self.response):
            sess = SshProxySession(instance_id=self.instance_id, ssm=self.ssm)
            sess.create()

            self.assertTrue(self.ssm.start_session.called)

    def test_terminate_ssh_proxy_session(self):
        with patch.object(self.ssm, "terminate_session", return_value=self.response):
            sess = SshProxySession(instance_id=self.instance_id, ssm=self.ssm)

            sess.create()
            sess.terminate()

            self.assertTrue(self.ssm.terminate_session.called)

    def test_open_ssh_proxy_session(self):
        with patch(
            "aws_gate.session_common.execute_plugin", return_value="output"
        ) as m:
            sess = SshProxySession(instance_id=self.instance_id, ssm=self.ssm)
            sess.open()

            self.assertTrue(m.called)

    def test_ssh_proxy_session_context_manager(self):
        with patch.object(
            self.ssm, "start_session", return_value=self.response
        ) as sm, patch.object(
            self.ssm, "terminate_session", return_value=self.response
        ) as tm:
            with SshProxySession(instance_id=self.instance_id, ssm=self.ssm):
                pass

            self.assertTrue(sm.called)
            self.assertTrue(tm.called)

    def test_ssh_proxy_session(self):
        with patch(
            "aws_gate.ssh_proxy.get_aws_client", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.get_aws_resource", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.query_instance", return_value=self.instance_id
        ), patch(
            "aws_gate.ssh_proxy.SshKey", return_value=self.ssh_key
        ), patch(
            "aws_gate.ssh_proxy.SshKeyUploader", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.get_instance_details",
            return_value=self.get_instance_details_response,
        ), patch(
            "aws_gate.ssh_proxy.SshProxySession", return_value=MagicMock()
        ) as session_mock, patch(
            "aws_gate.decorators.is_existing_profile", return_value=True
        ), patch(
            "aws_gate.decorators._plugin_exists", return_value=True
        ), patch(
            "aws_gate.decorators.execute_plugin", return_value="1.1.23.0"
        ):
            ssh_proxy(
                config=self.config,
                instance_name=self.instance_id,
                profile_name="default",
                region_name="eu-west-1",
            )

            self.assertTrue(session_mock.called)

    def test_ssh_proxy_exception_invalid_profile(self):
        with patch(
            "aws_gate.ssh_proxy.get_aws_client", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.get_aws_resource", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.query_instance", return_value=None
        ), patch(
            "aws_gate.ssh_proxy.SshKey", return_value=self.ssh_key
        ), patch(
            "aws_gate.decorators._plugin_exists", return_value=True
        ), patch(
            "aws_gate.decorators.execute_plugin", return_value="1.1.23.0"
        ), patch(
            "aws_gate.decorators.is_existing_region", return_value=True
        ):
            with self.assertRaises(ValueError):
                ssh_proxy(
                    config=self.config,
                    profile_name="invalid-profile",
                    instance_name=self.instance_id,
                    region_name="eu-west-1",
                )

    def test_ssh_proxy_exception_invalid_region(self):
        with patch(
            "aws_gate.ssh_proxy.get_aws_client", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.get_aws_resource", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.query_instance", return_value=None
        ), patch(
            "aws_gate.ssh_proxy.SshKey", return_value=self.ssh_key
        ), patch(
            "aws_gate.decorators._plugin_exists", return_value=True
        ), patch(
            "aws_gate.decorators.execute_plugin", return_value="1.1.23.0"
        ), patch(
            "aws_gate.decorators.is_existing_profile", return_value=True
        ):
            with self.assertRaises(ValueError):
                ssh_proxy(
                    config=self.config,
                    region_name="invalid-region",
                    instance_name=self.instance_id,
                    profile_name="default",
                )

    def test_ssh_proxy_exception_unknown_instance_id(self):
        with patch(
            "aws_gate.ssh_proxy.get_aws_client", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.get_aws_resource", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.query_instance", return_value=None
        ), patch(
            "aws_gate.ssh_proxy.SshKey", return_value=self.ssh_key
        ), patch(
            "aws_gate.decorators._plugin_exists", return_value=True
        ), patch(
            "aws_gate.decorators.execute_plugin", return_value="1.1.23.0"
        ), patch(
            "aws_gate.decorators.is_existing_profile", return_value=True
        ), patch(
            "aws_gate.decorators.is_existing_region", return_value=True
        ):
            with self.assertRaises(ValueError):
                ssh_proxy(
                    config=self.config,
                    instance_name=self.instance_id,
                    profile_name="default",
                    region_name="eu-west-1",
                )

    def test_ssh_proxy_without_config(self):
        with patch(
            "aws_gate.ssh_proxy.get_aws_client", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.get_aws_resource", return_value=MagicMock()
        ), patch(
            "aws_gate.ssh_proxy.query_instance", return_value=None
        ), patch(
            "aws_gate.ssh_proxy.SshKey", return_value=self.ssh_key
        ), patch(
            "aws_gate.decorators._plugin_exists", return_value=True
        ), patch(
            "aws_gate.decorators.execute_plugin", return_value="1.1.23.0"
        ):
            with self.assertRaises(ValueError):
                ssh_proxy(
                    config=self.empty_config,
                    instance_name=self.instance_id,
                    profile_name="default",
                    region_name="eu-west-1",
                )
