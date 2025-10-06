import time

import paramiko

HOST = '192.168.200.1'
PORT = 22  # replace with yours


class SshConnection:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh = None
        self.shell = None

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
        return self.ssh

    def execute(self, command, timeout=None):
        if self.ssh is None:
            raise RuntimeError("SSH not connected")
        stdin, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)
        return stdout.read().decode() + stderr.read().decode()

    def configure(self):
        stdin, stdout, stderr = self.ssh.exec_command('show version')
        time.sleep(1)
        print(stdout.read())

    def disconnect(self):
        if self.ssh:
            self.ssh.close()
            self.ssh = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == '__main__':
    conn = SshConnection(HOST, PORT, 'cisco', 'Cisco@123')
    conn.connect()
    conn.configure()


