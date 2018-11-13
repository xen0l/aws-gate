import errno
import os
import unittest
from unittest.mock import patch, MagicMock

from aws_gate.session import Session, session


class TestSession(unittest.TestCase):

    def setUp(self):
        self.ssm = MagicMock()
        self.instance_id = 'i-0c32153096cd68a6d'

        self.response = {
            'SessionId': 'session-020bf6cd31f912b53',
            'TokenValue': 'randomtokenvalue'
        }

    def test_create_session(self):
        with patch.object(self.ssm, 'start_session', return_value=self.response):
            sess = Session(instance_id=self.instance_id, ssm=self.ssm)
            sess.create()

            self.assertTrue(self.ssm.start_session.called)

    def test_terminate_session(self):
        with patch.object(self.ssm, 'terminate_session', return_value=self.response):
            sess = Session(instance_id=self.instance_id, ssm=self.ssm)

            sess.create()
            sess.terminate()

            self.assertTrue(self.ssm.terminate_session.called)

    def test_open_session(self):
        with patch('aws_gate.session.subprocess.check_call', return_value=True) as m:
            sess = Session(instance_id=self.instance_id, ssm=self.ssm)
            sess.open()

            self.assertTrue(m.called)

    def test_open_session_exception(self):
        with patch('aws_gate.session.subprocess.check_call',
                   side_effect=OSError(errno.ENOENT, os.strerror(errno.ENOENT))):
            with self.assertRaises(ValueError):
                sess = Session(instance_id=self.instance_id, ssm=self.ssm)
                sess.open()

    def test_context_manager(self):
        with patch.object(self.ssm, 'start_session', return_value=self.response) as sm, \
                patch.object(self.ssm, 'terminate_session', return_value=self.response) as tm:
            with Session(instance_id=self.instance_id, ssm=self.ssm):
                pass

            self.assertTrue(sm.called)
            self.assertTrue(tm.called)

    def test_session(self):
        with patch('aws_gate.session.get_aws_client', return_value=MagicMock()), \
                patch('aws_gate.session.get_aws_resource', return_value=MagicMock()), \
                patch('aws_gate.session.query_instance', return_value=self.instance_id), \
                patch('aws_gate.session.Session', return_value=MagicMock()) as session_mock:
            session(instance_name=self.instance_id)
            self.assertTrue(session_mock.called)

    def test_session_exception(self):
        with patch('aws_gate.session.get_aws_client', return_value=MagicMock()), \
                patch('aws_gate.session.get_aws_resource', return_value=MagicMock()), \
                patch('aws_gate.session.query_instance', return_value=None):
            with self.assertRaises(ValueError):
                session(instance_name=self.instance_id)
