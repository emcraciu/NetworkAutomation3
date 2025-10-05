import json
import requests
from bravado.client import SwaggerClient
from bravado.exception import HTTPUnprocessableEntity
from bravado.requests_client import RequestsClient
import time


class SwaggerConnector:
    def __init__(self, device_conn: dict):
        self.device_conn = device_conn
        self.client = None
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._url = None
        self.__access_token = None
        self.__refresh_token = None
        self.__token_type = None
        self.connected = False

    def connect(self):
        swagger_conn = self.device_conn['connections']['swagger']
        host = swagger_conn['ip']
        port = swagger_conn['port']
        protocol = swagger_conn.get('protocol', 'https')
        self._url = f"{protocol}://{host}:{port}"

        self.__login()
        self.connected = True
        return self

    def __login(self, max_retries=10, wait_seconds=10):
        """
        Login to FTD Swagger API with retry logic if the service is not ready.
        """
        endpoint = '/api/fdm/latest/fdm/token'
        creds = self.device_conn['credentials']['default']

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    url=self._url + endpoint,
                    headers=self._headers,
                    verify=False,
                    data=json.dumps({
                        'username': creds['username'],
                        'password': creds['password'],
                        'grant_type': 'password',
                    })
                )
                response.raise_for_status()

                resp_json = response.json()
                self.__access_token = resp_json['access_token']
                self.__refresh_token = resp_json['refresh_token']
                self.__token_type = resp_json['token_type']
                self._headers.update({'Authorization': f'{self.__token_type} {self.__access_token}'})
                print("Logged in successfully to FTD API")
                return

            except requests.exceptions.HTTPError as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    print(f"Retrying in {wait_seconds} seconds...")
                    time.sleep(wait_seconds)
                else:
                    raise Exception(f"FTD API unavailable after {max_retries} attempts") from e

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
            config={'validate_responses': False, 'validate_requests': False}
        )
        return self.client

    def accept_eula(self):
        body = {
            "type": "initialprovision",
            "id": "default",
            "acceptEULA": True,
            "startTrialEvaluation": True,
            "selectedPerformanceTierId": "FTDv5",
        }
        try:
            self.client.InitialProvision.addInitialProvision(body=body).result()
            print("EULA acceptată și FTD inițializat")
        except HTTPUnprocessableEntity as e:
            if "DeviceSetupAlreadyDone" in str(e):
                print("FTD already initialized, skipping EULA.")
            else:
                raise
