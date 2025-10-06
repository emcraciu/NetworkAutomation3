import time
import requests
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from pyats.topology import Device


class SwaggerConnection:
    def __init__(self, device: Device, **kwargs):
        print("got:", kwargs)
        self.device: Device = device
        self.client = None
        self._headers = None
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
        endpoint = "/api/fdm/latest/fdm/token"
        username = self.device.credentials.default.username
        password = self.device.credentials.default.password.plaintext

        # up to 7 attempts with delay
        for attempt in range(1, 8):
            try:
                print(f"[login] attempt {attempt} -> {self._url}{endpoint}")
                response = requests.post(
                    f"{self._url}{endpoint}",
                    headers={"Accept": "application/json"},
                    verify=False,
                    timeout=10,
                    json={
                        "grant_type": "password",
                        "username": username,
                        "password": password,
                    }
                )

                print(f"[login] HTTP status: {response.status_code}")
                if response.status_code == 200:
                    tokens = response.json()
                    self.__access_token = tokens["access_token"]
                    self.__refresh_token = tokens["refresh_token"]
                    self.__token_type = tokens["token_type"]
                    self._headers.update(
                        {"Authorization": f"{self.__token_type} {self.__access_token}"}
                    )
                    print("[login] authentication succeeded")
                    return

                # debug: preview part of the body
                print(f"[login] failed: {response.status_code} {response.text[:200]}")

            except requests.exceptions.RequestException as e:
                print(f"[login] connection error: {e}")

            time.sleep(4)

        raise Exception("Failed to authenticate after 7 attempts")

    def get_swagger_client(self):
        endpoint = "/apispec/ngfw.json"
        http_client = RequestsClient()
        http_client.session.verify = False
        http_client.ssl_verify = False
        http_client.session.headers = self._headers
        self.client = SwaggerClient.from_url(
            spec_url=self._url + endpoint,
            http_client=http_client,
            request_headers=self._headers,
            config={"validate_certificate": False, "validate_responses": False},
        )
        return self.client

    # def accept_eula(self):
    #     """Example: accept EULA and enable trial."""
    #     body = {
    #         "type": "initialprovision",
    #         "id": "default",
    #         "acceptEULA": True,
    #         "startTrialEvaluation": True,
    #         "selectedPerformanceTierId": "FTDv5",
    #     }
    #     self.client.InitialProvision.addInitialProvision(body=body).result()
    #     print("[eula] accepted and trial enabled")
