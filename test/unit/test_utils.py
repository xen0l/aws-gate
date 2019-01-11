import unittest
from unittest.mock import patch, MagicMock, call

from aws_gate.utils import is_existing_profile, _create_aws_session, get_aws_client, get_aws_resource


# pylint: disable=too-few-public-methods
class MockSession:
    def __init__(self):
        self._available_profiles = ['profile{}'.format(i) for i in range(5)]

    @property
    def available_profiles(self):
        return self._available_profiles


class TestUtils(unittest.TestCase):
    def test_existing_profile(self):
        with patch('aws_gate.utils._create_aws_session', return_value=MockSession()):
            self.assertTrue(is_existing_profile('profile1'))
            self.assertFalse(is_existing_profile('nonexistentprofile'))

    def test_create_aws_session(self):
        with patch('aws_gate.utils.boto3.session', return_value=MagicMock()) as session_mock:
            _create_aws_session(region_name='eu-west-1')

            self.assertTrue(session_mock.Session.called)
            self.assertEqual(session_mock.Session.mock_calls, [call(region_name='eu-west-1')])

    def test_create_aws_session_with_profile(self):
        with patch('aws_gate.utils.boto3.session', return_value=MagicMock()) as session_mock:
            _create_aws_session(region_name='eu-west-1', profile_name='default')

            self.assertTrue(session_mock.Session.called)
            self.assertEqual(session_mock.Session.mock_calls, [call(region_name='eu-west-1', profile_name='default')])

    def test_get_aws_client(self):
        with patch('aws_gate.utils._create_aws_session', return_value=MagicMock()) as mock:
            get_aws_client(service_name='ec2', region_name='eu-west-1')

            self.assertTrue(mock.called)
            self.assertEqual(mock.mock_calls, [])

    def test_get_aws_resource(self):
        with patch('aws_gate.utils._create_aws_session', return_value=MagicMock()) as mock:
            get_aws_resource(service_name='ec2', region_name='eu-west-1')

            self.assertTrue(mock.called)
