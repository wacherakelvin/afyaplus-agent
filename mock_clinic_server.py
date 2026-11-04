# mock_clinic_server.py
import asyncio
from mcp.server import Server
from mcp.server.stdio import start_stdio_server
from mcp.types import Tool, TextContent

# Initialize a named backend server space container
server_app = Server("afyaplus-mock-clinic-server")

@server_app.list_tools()
async def handle_tool_listing():
    """Exposes available capabilities to any connecting MCP client dynamically."""
    return [
        Tool(
            name="get_market_trends",
            description="Retrieves clinic performance metrics for East Africa.",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "Country name (e.g., 'Kenya')"}
                },
                "required": ["region"]
            }
        )
    ]

@server_app.call_tool()
async def handle_tool_execution(name: str, arguments: dict):
    """Processes execution instructions sent down from the client side."""
    if name == "get_market_trends":
        target_region = arguments.get("region", "Unknown")
        return [
            TextContent(
                type="text",
                text=f"Verified Record for [{target_region}]: Nairobi claims velocity is up 14%."
            )
        ]
    raise ValueError(f"Requested tool '{name}' is not supported on this node.")

async def launch_server():
    # Keep the server running and listening over the standard input/output lines
    async with start_stdio_server() as (read_stream, write_stream):
        await server_app.run(read_stream, write_stream, server_app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(launch_server())