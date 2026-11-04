# lab3_2_transport_stream.py
import asyncio
from mcp.client.stdio import stdio_client
from lab3_1_server_config import configure_remote_server

async def verify_transport_stream():
    print("--- Step 2: Opening Standard I/O Communication Streams ---")
    target_config = configure_remote_server()

    # Establish the transport line. This boots the server script in the background.
    async with stdio_client(target_config) as (read_stream, write_stream):
        print("Communication pipe successfully allocated.")
        print(f"Read stream object initialized: {type(read_stream)}")
        print(f"Write stream object initialized: {type(write_stream)}")

if __name__ == "__main__":
    asyncio.run(verify_transport_stream())