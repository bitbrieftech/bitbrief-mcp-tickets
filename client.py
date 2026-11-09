"""A command-line MCP client: list what a server offers, and call it.

    python client.py tools
    python client.py call search_tickets '{"query": "refund"}'
    python client.py resources
    python client.py read ticket://3
    python client.py --url http://127.0.0.1:8000/mcp --token-env TICKETS_READ_TOKEN tools
"""

import argparse
import asyncio
import json
import os
import sys

import httpx2
from mcp import Client, StdioServerParameters
from mcp.client.streamable_http import streamable_http_client

# Launch server.py as a subprocess and talk to it over stdin/stdout.
LOCAL = StdioServerParameters(command=sys.executable, args=["server.py"])


def connect(args: argparse.Namespace):
    """The local subprocess, or a remote server over HTTP with a bearer token."""
    if not args.url:
        return LOCAL
    token = os.environ.get(args.token_env)
    http = httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {token}"} if token else {},
        event_hooks={"response": [explain_refusal]},
    )
    return streamable_http_client(args.url, http_client=http)


async def explain_refusal(response: httpx2.Response) -> None:
    """The SDK reports a refused request as a generic error; keep the HTTP reason."""
    if response.status_code in (401, 403):
        raise PermissionError(f"HTTP {response.status_code}: {response.headers.get('www-authenticate', '')}")


async def main(args: argparse.Namespace) -> None:
    async with Client(connect(args)) as client:
        if args.command == "tools":
            for tool in (await client.list_tools()).tools:
                print(f"{tool.name}: {tool.description.splitlines()[0]}")
                if tool.annotations:
                    print("  hints:", tool.annotations.model_dump(exclude_none=True, by_alias=True))
                print(json.dumps(tool.input_schema["properties"], indent=2))
        elif args.command == "resources":
            for template in (await client.list_resource_templates()).resource_templates:
                print(f"{template.uri_template}: {template.description}")
        elif args.command == "read":
            for content in (await client.read_resource(args.uri)).contents:
                print(content.text)
        elif args.command == "call":
            result = await client.call_tool(args.name, json.loads(args.arguments))
            if result.is_error:
                print("error:", result.content[0].text)
            else:
                show(result.structured_content)


def show(content: dict) -> None:
    """One line per item, so a list of results reads as a list."""
    items = content.get("result", content)
    for item in items if isinstance(items, list) else [items]:
        print(json.dumps(item))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="an HTTP server, e.g. http://127.0.0.1:8000/mcp")
    parser.add_argument("--token-env", default="TICKETS_TOKEN", help="env var holding the bearer token")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("tools")
    sub.add_parser("resources")
    sub.add_parser("read").add_argument("uri")
    call = sub.add_parser("call")
    call.add_argument("name")
    call.add_argument("arguments", nargs="?", default="{}")
    try:
        asyncio.run(main(parser.parse_args()))
    except Exception as exc:
        # A failed connection arrives wrapped in exception groups; show the cause.
        while isinstance(exc, BaseExceptionGroup):
            exc = exc.exceptions[0]
        sys.exit(f"error: {exc} {getattr(exc, 'data', None) or ''}".rstrip())
