"""The server's contract, tested in memory: no subprocess, no port, no model."""

import pytest

from mcp import Client

import auth
from server import mcp

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    async with Client(mcp) as c:
        yield c


async def test_offers_three_tools(client):
    tools = {tool.name: tool for tool in (await client.list_tools()).tools}
    assert set(tools) == {"search_tickets", "get_ticket", "add_note"}
    assert tools["search_tickets"].annotations.read_only_hint is True
    assert tools["add_note"].annotations.read_only_hint is False


async def test_search_filters_by_status(client):
    result = await client.call_tool("search_tickets", {"query": "refund", "status": "open"})
    tickets = result.structured_content["result"]
    assert [t["id"] for t in tickets] == [1, 4, 7, 12]
    assert all(t["status"] == "open" for t in tickets)


async def test_unknown_ticket_is_an_error_the_model_can_read(client):
    result = await client.call_tool("get_ticket", {"ticket_id": 99})
    assert result.is_error
    assert "Use search_tickets" in result.content[0].text


async def test_notes_only_on_open_tickets(client):
    closed = await client.call_tool("add_note", {"ticket_id": 5, "note": "Address updated."})
    assert closed.is_error and "closed" in closed.content[0].text

    saved = await client.call_tool("add_note", {"ticket_id": 3, "note": "  Exchange label sent.  "})
    assert saved.structured_content["notes"][-1]["body"] == "Exchange label sent."


async def test_empty_note_is_rejected_before_our_code_runs(client):
    result = await client.call_tool("add_note", {"ticket_id": 3, "note": ""})
    assert result.is_error and "at least 1 character" in result.content[0].text


async def test_tokens_grant_only_their_scopes(monkeypatch):
    monkeypatch.setenv("TICKETS_READ_TOKEN", "read-secret")
    monkeypatch.setenv("TICKETS_WRITE_TOKEN", "write-secret")
    verifier = auth.DemoTokenVerifier()
    assert (await verifier.verify_token("read-secret")).scopes == [auth.READ]
    assert auth.WRITE in (await verifier.verify_token("write-secret")).scopes
    assert await verifier.verify_token("guess") is None
