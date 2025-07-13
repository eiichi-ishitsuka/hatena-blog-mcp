"""Hatena Blog MCP Server."""

import asyncio
import os
import sys
from typing import Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent
)
from pydantic import AnyUrl

from .client import HatenaBlogClient, BlogEntry


app = Server("hatena-blog-mcp")


def get_client() -> HatenaBlogClient:
    """Get configured Hatena Blog client."""
    hatena_id = os.getenv("HATENA_ID")
    api_key = os.getenv("HATENA_API_KEY")
    blog_id = os.getenv("HATENA_BLOG_ID")
    
    if not all([hatena_id, api_key, blog_id]):
        raise ValueError(
            "Missing required environment variables: HATENA_ID, HATENA_API_KEY, HATENA_BLOG_ID"
        )
    
    return HatenaBlogClient(hatena_id, api_key, blog_id)


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_blog_entries",
            description="Get blog entries from Hatena Blog",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Page number (default: 1)",
                        "minimum": 1,
                        "default": 1
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of entries to return (default: 10)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10
                    }
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_blog_entry",
            description="Get a specific blog entry by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "Blog entry ID"
                    }
                },
                "required": ["entry_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="search_blog_entries",
            description="Search blog entries by title or content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_blog_categories",
            description="Get available blog categories",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="create_blog_entry",
            description="Create a new blog entry as draft",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Entry title"
                    },
                    "content": {
                        "type": "string",
                        "description": "Entry content (HTML or plain text)"
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of category names (optional)",
                        "default": []
                    },
                    "is_draft": {
                        "type": "boolean",
                        "description": "Whether to create as draft (default: true)",
                        "default": True
                    }
                },
                "required": ["title", "content"],
                "additionalProperties": False
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}
    
    try:
        client = get_client()
        
        if name == "get_blog_entries":
            page = arguments.get("page", 1)
            limit = arguments.get("limit", 10)
            
            entries = client.get_entries(page)
            entries = entries[:limit]  # Limit results
            
            if not entries:
                return [TextContent(type="text", text="No blog entries found.")]
            
            result = f"Found {len(entries)} blog entries (page {page}):\n\n"
            for entry in entries:
                result += format_entry_summary(entry)
                result += "\n---\n\n"
            
            return [TextContent(type="text", text=result.strip())]
        
        elif name == "get_blog_entry":
            entry_id = arguments["entry_id"]
            
            entry = client.get_entry(entry_id)
            if not entry:
                return [TextContent(type="text", text=f"Blog entry '{entry_id}' not found.")]
            
            result = format_entry_detail(entry)
            return [TextContent(type="text", text=result)]
        
        elif name == "search_blog_entries":
            query = arguments["query"]
            max_results = arguments.get("max_results", 10)
            
            entries = client.search_entries(query, max_results)
            
            if not entries:
                return [TextContent(type="text", text=f"No blog entries found matching '{query}'.")]
            
            result = f"Found {len(entries)} blog entries matching '{query}':\n\n"
            for entry in entries:
                result += format_entry_summary(entry)
                result += "\n---\n\n"
            
            return [TextContent(type="text", text=result.strip())]
        
        elif name == "get_blog_categories":
            categories = client.get_categories()
            
            if not categories:
                return [TextContent(type="text", text="No categories found.")]
            
            result = f"Available categories ({len(categories)}):\n\n"
            for category in sorted(categories):
                result += f"- {category}\n"
            
            return [TextContent(type="text", text=result.strip())]
        
        elif name == "create_blog_entry":
            title = arguments["title"]
            content = arguments["content"]
            categories = arguments.get("categories", [])
            is_draft = arguments.get("is_draft", True)
            
            entry = client.create_entry(title, content, categories, is_draft)
            
            status = "📝 Draft" if entry.is_draft else "✅ Published"
            result = f"Successfully created blog entry: {status}\n\n"
            result += format_entry_detail(entry)
            
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def format_entry_summary(entry: BlogEntry) -> str:
    """Format blog entry summary."""
    status = "📝 Draft" if entry.is_draft else "✅ Published"
    categories_str = ", ".join(entry.categories) if entry.categories else "No categories"
    
    return f"""**{entry.title}** {status}
ID: {entry.id}
Author: {entry.author}
Published: {entry.published.strftime('%Y-%m-%d %H:%M')}
Categories: {categories_str}

{entry.content[:200]}{"..." if len(entry.content) > 200 else ""}"""


def format_entry_detail(entry: BlogEntry) -> str:
    """Format detailed blog entry."""
    status = "📝 Draft" if entry.is_draft else "✅ Published"
    categories_str = ", ".join(entry.categories) if entry.categories else "No categories"
    
    return f"""# {entry.title} {status}

**ID:** {entry.id}
**Author:** {entry.author}
**Published:** {entry.published.strftime('%Y-%m-%d %H:%M:%S')}
**Updated:** {entry.updated.strftime('%Y-%m-%d %H:%M:%S')}
**Categories:** {categories_str}

## Content

{entry.content}"""


@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri=AnyUrl("hatena://blog/entries"),
            name="Blog Entries",
            description="All blog entries from Hatena Blog",
            mimeType="text/plain"
        ),
        Resource(
            uri=AnyUrl("hatena://blog/categories"),
            name="Blog Categories",
            description="Available blog categories",
            mimeType="text/plain"
        )
    ]


@app.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Get resource content."""
    try:
        client = get_client()
        
        if str(uri) == "hatena://blog/entries":
            entries = client.get_entries(1)
            result = f"# Blog Entries\n\n"
            for entry in entries:
                result += format_entry_summary(entry)
                result += "\n\n---\n\n"
            return result.strip()
        
        elif str(uri) == "hatena://blog/categories":
            categories = client.get_categories()
            result = f"# Blog Categories\n\n"
            for category in sorted(categories):
                result += f"- {category}\n"
            return result.strip()
        
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    except Exception as e:
        return f"Error: {str(e)}"


async def main():
    """Main entry point."""
    # Run the server using stdio transport
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="hatena-blog-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def cli_main():
    """CLI entry point."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down server...", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    cli_main()