# lab3_4_tool_discovery.py
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from lab3_1_server_config import configure_remote_server

async def discover_server_capabilities():
    print("--- Step 4: Running Dynamic Capability Discovery ---")
    target_config = configure_remote_server()

    async with stdio_client(target_config) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Query the server for its live dictionary of tools
            discovered_assets = await session.list_tools()

            print(f"Discovered {len(discovered_assets.tools)} operational tool layouts on server node:")
            for tool in discovered_assets.tools:
                print(f" -> Tool Identifier: {tool.name}")
                print(f"    Purpose: {tool.description}")
    return discovered_assets

if __name__ == "__main__":
    asyncio.run(discover_server_capabilities())