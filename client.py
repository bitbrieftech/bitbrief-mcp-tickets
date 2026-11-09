"""A command-line MCP client: list what a server offers, and call it.

    python client.py tools
    python client.py call search_tickets '{"query": "refund"}'
    python client.py resources
    python client.py read ticket://3
"""

import argparse
import asyncio
import json
import sys

from mcp import Client, StdioServerParameters

# Launch server.py as a subprocess and talk to it over stdin/stdout.
LOCAL = StdioServerParameters(command=sys.executable, args=["server.py"])


async def main(args: argparse.Namespace) -> None:
    async with Client(LOCAL) as client:
        if args.command == "tools":
            for tool in (await client.list_tools()).tools:
                print(f"{tool.name}: {tool.description.splitlines()[0]}")
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
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("tools")
    sub.add_parser("resources")
    sub.add_parser("read").add_argument("uri")
    call = sub.add_parser("call")
    call.add_argument("name")
    call.add_argument("arguments", nargs="?", default="{}")
    asyncio.run(main(parser.parse_args()))
