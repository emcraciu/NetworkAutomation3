import unittest
from unittest.mock import patch, MagicMock
from Gules_Bogdan_project.swagger import SwaggerConnector
from bravado.exception import HTTPUnprocessableEntity
from Gules_Bogdan_project.main import ssh_show_ip

class TestSwaggerConnector(unittest.TestCase):

    @patch('Gules_Bogdan_project.swagger.requests.post')
    def test_login_success(self, mock_post):
        """Testează login-ul SwaggerConnector"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'access123',
            'refresh_token': 'refresh123',
            'token_type': 'Bearer'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        device_conn = {
            'connections': {'swagger': {'ip': '1.1.1.1', 'port': 443}},
            'credentials': {'default': {'username': 'admin', 'password': 'pass'}}
        }

        connector = SwaggerConnector(device_conn)
        connector.connect()

        self.assertTrue(connector.connected)
        self.assertEqual(connector._SwaggerConnector__access_token, 'access123')
        self.assertEqual(connector._SwaggerConnector__refresh_token, 'refresh123')
        self.assertEqual(connector._SwaggerConnector__token_type, 'Bearer')

    @patch('Gules_Bogdan_project.swagger.SwaggerClient.from_url')
    @patch('Gules_Bogdan_project.swagger.requests.post')
    def test_connect_and_get_client(self, mock_post, mock_swagger_client):
        """Testează obținerea clientului Swagger"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'token',
            'refresh_token': 'refresh',
            'token_type': 'Bearer'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        mock_client_instance = MagicMock()
        mock_swagger_client.return_value = mock_client_instance

        device_conn = {
            'connections': {'swagger': {'ip': '1.1.1.2', 'port': 443}},
            'credentials': {'default': {'username': 'admin', 'password': 'pass'}}
        }

        connector = SwaggerConnector(device_conn)
        connector.connect()
        swagger_client = connector.get_swagger_client()

        self.assertEqual(swagger_client, mock_client_instance)
        self.assertTrue(connector.connected)
        self.assertTrue(mock_swagger_client.called)

    @patch('Gules_Bogdan_project.swagger.SwaggerClient.from_url')
    @patch('Gules_Bogdan_project.swagger.requests.post')
    def test_accept_eula_already_done(self, mock_post, mock_swagger_client):
        """Testează acceptarea EULA dacă deja a fost acceptată"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'token',
            'refresh_token': 'refresh',
            'token_type': 'Bearer'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        mock_client = MagicMock()
        mock_eula_method = MagicMock()
        mock_client.InitialProvision.addInitialProvision.return_value = mock_eula_method

        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 422
        mock_eula_method.result.side_effect = HTTPUnprocessableEntity(
            response=mock_response_obj,
            message="DeviceSetupAlreadyDone"
        )
        mock_swagger_client.return_value = mock_client

        device_conn = {
            'connections': {'swagger': {'ip': '1.1.1.3', 'port': 443}},
            'credentials': {'default': {'username': 'admin', 'password': 'pass'}}
        }

        connector = SwaggerConnector(device_conn)
        connector.connect()
        connector.client = connector.get_swagger_client()

        try:
            connector.accept_eula()
            success = True
        except HTTPUnprocessableEntity:
            success = False

        self.assertTrue(success)
        mock_client.InitialProvision.addInitialProvision.assert_called_once()

    @patch("subprocess.run")
    def test_ping_guest1_mocked(self, mock_subprocess):
        """Testează funcția ping_guest1 cu subprocess mock"""
        mock_subprocess.return_value = MagicMock(returncode=0)  # simulăm ping reușit

        from Gules_Bogdan_project.main import ping_guest1
        ping_guest1()

        # verificăm că subprocess.run a fost apelat cu argumentele corecte
        mock_subprocess.assert_called_once_with(["ping", "-c", "4", "192.168.201.10"], check=True)

    @patch("paramiko.SSHClient")
    def test_ssh_show_ip_mocked(self, mock_ssh_client):
        """Testează funcția ssh_show_ip cu conexiune mock"""
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"Interface output"
        mock_ssh.exec_command.return_value = (None, mock_stdout, None)

        ssh_show_ip("1.1.1.1", "user", "pass")

        self.assertTrue(mock_ssh.connect.called)
        self.assertTrue(mock_ssh.exec_command.called)
        mock_ssh.close.assert_called_once()

    @patch("subprocess.run")
    def test_ping_device_mocked(self, mock_subprocess):
        """Testează funcția ping_device cu subprocess mock"""
        mock_subprocess.return_value = MagicMock(returncode=0)  # simulăm ping reușit

        from Gules_Bogdan_project.main import ping_device
        ping_device("1.1.1.1")

        # verificăm că subprocess.run a fost apelat cu argumentele corecte
        mock_subprocess.assert_called_once_with(["ping", "-c", "4", "1.1.1.1"], check=True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
