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

        # CORRECTED ASSERTION:
        # Use assert_any_call to check if our specific call exists among all calls.
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

        # Check that write was called for each command
        # CORRECTED: The total call count is 4 (1 from connect + 3 from enter_commands)
        self.assertEqual(conn.writer.write.call_count, 4)

        # Check that we awaited a response for each command (this one is correct)
        self.assertEqual(conn.reader.readuntil.call_count, 3)

        # Check the content of the last call to write (this one is also correct)
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

        # Assert that the function returned the value we configured in our mock
        self.assertEqual(response, "this is the command output")

        # Assert that the read method was called with a positional argument.
        conn.reader.read.assert_awaited_once_with(1000)

        # Now you can also assert that time.sleep was called
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('time.sleep')
    @patch('telnetlib3.open_connection')
    async def test_ping_end_device_success(self, mock_open_connection, mock_sleep):
        """Test 5: Verifies ping_end_device returns True on successful output."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock() # The writer needs to be an AsyncMock for the connect() method

        # CORRECTED: We now mock .readuntil() because that's what the method uses.
        # We use side_effect to simulate the sequence of responses.
        mock_reader.readuntil.side_effect = [
            # This first response is for the readuntil() call BEFORE the while loop.
            # It does NOT contain "packet loss, time", so the loop will run once.
            b"some initial prompt\n",

            # This second response is for the readuntil() call INSIDE the while loop.
            # It contains the success text, which will break the loop.
            b"--- 192.168.250.100 ping statistics ---\n3 packets transmitted, 3 received, 0% packet loss, time 2003ms\n"
        ]

        mock_open_connection.return_value = (mock_reader, mock_writer)

        conn = TelnetConnection('92.81.55.146', 5106)
        await conn.connect()

        # Call the method we are testing
        result = await conn.ping_end_device("192.168.250.100")

        # This assertion is now valid because the method will run correctly.
        self.assertTrue(result)

        # Let's verify the sleep calls.
        # 1 call from connect(), 1 from before the loop, and 1 from inside the loop.
        # Your method has one sleep(1) and the loop runs once, calling sleep(2).
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('time.sleep')
    @patch('telnetlib3.open_connection')
    async def test_initialize_csr(self, mock_open_connection, mock_sleep):
        """Test 6: Verifies initialize_csr correctly navigates the setup dialog."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()

        # This mock MUST return BYTES because the readuntil() method calls .decode()
        mock_reader.readuntil.side_effect = [
            b"Press RETURN to get started.",
            b"Would you like to enter the initial configuration dialog? [yes/no]:",
            b"Exiting initial configuration dialog."
        ]

        # CORRECTED: This mock now returns STRINGS to prevent the TypeError
        # in the 'while "Router>" not in out:' comparison.
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

        # CORRECTED: This mock now returns STRINGS
        mock_reader.read.side_effect = [
            "CSR>",
            "CSR#\r\n"
        ]
        # This mock MUST return BYTES
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