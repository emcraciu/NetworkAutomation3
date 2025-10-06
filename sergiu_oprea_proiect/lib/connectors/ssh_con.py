import time

import paramiko

class SshConnection:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh = None

    def __enter__(self):
        return self

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
        )

    def exec_command(self, command: str):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.read()

    def create_shell(self):
        self.shell = self.ssh.invoke_shell()

    def send(self, command: str):
        self.shell.send(command)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close(self):
        if self.ssh:
            self.ssh.close()

