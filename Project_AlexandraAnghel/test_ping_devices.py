from Project_IM.ping_helper import run_pings

import unittest
import subprocess
import os
from ipaddress import ip_address, ip_network
from pyats.topology import loader



IGNORE_IPS = {
    "192.168.250.40",
}

IGNORE_NETWORKS = {
    ip_network("192.168.250.0/24"),
}

_env_ignore = os.getenv("PING_IGNORE", "").strip()
if _env_ignore:
    for token in [t.strip() for t in _env_ignore.split(",") if t.strip()]:
        try:
            IGNORE_IPS.add(str(ip_address(token)))
        except ValueError:
            try:
                IGNORE_NETWORKS.add(ip_network(token, strict=False))
            except ValueError:
                pass


class RealPingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load testbed and collect all destination IPs (minus cele ignorate)."""
        testbed_path = os.path.join(os.path.dirname(__file__), "testbed_ospf.yaml")
        cls.testbed = loader.load(testbed_path)

        cls.device = cls.testbed.devices["UbuntuServer"]
        cls.device_name = cls.device.name
        cls.os = cls.device.os or "linux"

        cls.topology_addresses = []

        print("\nCollected IPs from testbed:")

        for dev in cls.testbed.devices.values():
            if dev.name == cls.device_name:
                continue
            for intf in dev.interfaces.values():
                if hasattr(intf, "ipv4") and intf.ipv4:
                    ip = intf.ipv4.ip.compressed
                    addr = ip_address(ip)
                    if ip in IGNORE_IPS or any(addr in net for net in IGNORE_NETWORKS):
                        print(f" - {dev.name} -> {intf.name}: {ip}  ")
                        continue
                    cls.topology_addresses.append(ip)
                    print(f" - {dev.name} -> {intf.name}: {ip}")

        if not cls.topology_addresses:
            raise unittest.SkipTest("Niciun IP de test după filtrare; testul este sărit.")

    @staticmethod
    def real_execute(command: str, **kwargs) -> str:
        """Execută ping pe OS (Linux)."""
        if not command.strip():
            return ""
        if command.startswith("ping ") and " -c " not in command:
            command = command.replace("ping", "ping -c 4", 1)

        print(f"\n[INFO] Running ping command: {command}")

        try:
            process = subprocess.Popen(
                ["sh", "-c", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate(timeout=10)
            decoded_stdout = stdout.decode()
            decoded_stderr = stderr.decode()

            print("\n--- Raw Ping Output ---")
            print(decoded_stdout.strip())

            if process.returncode == 0:
                print(f"[PASS] Ping successful for {command.split()[-1]}")
                return decoded_stdout
            else:
                print(f"[FAIL] Ping failed for {command.split()[-1]}")
                print(decoded_stderr.strip())
                return decoded_stdout + decoded_stderr

        except subprocess.TimeoutExpired as e:
            process.kill()
            print(f"[TIMEOUT] Ping to {command.split()[-1]} timed out after 10s")
            return f"TimeoutExpired: {str(e)}"

    def real_read(self) -> str:
        return ""

    def test_ping_all_devices(self):
        """Runs real ping tests to all IPs collected from the testbed (fără cele ignorate)."""
        result, ping_details = run_pings(
            topology_addresses=self.topology_addresses,
            execute=self.real_execute,
            read=lambda: "",
            device_name=self.device_name,
            os=self.os
        )

        for ip, success in ping_details.items():
            with self.subTest(ip=ip):
                self.assertTrue(success, msg=f"Ping to {ip} failed")

        self.assertTrue(result, msg="One or more devices did not respond to ping")
