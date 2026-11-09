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

## Over HTTP, with Claude Code (chapters 4 and 6)

```bash
export TICKETS_READ_TOKEN=demo-read-7f3a TICKETS_WRITE_TOKEN=demo-write-91c2
python server.py --http                      # http://127.0.0.1:8000/mcp

TICKETS_TOKEN=$TICKETS_READ_TOKEN claude -p "Which open tickets are about refunds?" \
  --mcp-config claude-mcp.json --strict-mcp-config \
  --allowedTools "mcp__tickets__search_tickets mcp__tickets__get_ticket mcp__tickets__add_note"
```

The demo tokens are for local use only. In production, `auth.py` should verify
JWTs from your identity provider.
