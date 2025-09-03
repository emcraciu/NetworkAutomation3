import threading

from lib.connectors.ssh_con import SshConnection

HOST = '192.168.200.1'
PORT = 22
USER = 'admin'
PASS = 'Cisco@123'

devices = [
    {"host": '192.168.200.1', "port": 22, "username": 'admin', "password": 'Cisco@123'},
    {"host": '192.168.200.2', "port": 22, "username": 'admin', "password": 'Cisco@123'}
]


def configure_ip(host, port, user, passwd):
    ssh = SshConnection(host=host, port=port, username=user, password=passwd)
    ssh.connect()
    ssh.configure()


threads = []
for device in devices:
    t = threading.Thread(
        target=configure_ip,
        args=(
            device['host'], device['port'], device['username'], device['password']
        )
    )
    threads.append(t)
for thd in threads:
    thd.start()
