from pyats import aetest, topology

SERVER_IP = "192.168.200.1"
class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self, steps):
        tb = topology.loader.load("ubuntu_docker2_testbed.yaml")
        self.parent.parameters.update(tb=tb)

class ConfigureUbuntu(aetest.Testcase):
    @aetest.setup
    def connect(self, steps):
        tb = self.parent.parameters.get("tb")
        self.dev = tb.devices.UbuntuDocker1
        self.dev.connect(via="cli", log_stdout=True)

    @aetest.test
    def set_ip_address(self, steps):
        cmds = [
            "ip addr flush dev eth0",
            "ip addr add 192.168.250.2/24 dev eth0",
            "ip link set eth0 up",
            "ip route add default via 192.168.250.40"
        ]
        for cmd in cmds:
            with steps.start(f"Run: {cmd}"):
                output = self.dev.execute(cmd, timeout=10)
                print(output)

    @aetest.test
    def run_iperf_client(self, steps):

        cmd = f"iperf3 -c {SERVER_IP} -t 10"
        with steps.start(f"Run iperf client to {SERVER_IP}"):
            output = self.dev.execute(cmd, timeout=30)
            print("\n===== iperf3 Client Output =====")
            print(output)
            print("================================")

            # Check if iperf was successful
            if "Interval" in output and "sender" in output and "receiver" in output:
                self.dev.log.info("✅ iPerf3 client ran successfully! ")
            else:
                self.dev.log.error("❌ iPerf3 test failed or did not run properly. ")

if __name__ == "__main__":
    aetest.main()
