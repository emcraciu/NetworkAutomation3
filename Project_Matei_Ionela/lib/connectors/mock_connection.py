import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from queue import Queue

from Project_Matei_Ionela.lib.connectors.telnet_connection import TelnetConnection



class TestTelnetConnection(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.host = "127.0.0.1"
        self.port = 2323

        self.mock_reader = AsyncMock()
        self.mock_writer = MagicMock()

        patcher = patch(
            "Project_IM.lib.connectors.telnet_connection.telnetlib3.open_connection",
            new=AsyncMock(return_value=(self.mock_reader, self.mock_writer))
        )
        self.addCleanup(patcher.stop)
        self.mock_open_conn = patcher.start()

        self.conn = TelnetConnection(self.host, self.port)

    async def test_connect_calls_telnetlib3(self):
        await self.conn.connect()
        self.mock_open_conn.assert_awaited_once_with(self.host, self.port)
        self.assertEqual(self.conn.reader, self.mock_reader)
        self.assertEqual(self.conn.writer, self.mock_writer)

    async def test_write_sends_data(self):
        self.conn.writer = MagicMock()
        self.conn.write("show ip int brief")
        self.conn.writer.write.assert_called_once_with("show ip int brief\r\n")

    async def test_readuntil_returns_decoded_data(self):
        self.conn.reader = AsyncMock()
        self.conn.reader.readuntil.return_value = b"Router#"
        result = await self.conn.readuntil("#")
        self.conn.reader.readuntil.assert_awaited_once_with(b"#")
        self.assertEqual(result, "Router#")

    async def test_execute_commends_sends_multiple_cmds(self):
        self.conn.write = MagicMock()
        self.conn.readuntil = AsyncMock(return_value="Router#")
        cmds = ["show ver", "show run"]

        await self.conn.execute_commends(cmds, prompt="#")

        self.assertEqual(self.conn.write.call_count, 2)
        self.conn.readuntil.assert_awaited_with("#")

    async def test_configure_puts_result_in_queue(self):
        self.conn.read = AsyncMock(return_value="Router#")
        self.conn.readuntil = AsyncMock(return_value="Router(config)#")
        self.conn.write = MagicMock()
        q = Queue()

        await self.conn.configure(completed=q)

        self.assertFalse(q.empty())
        item = q.get()
        self.assertEqual(item, {"Router": "192.168.200.3"})
        self.conn.write.assert_any_call("conf t")

    async def test_configure_handles_iou_case(self):
        self.conn.read = AsyncMock(return_value="IOU1#")
        self.conn.readuntil = AsyncMock(return_value="IOU1(config)#")
        self.conn.write = MagicMock()
        q = Queue()

        await self.conn.configure(completed=q)
        self.assertTrue(q.empty())
        self.conn.write.assert_called_with("conf t")


if __name__ == "__main__":
    unittest.main(verbosity=2)