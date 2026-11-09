"""An MCP server for a support ticket queue."""

from typing import Literal

from pydantic import BaseModel

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

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


class Note(BaseModel):
    body: str
    created_at: str


class Ticket(TicketSummary):
    customer: str
    body: str
    notes: list[Note]


@mcp.tool()
def get_ticket(ticket_id: int) -> Ticket:
    """Read one ticket in full: the customer's message and every note on it."""
    ticket = db.get(ticket_id)
    if ticket is None:
        # A ToolError's message goes back to the model, so it can correct itself.
        raise ToolError(f"No ticket with id {ticket_id}. Use search_tickets to find one.")
    return Ticket(**ticket)


@mcp.resource("ticket://{ticket_id}", mime_type="application/json")
def ticket_resource(ticket_id: int) -> str:
    """A ticket as a document the user can attach to a conversation."""
    ticket = db.get(ticket_id)
    if ticket is None:
        raise ValueError(f"No ticket with id {ticket_id}")
    return Ticket(**ticket).model_dump_json(indent=2)


if __name__ == "__main__":
    mcp.run()
