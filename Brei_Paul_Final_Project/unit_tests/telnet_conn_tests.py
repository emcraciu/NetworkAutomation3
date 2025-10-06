import unittest
from unittest.mock import patch, AsyncMock, MagicMock, call

# Make sure to import your TelnetConnection class
# You may need to adjust the import path based on your project structure
from Brei_Paul_Final_Project.connectors.telnet_conn import TelnetConnection

class TestTelnetConnection(unittest.IsolatedAsyncioTestCase):

    # We use @patch to replace the real telnetlib3.open_connection with a mock
    @patch('telnetlib3.open_connection')
    async def test_connect_and_write(self, mock_open_connection):
        """Tests that the connection is established and write commands are sent correctly."""
        # --- Setup ---
        mock_reader = AsyncMock()
        mock_writer = MagicMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)

        # --- Actions ---
        conn = TelnetConnection('92.81.55.146', 5079)
        await conn.connect()
        conn.write("show version")

        # --- Assertions ---
        mock_open_connection.assert_called_once_with('92.81.55.146', 5079)
        self.assertEqual(conn.reader, mock_reader)
        self.assertEqual(conn.writer, mock_writer)

        conn.writer.write.assert_any_call("show version\r\n")

    @patch('telnetlib3.open_connection')
    async def test_enter_commands(self, mock_open_connection):
        """Test 3: Verifies that enter_commands correctly loops and sends commands."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)

        conn = TelnetConnection('92.81.55.146', 5079)
        await conn.connect()

        commands = ["conf t", "interface gi1", "ip address 1.1.1.1 255.255.255.255"]
        await conn.enter_commands(commands, "#")

        self.assertEqual(conn.writer.write.call_count, 4)

        self.assertEqual(conn.reader.readuntil.call_count, 3)

        conn.writer.write.assert_called_with("ip address 1.1.1.1 255.255.255.255\r\n")

    @patch('time.sleep')
    @patch('telnetlib3.open_connection')
    async def test_get_response(self, mock_open_connection, mock_sleep):
        """Test 4: Verifies get_response returns the correct data from the mock reader."""
        mock_reader = AsyncMock()
        mock_reader.read.return_value = "this is the command output"
        mock_open_connection.return_value = (mock_reader, AsyncMock())

        conn = TelnetConnection('92.81.55.146', 5079)
        await conn.connect()

        response = await conn.get_response("show ip route")

        self.assertEqual(response, "this is the command output")

        conn.reader.read.assert_awaited_once_with(1000)

        self.assertEqual(mock_sleep.call_count, 2)

    @patch('time.sleep')
    @patch('telnetlib3.open_connection')
    async def test_ping_end_device_success(self, mock_open_connection, mock_sleep):
        """Test 5: Verifies ping_end_device returns True on successful output."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()

        mock_reader.readuntil.side_effect = [
            b"some initial prompt\n",

            b"--- 192.168.250.100 ping statistics ---\n3 packets transmitted, 3 received, 0% packet loss, time 2003ms\n"
        ]

        mock_open_connection.return_value = (mock_reader, mock_writer)

        conn = TelnetConnection('92.81.55.146', 5106)
        await conn.connect()

        result = await conn.ping_end_device("192.168.250.100")

        self.assertTrue(result)

        self.assertEqual(mock_sleep.call_count, 2)

    @patch('time.sleep')
    @patch('telnetlib3.open_connection')
    async def test_initialize_csr(self, mock_open_connection, mock_sleep):
        """Test 6: Verifies initialize_csr correctly navigates the setup dialog."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()

        mock_reader.readuntil.side_effect = [
            b"Press RETURN to get started.",
            b"Would you like to enter the initial configuration dialog? [yes/no]:",
            b"Exiting initial configuration dialog."
        ]

        mock_reader.read.side_effect = [
            "Some banner text...",
            "Router>",
            "Router> "
        ]

        mock_open_connection.return_value = (mock_reader, mock_writer)

        conn = TelnetConnection('92.81.55.146', 5079)
        await conn.connect()

        final_output = await conn.initialize_csr()

        self.assertIn("Router>", final_output)
        mock_writer.write.assert_any_call('n\n')
        self.assertIn(call('\r\n'), mock_writer.write.call_args_list)

    @patch('time.sleep')
    @patch('telnetlib3.open_connection')
    async def test_enable_csr(self, mock_open_connection, mock_sleep):
        """Test 7: Verifies enable_csr correctly enters enable mode with a password."""
        mock_reader = AsyncMock()
        mock_writer = MagicMock()

        mock_reader.read.side_effect = [
            "CSR>",
            "CSR#\r\n"
        ]
        mock_reader.readuntil.side_effect = [
            b"Password:",
            b"CSR#\r\n"
        ]

        mock_open_connection.return_value = (mock_reader, mock_writer)

        conn = TelnetConnection('92.81.55.146', 5079)
        await conn.connect()

        final_output = await conn.enable_csr()

        self.assertIn("CSR#", final_output)
        mock_writer.write.assert_any_call('enable\n')
        mock_writer.write.assert_any_call('Cisco123!\n')

if __name__ == '__main__':
    unittest.main()