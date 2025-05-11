import asyncio
import logging
from typing import Any, Dict
from agents.mcp import MCPServerStdio


class MCPServerManager:
    def __init__(self, mcp_server_config: Dict[str, Any], timeout: int = 60):
        self._mcp_servers = [
            (
                server_name,
                MCPServerStdio(
                    params={
                        "command": server_config.get("command"),
                        "args": server_config.get("args"),
                        "env": server_config.get("env"),
                    },
                    client_session_timeout_seconds=timeout,
                ),
            )
            for server_name, server_config in mcp_server_config.get(
                "servers", {}
            ).items()
        ]

    async def start(self):
        if not self._mcp_servers:
            raise ValueError("No MCP servers configured to start.")

        logging.info(f"Starting {len(self._mcp_servers)} MCP servers...")
        for name, server in self._mcp_servers:
            logging.info(f"  Starting MCP server: {name}")
            await server.connect()
        logging.info(
            f"{len(self._mcp_servers)} MCP servers started. [{
                ', '.join([name for name, _ in self._mcp_servers])
            }]"
        )

    def get(self):
        return [server for _, server in self._mcp_servers]

    async def stop(self):
        if not self._mcp_servers:
            raise ValueError("No MCP servers configured to stop.")

        logging.info(f"Stopping {len(self._mcp_servers)} MCP servers...")

        for name, server in self._mcp_servers:
            logging.info(f"  Stopping MCP server: {name}")
            await server.cleanup()

        logging.info(f"{len(self._mcp_servers)} MCP servers stopped.")
