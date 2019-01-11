import unittest
import unittest.mock
import io

from placebo.utils import placebo_session
from aws_gate.list import list_instances


class TestList(unittest.TestCase):

    @placebo_session
    def setUp(self, session):
        self.ec2 = session.resource('ec2', region_name='eu-west-1')
        self.ssm = session.client('ssm', region_name='eu-west-1')

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @unittest.mock.patch('aws_gate.list.get_aws_resource')
    @unittest.mock.patch('aws_gate.list.get_aws_client')
    def test_list_instances(self, mock_client, mock_resource, mock_stdout):
        mock_client.return_value = self.ssm
        mock_resource.return_value = self.ec2
        list_instances()
        self.assertEqual(mock_stdout.getvalue(), "i-0c32153096cd68a6d - dummy-instance\n")
