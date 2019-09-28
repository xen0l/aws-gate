import json
import unittest
from unittest.mock import patch, MagicMock

from aws_gate.ssh_proxy import SSHProxySession, ssh_proxy


class TestSSHProxySession(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.config.configure_mock(**{
            'get_host.return_value': {
                'alias': 'test',
                'name': 'SSM-test',
                'profile': 'default',
                'region': 'eu-west-1'
            }
        })
        self.empty_config = MagicMock()
        self.empty_config.configure_mock(**{
            'get_host.return_value': {}
        })

        self.ssm = MagicMock()
        self.instance_id = 'i-0c32153096cd68a6d'
        self.ssh_key = MagicMock()
        self.ssh_key.configure_mock(**{
            'key_path.return_value': '/tmp/key'
        })

        self.response = {
            'SessionId': 'session-020bf6cd31f912b53',
            'TokenValue': 'randomtokenvalue'
        }

        self.region_name = 'eu-west-1'

    def test_create_ssh_proxy_session(self):
        with patch.object(self.ssm, 'start_session', return_value=self.response):
            sess = SSHProxySession(instance_id=self.instance_id, ssm=self.ssm)
            sess.create()

            self.assertTrue(self.ssm.start_session.called)

    def test_terminate_ssh_proxy_session(self):
        with patch.object(self.ssm, 'terminate_session', return_value=self.response):
            sess = SSHProxySession(instance_id=self.instance_id, ssm=self.ssm)

            sess.create()
            sess.terminate()

            self.assertTrue(self.ssm.terminate_session.called)

    def test_open_ssh_proxy_session(self):
        with patch('aws_gate.ssh_proxy.execute_plugin', return_value='output') as m:
            sess = SSHProxySession(instance_id=self.instance_id, ssm=self.ssm)
            sess.open()

            self.assertTrue(m.called)
