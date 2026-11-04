# challenge28_mcp_triage_tool.py
# Run: python challenge28_mcp_triage_tool.py
from mcp.server.fastmcp import FastMCP

server = FastMCP("afyaplus-clinic")

@server.tool()
def triage_lookup(symptom: str) -> str:
    """Returns an urgency level (EMERGENCY, URGENT, or ROUTINE) for a given patient symptom."""
    table = {
        "chest pain": "EMERGENCY",
        "difficulty breathing": "EMERGENCY",
        "fever": "URGENT",
        "headache": "ROUTINE",
    }
    return table.get(symptom.lower(), "ROUTINE")

if __name__ == "__main__":
    # FastMCP serves the registered tools over stdio for any MCP client to discover.
    server.run()