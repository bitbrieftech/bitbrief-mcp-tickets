"""An MCP server for a support ticket queue."""

import sys
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from mcp.server import MCPServer
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

import auth
import db

mcp = MCPServer(
    "tickets",
    instructions="Search, read and annotate the support ticket queue.",
    log_level="WARNING",
    # Over HTTP, every request needs a bearer token with at least tickets:read.
    token_verifier=auth.DemoTokenVerifier(),
    auth=AuthSettings(
        issuer_url="https://auth.example.com",  # your identity provider
        resource_server_url="http://127.0.0.1:8000/mcp",
        required_scopes=[auth.READ],
        validate_token_resource=False,  # the demo verifier checks tokens itself
    ),
)

# Hints for the client: these two only read, so a host can run them without asking.
READ_ONLY = ToolAnnotations(read_only_hint=True)


class TicketSummary(BaseModel):
    id: int
    subject: str
    status: str
    priority: str
    created_at: str


@mcp.tool(annotations=READ_ONLY)
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


@mcp.tool(annotations=READ_ONLY)
def get_ticket(ticket_id: int) -> Ticket:
    """Read one ticket in full: the customer's message and every note on it."""
    ticket = db.get(ticket_id)
    if ticket is None:
        # A ToolError's message goes back to the model, so it can correct itself.
        raise ToolError(f"No ticket with id {ticket_id}. Use search_tickets to find one.")
    return Ticket(**ticket)


@mcp.tool(annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False))
def add_note(ticket_id: int, note: Annotated[str, Field(min_length=1, max_length=500)]) -> Ticket:
    """Add an internal note to an open ticket. The customer never sees notes.

    Returns the ticket with the new note, so you can confirm what was saved.
    """
    token = get_access_token()
    # Over HTTP every call carries a token. Locally (stdio, tests) there is none.
    if token is not None and auth.WRITE not in token.scopes:
        raise ToolError("This token can read tickets but not change them: it lacks tickets:write.")
    ticket = db.get(ticket_id)
    if ticket is None:
        raise ToolError(f"No ticket with id {ticket_id}. Use search_tickets to find one.")
    if ticket["status"] != "open":
        raise ToolError(f"Ticket {ticket_id} is closed. Notes can only be added to open tickets.")
    db.add_note(ticket_id, note.strip(), date.today().isoformat())
    return Ticket(**db.get(ticket_id))


@mcp.resource("ticket://{ticket_id}", mime_type="application/json")
def ticket_resource(ticket_id: int) -> str:
    """A ticket as a document the user can attach to a conversation."""
    ticket = db.get(ticket_id)
    if ticket is None:
        raise ValueError(f"No ticket with id {ticket_id}")
    return Ticket(**ticket).model_dump_json(indent=2)


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run("streamable-http", host="127.0.0.1", port=8000)
    else:
        mcp.run()
