# lab3_3_client_session.py
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from lab3_1_server_config import configure_remote_server

async def run_protocol_handshake():
    print("--- Step 3: Executing Protocol Handshake (Initialize) ---")
    target_config = configure_remote_server()

    async with stdio_client(target_config) as (read_stream, write_stream):
        # Open a structural protocol session over the active raw text streams
        async with ClientSession(read_stream, write_stream) as session:
            # Perform the critical protocol greeting handshake
            await session.initialize()
            print("Handshake Completed! Client and Server have successfully negotiated feature sync.")
            return True

if __name__ == "__main__":
    asyncio.run(run_protocol_handshake())