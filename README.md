# bitbrief-mcp-tickets

An MCP server for a support ticket queue, built step by step in the BIT / BRIEF
tutorial "Build an MCP Server in Python". Each chapter is a git tag:
`git checkout ch1` ... `ch6`.

Written against `mcp` 2.3.0 (the v2 SDK, where `FastMCP` became `MCPServer`).

```bash
py -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python client.py tools
python client.py call search_tickets '{"query": "refund"}'
```

The tickets and customers in `seed.sql` are fictional.
