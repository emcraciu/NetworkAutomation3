import unittest
from pyats.topology import loader


class TestDeviceInterfaces(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testbed = loader.load("testbed.yaml")
        cls.device_name = "IOU1"
        cls.device = cls.testbed.devices[cls.device_name]
        cls.device.connect(log_stdout=False)

    def test_has_up_interface(self):
        output = self.device.execute("show ip int brief")
        found = False
        for line in output.splitlines():
            if "up" in line.split()[-2:] and not line.startswith("Interface"):
                found = True
                break

        self.assertTrue(found, msg="No interface is UP/UP!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
