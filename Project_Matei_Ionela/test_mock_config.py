import unittest
from unittest.mock import MagicMock
from Project_IM.device_config import set_device_hostname, get_device_prompt

class TestDeviceConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_device = MagicMock()
        self.mock_device.name = "Router"

    def test_set_hostname_with_mock(self) -> None:
        target_hostname = "Router1"
        result = set_device_hostname(self.mock_device)
        self.assertTrue(result)
        self.mock_device.configure.assert_called_once_with(f"hostname {target_hostname}")

    def test_get_device_prompt(self) -> None:
        prompt = get_device_prompt(self.mock_device)
        self.assertEqual(prompt, "Router#")

if __name__ == '__main__':
    unittest.main(verbosity=2)