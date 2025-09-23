import json
import time
import requests
from bravado.client import SwaggerClient
from pyats.topology import Device
from bravado.requests_client import RequestsClient


class SwaggerConnector:
    def __init__(self, device: Device, **kwargs):
        print('got:', kwargs)
        self.device: Device = device
        self.client = None
        self._session = None
        self._headers = None
        self._auth = None
        self._url = None
        self.__access_token = None
        self.__refresh_token = None
        self.__token_type = None
        self.connected = False

    def connect(self):
        host = self.device.connections.swagger.ip
        port = self.device.connections.swagger.port
        protocol = self.device.connections.swagger.protocol
        self._url = f"{protocol}://{host}:{port}"
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.__login()
        self.connected = True
        return self

    def __login(self):
        endpoint = '/api/fdm/latest/fdm/token'
        username = self.device.credentials.default.username
        password = self.device.credentials.default.password.plaintext

        # Retry logic cu timpi de așteptare
        for attempt in range(3):
            response = requests.post(
                url=self._url + endpoint,
                headers=self._headers,
                verify=False,
                data=json.dumps(
                    {
                        'username': username,
                        'password': password,
                        'grant_type': 'password',
                    }
                )
            )

            if response.status_code == 200:
                tokens = response.json()
                self.__access_token = tokens['access_token']
                self.__refresh_token = tokens['refresh_token']
                self.__token_type = tokens['token_type']
                self._headers.update(
                    {'Authorization': f'{self.__token_type} {self.__access_token}'}
                )
                return

            print(f"[Login attempt {attempt+1}] failed: {response.status_code} {response.text}")
            time.sleep(2)  # mic delay înainte de retry

        raise Exception("Failed to authenticate after 3 attempts")

    def get_swagger_client(self):
        endpoint = '/apispec/ngfw.json'
        http_client = RequestsClient()
        http_client.session.verify = False
        http_client.ssl_verify = False
        http_client.session.headers = self._headers
        self.client = SwaggerClient.from_url(
            spec_url=self._url + endpoint,
            http_client=http_client,
            request_headers=self._headers,
            config={'validate_certificate': False, 'validate_responses': False},
        )
        return self.client