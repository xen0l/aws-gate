import json
import unittest
from unittest.mock import patch, MagicMock


# pylint: disable=wrong-import-position
from aws_gate.constants import PLUGIN_INSTALL_PATH
from aws_gate.ssh import SSHSession, ssh  # noqa


class TestSSHSession(unittest.TestCase):

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

    def test_create_ssh_session(self):
        with patch.object(self.ssm, 'start_session', return_value=self.response):
            sess = SSHSession(instance_id=self.instance_id, ssm=self.ssm)
            sess.create()

            self.assertTrue(self.ssm.start_session.called)

    def test_terminate_ssh_session(self):
        with patch.object(self.ssm, 'terminate_session', return_value=self.response):
            sess = SSHSession(instance_id=self.instance_id, ssm=self.ssm)

            sess.create()
            sess.terminate()

            self.assertTrue(self.ssm.terminate_session.called)

    def test_open_ssh_session(self):
        mock_output = MagicMock(stdout=b'output')

        with patch('aws_gate.ssh.execute', return_value=mock_output) as m:
            sess = SSHSession(instance_id=self.instance_id, ssm=self.ssm)
            sess.open()

            self.assertTrue(m.called)

    def test_ssh_session_context_manager(self):
        with patch.object(self.ssm, 'start_session', return_value=self.response) as sm, \
                patch.object(self.ssm, 'terminate_session', return_value=self.response) as tm:
            with SSHSession(instance_id=self.instance_id, ssm=self.ssm):
                pass

            self.assertTrue(sm.called)
            self.assertTrue(tm.called)

    def test_ssh_session_generated_command(self):
        mock_output = MagicMock(stdout=b'output')

        with patch.object(self.ssm, 'start_session', return_value=self.response), \
                patch.object(self.ssm, 'terminate_session', return_value=self.response), \
                patch('aws_gate.ssh.execute', return_value=mock_output):
            with SSHSession(instance_id=self.instance_id, ssm=self.ssm) as ssh_session:

                ssh_session.open()

            expected_cmd = ['ssh', '-l', 'ec2-user', '-p', '22', '-F', '/dev/null', '-q', '-o']
            expected_cmd.append('ProxyCommand="{}"'.format(' '.join([PLUGIN_INSTALL_PATH,
                                                                     json.dumps(self.response),
                                                                     self.region_name,
                                                                     'StartSession'])
                                                           ))
            expected_cmd.append(self.instance_id)

            self.assertIsInstance(ssh_session.ssh_cmd, list)
            self.assertEqual(ssh_session.ssh_cmd, expected_cmd)

    def test_ssh_session_generated_command_debug(self):
        mock_output = MagicMock(stdout=b'output')

        with patch.object(self.ssm, 'start_session', return_value=self.response), \
                patch.object(self.ssm, 'terminate_session', return_value=self.response), \
                patch('aws_gate.ssh.DEBUG', return_value=True), \
                patch('aws_gate.ssh.execute', return_value=mock_output):
            with SSHSession(instance_id=self.instance_id, ssm=self.ssm) as ssh_session:

                ssh_session.open()

            expected_cmd = ['ssh', '-l', 'ec2-user', '-p', '22', '-F', '/dev/null', '-vv', '-o']
            expected_cmd.append('ProxyCommand="{}"'.format(' '.join([PLUGIN_INSTALL_PATH,
                                                                     json.dumps(self.response),
                                                                     self.region_name,
                                                                     'StartSession'])
                                                           ))
            expected_cmd.append(self.instance_id)

            self.assertIsInstance(ssh_session.ssh_cmd, list)
            self.assertEqual(ssh_session.ssh_cmd, expected_cmd)

    def test_ssh_session(self):
        with patch('aws_gate.session.get_aws_client', return_value=MagicMock()), \
                patch('aws_gate.ssh.get_aws_resource', return_value=MagicMock()), \
                patch('aws_gate.ssh.query_instance', return_value=self.instance_id), \
                patch('aws_gate.ssh.GateKey', return_value=self.ssh_key), \
                patch('aws_gate.ssh.SSHSession', return_value=MagicMock()) as session_mock, \
                patch('aws_gate.ssh.is_existing_profile', return_value=True), \
                patch('aws_gate.decorators._plugin_exists', return_value=True), \
                patch('aws_gate.decorators.execute', return_value='1.1.23.0'):
            ssh(config=self.config, instance_name=self.instance_id)
            self.assertTrue(session_mock.called)

    def test_ssh_exception_invalid_profile(self):
        with patch('aws_gate.session.get_aws_client', return_value=MagicMock()), \
                patch('aws_gate.ssh.get_aws_resource', return_value=MagicMock()), \
                patch('aws_gate.ssh.query_instance', return_value=None), \
                patch('aws_gate.ssh.GateKey', return_value=self.ssh_key), \
                patch('aws_gate.decorators._plugin_exists', return_value=True), \
                patch('aws_gate.decorators.execute', return_value='1.1.23.0'):
            with self.assertRaises(ValueError):
                ssh(config=self.config, profile_name='invalid-profile', instance_name=self.instance_id)

    def test_ssh_exception_invalid_region(self):
        with patch('aws_gate.session.get_aws_client', return_value=MagicMock()), \
                patch('aws_gate.ssh.get_aws_resource', return_value=MagicMock()), \
                patch('aws_gate.ssh.query_instance', return_value=None), \
                patch('aws_gate.ssh.GateKey', return_value=self.ssh_key), \
                patch('aws_gate.decorators._plugin_exists', return_value=True), \
                patch('aws_gate.decorators.execute', return_value='1.1.23.0'):
            with self.assertRaises(ValueError):
                ssh(config=self.config, region_name='invalid-region', instance_name=self.instance_id)

    def test_ssh_exception_unknown_instance_id(self):
        with patch('aws_gate.session.get_aws_client', return_value=MagicMock()), \
                patch('aws_gate.ssh.get_aws_resource', return_value=MagicMock()), \
                patch('aws_gate.ssh.query_instance', return_value=None), \
                patch('aws_gate.ssh.GateKey', return_value=self.ssh_key), \
                patch('aws_gate.decorators._plugin_exists', return_value=True), \
                patch('aws_gate.decorators.execute', return_value='1.1.23.0'):
            with self.assertRaises(ValueError):
                ssh(config=self.config, instance_name=self.instance_id)

    def test_ssh_without_config(self):
        with patch('aws_gate.session.get_aws_client', return_value=MagicMock()), \
                patch('aws_gate.ssh.get_aws_resource', return_value=MagicMock()), \
                patch('aws_gate.ssh.query_instance', return_value=None), \
                patch('aws_gate.ssh.GateKey', return_value=self.ssh_key), \
                patch('aws_gate.decorators._plugin_exists', return_value=True), \
                patch('aws_gate.decorators.execute', return_value='1.1.23.0'):
            with self.assertRaises(ValueError):
                ssh(config=self.empty_config, instance_name=self.instance_id)
