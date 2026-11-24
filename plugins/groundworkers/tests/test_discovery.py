"""Exercise wheel entry-point discovery through a stock Groundworkers MCP host."""

import os
import sys
import unittest
from pathlib import Path

from examples.run_demo import TOOLS
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class DiscoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_installed_host_discovers_all_hosted_tools_without_network(self):
        config = Path(__file__).resolve().parents[1] / "examples" / "demo.toml"
        env = {"OMOPHUB_API_KEY": "offline-test", "OMOPHUB_VOCAB_RELEASE": "2026.2"}
        if "PYSTOW_HOME" in os.environ:
            env["PYSTOW_HOME"] = os.environ["PYSTOW_HOME"]
        host = StdioServerParameters(
            command=str(Path(sys.executable).with_name("groundworkers")),
            args=["--config-path", str(config), "--transport", "stdio"],
            env=env,
        )
        async with (
            stdio_client(host) as (read, write),
            ClientSession(read, write) as session,
        ):
            await session.initialize()
            available = {tool.name for tool in (await session.list_tools()).tools}
            self.assertEqual(
                {name for name in available if name.startswith("omophub_")},
                {f"omophub_{name}" for name in TOOLS},
            )
