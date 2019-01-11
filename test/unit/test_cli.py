import unittest
import unittest.mock

from aws_gate.cli import main


class TestCli(unittest.TestCase):

    def test_cli_param_error(self):
        with self.assertRaises(SystemExit):
            main()
