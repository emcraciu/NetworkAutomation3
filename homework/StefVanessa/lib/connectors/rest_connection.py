# lib/connectors1/rest_connection.py
import requests

class RESTConnection:
    def __init__(self, ip, username, password, port=443, verify_ssl=False):
        self.base_url = f"https://{ip}:{port}/api"
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session = None

    def connect(self):
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.verify = self.verify_ssl
        return self

    def get(self, endpoint):
        url = self.base_url + endpoint
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def post(self, endpoint, data):
        url = self.base_url + endpoint
        resp = self.session.post(url, json=data)
        resp.raise_for_status()
        return resp.json()

    def disconnect(self):
        if self.session:
            self.session.close()
