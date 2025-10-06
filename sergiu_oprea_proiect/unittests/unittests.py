"""unittests"""
import unittest
from pathlib import Path
from unittest.mock import Mock

from sergiu_oprea_proiect.lib.connectors.ssh_con import SshConnection
from sergiu_oprea_proiect.lib.connectors.telnet_con import TelnetConnection
from sergiu_oprea_proiect.path_helper import resource, PROJECT_ROOT


class TestSshConnection(unittest.TestCase):
    def test_ssh_connection_initialization(self):
        conn = SshConnection('192.168.1.1', 22, 'admin', 'password123')
        self.assertEqual(conn.host, '192.168.1.1')
        self.assertEqual(conn.port, 22)
        self.assertEqual(conn.username, 'admin')
        self.assertEqual(conn.password, 'password123')
        self.assertIsNone(conn.ssh)


class TestTelnetConnection(unittest.TestCase):
    def test_telnet_connection_initialization(self):
        conn = TelnetConnection('10.0.0.1', 23)
        self.assertEqual(conn.host, '10.0.0.1')
        self.assertEqual(conn.port, 23)
        self.assertIsNone(conn.reader)
        self.assertIsNone(conn.writer)


class TestPathHelper(unittest.TestCase):
    def test_resource_function_returns_correct_path(self):
        test_path = 'test/data.txt'
        result = resource(test_path)
        expected = PROJECT_ROOT / test_path
        self.assertEqual(result, expected)
        self.assertIsInstance(result, Path)


class TestSshConnectionClose(unittest.TestCase):
    def test_close_when_ssh_is_none(self):
        conn = SshConnection('192.168.1.1', 22, 'admin', 'password')
        conn.ssh = None
        conn.close()
        self.assertIsNone(conn.ssh)


class TestTelnetConnectionWrite(unittest.TestCase):
    def test_write_sends_data_to_writer(self):
        conn = TelnetConnection('10.0.0.1', 23)
        conn.writer = Mock()
        test_data = 'show version\n'
        conn.write(test_data)
        conn.writer.write.assert_called_once_with(test_data)


if __name__ == '__main__':
    unittest.main()
