import unittest
from pathlib import Path
from pyats.topology import loader

class TestOSPFOnIOSv(unittest.TestCase):
    """Verify that IOU1 and CSR are OSPF neighbors of IOSv (by Router ID)."""

    @classmethod
    def setUpClass(cls):
        # Load the testbed
        tb_path = Path(__file__).resolve().parent / "testbed_ospf.yaml"
        cls.testbed = loader.load(str(tb_path))
        cls.device = cls.testbed.devices["IOSv"]

    def test_ospf_neighbors_iosv(self):
        """Verify that router IDs 1.1.1.1 and 3.3.3.3 appear in OSPF neighbors."""
        self.device.connect(via="cli", log_stdout=False)

        print(f"\n=== Connected to {self.device.name} ===")
        self.device.execute("end")  # exit config mode if needed
        self.device.execute("\r")   # refresh prompt
        output = self.device.execute("show ip ospf neighbor")
        print(output)

        # Put the real Router IDs here (based on your device output)
        expected_router_ids = ["1.1.1.1", "3.3.3.3"]

        # Extract neighbors that are in FULL state
        found_neighbors = [line for line in output.splitlines() if "FULL" in line]

        if found_neighbors:
            print("\nActive OSPF neighbors (FULL state):")
            for n in found_neighbors:
                print("-", n)
        else:
            print("[WARN] No active OSPF neighbors (FULL state) found.")

        # Check that each Router ID appears in the output
        for rid in expected_router_ids:
            with self.subTest(router_id=rid):
                self.assertIn(
                    rid, output,
                    msg=f"Router ID {rid} does NOT appear in IOSv's OSPF neighbors!"
                )

        self.device.disconnect()
        print(f"Verification finished for {self.device.name}.\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
