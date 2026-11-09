"""An MCP server for a support ticket queue."""

from typing import Literal

from pydantic import BaseModel

from mcp.server import MCPServer

import db

mcp = MCPServer("tickets", instructions="Search and read the support ticket queue.", log_level="WARNING")


class TicketSummary(BaseModel):
    id: int
    subject: str
    status: str
    priority: str
    created_at: str


@mcp.tool()
def search_tickets(query: str, status: Literal["open", "closed"] | None = None) -> list[TicketSummary]:
    """Search support tickets by a word or phrase in the subject or body.

    Returns at most ten tickets, oldest first. Filter by status to see only open or closed ones.
    """
    return [TicketSummary(**row) for row in db.search(query, status)]


if __name__ == "__main__":
    mcp.run()
