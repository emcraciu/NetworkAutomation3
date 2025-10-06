import logging
import time

from pyats import aetest

from sergiu_oprea_proiect.lib.connectors.ssh_con import SshConnection

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class PingTest(aetest.Testcase):

    @aetest.test
    def ping(self, steps):
        with steps.start("Connect to pc2 and ping FTD"):
            conn = SshConnection('192.168.210.10', 22, 'osboxes', 'osboxes.org')
            conn.connect()
            log.info("Successfully connected to pc2")
            conn.create_shell()
            conn.send('ping -c 4 192.168.240.20\n')
            time.sleep(5)
            log.info(conn.shell.recv(10000).decode('utf-8'))
            conn.close()

if __name__ == '__main__':
    aetest.main()