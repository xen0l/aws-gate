import unittest
from unittest.mock import patch, MagicMock

# pylint: disable=wrong-import-position
from aws_gate.session import SSMSession, session  # noqa


class TestSSMSession(unittest.TestCase):
    def setUp(self):
        mock_attrs = {"get_host.return_value": {}}

        self.config = MagicMock()
        self.empty_config = MagicMock()
        self.empty_config.configure_mock(**mock_attrs)
        self.ssm = MagicMock()
        self.instance_id = "i-0c32153096cd68a6d"

        self.response = {
            "SessionId": "session-020bf6cd31f912b53",
            "TokenValue": "randomtokenvalue",
        }

    def test_create_ssm_session(self):
        with patch.object(self.ssm, "start_session", return_value=self.response):
            sess = SSMSession(instance_id=self.instance_id, ssm=self.ssm)
            sess.create()

            self.assertTrue(self.ssm.start_session.called)

    def test_terminate_ssm_session(self):
        with patch.object(self.ssm, "terminate_session", return_value=self.response):
            sess = SSMSession(instance_id=self.instance_id, ssm=self.ssm)

            sess.create()
            sess.terminate()

            self.assertTrue(self.ssm.terminate_session.called)

    def test_open_ssm_session(self):
        with patch(
            "aws_gate.session_common.execute_plugin", return_value="output"
        ) as m:
            sess = SSMSession(instance_id=self.instance_id, ssm=self.ssm)
            sess.open()

            self.assertTrue(m.called)

    def test_ssm_session_context_manager(self):
        with patch.object(
            self.ssm, "start_session", return_value=self.response
        ) as sm, patch.object(
            self.ssm, "terminate_session", return_value=self.response
        ) as tm:
            with SSMSession(instance_id=self.instance_id, ssm=self.ssm):
                pass

            self.assertTrue(sm.called)
            self.assertTrue(tm.called)

    def test_ssm_session(self):
        with patch("aws_gate.session.get_aws_client", return_value=MagicMock()), patch(
            "aws_gate.session.get_aws_resource", return_value=MagicMock()
        ), patch(
            "aws_gate.session.query_instance", return_value=self.instance_id
        ), patch(
            "aws_gate.session.SSMSession", return_value=MagicMock()
        ) as session_mock, patch(
            "aws_gate.decorators._plugin_exists", return_value=True
        ), patch(
            "aws_gate.decorators.execute_plugin", return_value="1.1.23.0"
        ), patch(
            "aws_gate.decorators.is_existing_profile", return_value=True
        ):
            session(
                config=self.config,
                instance_name=self.instance_id,
                profile_name="profile",
                region_name="eu-west-1",
            )
            self.assertTrue(session_mock.called)

    def test_ssm_session_exception_invalid_profile(self):
        with patch("aws_gate.session.get_aws_client", return_value=MagicMock()), patch(
            "aws_gate.session.get_aws_resource", return_value=MagicMock()
        ), patch("aws_gate.session.query_instance", return_value=None), patch(
            "aws_gate.decorators._plugin_exists", return_value=True
        ), patch(
            "aws_gate.decorators.execute_plugin", return_value="1.1.23.0"
        ):
            with self.assertRaises(ValueError):
                session(
                    config=self.config,
                    profile_name="invalid-profile",
                    instance_name=self.instance_id,
                )

    def test_ssm_session_exception_invalid_region(self):
        with patch("aws_gate.session.get_aws_client", return_value=MagicMock()), patch(
            "aws_gate.session.get_aws_resource", return_value=MagicMock()
        ), patch("aws_gate.session.query_instance", return_value=None), patch(
            "aws_gate.decorators._plugin_exists", return_value=True
        ), patch(
            "aws_gate.decorators.execute_plugin", return_value="1.1.23.0"
        ):
            with self.assertRaises(ValueError):
                session(
                    config=self.config,
                    region_name="invalid-region",
                    instance_name=self.instance_id,
                    profile_name="default",
                )

    def test_ssm_session_exception_unknown_instance_id(self):
        with patch("aws_gate.session.get_aws_client", return_value=MagicMock()), patch(
            "aws_gate.session.get_aws_resource", return_value=MagicMock()
        ), patch("aws_gate.session.query_instance", return_value=None), patch(
            "aws_gate.decorators._plugin_exists", return_value=True
        ), patch(
            "aws_gate.decorators.execute_plugin", return_value="1.1.23.0"
        ), patch(
            "aws_gate.decorators.is_existing_profile", return_value=True
        ):
            with self.assertRaises(ValueError):
                session(
                    config=self.config,
                    instance_name=self.instance_id,
                    profile_name="profile",
                    region_name="eu-west-1",
                )

    def test_ssm_session_without_config(self):
        with patch("aws_gate.session.get_aws_client", return_value=MagicMock()), patch(
            "aws_gate.session.get_aws_resource", return_value=MagicMock()
        ), patch("aws_gate.session.query_instance", return_value=None), patch(
            "aws_gate.decorators._plugin_exists", return_value=True
        ), patch(
            "aws_gate.decorators.execute_plugin", return_value="1.1.23.0"
        ):
            with self.assertRaises(ValueError):
                session(
                    config=self.empty_config,
                    instance_name=self.instance_id,
                    profile_name="profile",
                    region_name="eu-west-1",
                )
