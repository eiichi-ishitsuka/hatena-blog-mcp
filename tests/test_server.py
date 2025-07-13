"""Tests for Hatena Blog MCP server."""

import asyncio
import os
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from mcp.types import TextContent
from pydantic import AnyUrl

from hatena_blog_mcp.server import (
    app,
    get_client,
    handle_list_tools,
    handle_call_tool,
    handle_list_resources,
    handle_read_resource,
    format_entry_summary,
    format_entry_detail,
    main,
    cli_main
)
import hatena_blog_mcp.server
from hatena_blog_mcp.client import BlogEntry


class TestGetClient:
    """Test cases for get_client function."""
    
    def test_get_client_success(self):
        """Test successful client creation."""
        with patch.dict(os.environ, {
            'HATENA_ID': 'test_user',
            'HATENA_API_KEY': 'test_key',
            'HATENA_BLOG_ID': 'test_blog'
        }):
            client = get_client()
            assert client.hatena_id == 'test_user'
            assert client.api_key == 'test_key'
            assert client.blog_id == 'test_blog'
    
    def test_get_client_missing_env_vars(self):
        """Test client creation with missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_client()
            assert "Missing required environment variables" in str(exc_info.value)


class TestHandlers:
    """Test cases for MCP handlers."""
    
    @pytest.mark.asyncio
    async def test_handle_list_tools(self):
        """Test listing available tools."""
        tools = await handle_list_tools()
        
        assert len(tools) == 5
        tool_names = [tool.name for tool in tools]
        assert "get_blog_entries" in tool_names
        assert "get_blog_entry" in tool_names
        assert "search_blog_entries" in tool_names
        assert "get_blog_categories" in tool_names
        assert "create_blog_entry" in tool_names
    
    @pytest.mark.asyncio
    async def test_handle_list_resources(self):
        """Test listing available resources."""
        resources = await handle_list_resources()
        
        assert len(resources) == 2
        resource_uris = [str(resource.uri) for resource in resources]
        assert "hatena://blog/entries" in resource_uris
        assert "hatena://blog/categories" in resource_uris
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_get_blog_entries(self, mock_get_client):
        """Test get_blog_entries tool call."""
        mock_client = Mock()
        mock_entry = BlogEntry(
            id="123",
            title="Test Entry",
            content="Test content",
            published=datetime(2024, 1, 1, 10, 0, 0),
            updated=datetime(2024, 1, 1, 10, 0, 0),
            author="test_user",
            categories=["test"]
        )
        mock_client.get_entries.return_value = [mock_entry]
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("get_blog_entries", {"page": 1, "limit": 10})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Test Entry" in result[0].text
        assert "test_user" in result[0].text
        mock_client.get_entries.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_get_blog_entries_no_results(self, mock_get_client):
        """Test get_blog_entries with no results."""
        mock_client = Mock()
        mock_client.get_entries.return_value = []
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("get_blog_entries", {})
        
        assert len(result) == 1
        assert "No blog entries found" in result[0].text
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_get_blog_entry(self, mock_get_client):
        """Test get_blog_entry tool call."""
        mock_client = Mock()
        mock_entry = BlogEntry(
            id="123",
            title="Test Entry",
            content="Test content",
            published=datetime(2024, 1, 1, 10, 0, 0),
            updated=datetime(2024, 1, 1, 10, 0, 0),
            author="test_user"
        )
        mock_client.get_entry.return_value = mock_entry
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("get_blog_entry", {"entry_id": "123"})
        
        assert len(result) == 1
        assert "Test Entry" in result[0].text
        mock_client.get_entry.assert_called_once_with("123")
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_get_blog_entry_not_found(self, mock_get_client):
        """Test get_blog_entry with non-existent entry."""
        mock_client = Mock()
        mock_client.get_entry.return_value = None
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("get_blog_entry", {"entry_id": "nonexistent"})
        
        assert len(result) == 1
        assert "not found" in result[0].text
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_search_blog_entries(self, mock_get_client):
        """Test search_blog_entries tool call."""
        mock_client = Mock()
        mock_entry = BlogEntry(
            id="123",
            title="Python Tutorial",
            content="Learn Python",
            published=datetime(2024, 1, 1, 10, 0, 0),
            updated=datetime(2024, 1, 1, 10, 0, 0),
            author="test_user"
        )
        mock_client.search_entries.return_value = [mock_entry]
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("search_blog_entries", {"query": "Python", "max_results": 5})
        
        assert len(result) == 1
        assert "Python Tutorial" in result[0].text
        mock_client.search_entries.assert_called_once_with("Python", 5)
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_search_blog_entries_no_results(self, mock_get_client):
        """Test search_blog_entries with no results."""
        mock_client = Mock()
        mock_client.search_entries.return_value = []
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("search_blog_entries", {"query": "NonExistent"})
        
        assert len(result) == 1
        assert "No blog entries found matching" in result[0].text
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_get_blog_categories(self, mock_get_client):
        """Test get_blog_categories tool call."""
        mock_client = Mock()
        mock_client.get_categories.return_value = ["Python", "Java"]
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("get_blog_categories", {})
        
        assert len(result) == 1
        assert "Python" in result[0].text
        assert "Java" in result[0].text
        mock_client.get_categories.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_get_blog_categories_no_results(self, mock_get_client):
        """Test get_blog_categories with no results."""
        mock_client = Mock()
        mock_client.get_categories.return_value = []
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("get_blog_categories", {})
        
        assert len(result) == 1
        assert "No categories found" in result[0].text
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_unknown_tool(self, mock_get_client):
        """Test unknown tool call."""
        mock_get_client.return_value = Mock()
        
        result = await handle_call_tool("unknown_tool", {})
        
        assert len(result) == 1
        assert "Unknown tool" in result[0].text
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_with_exception(self, mock_get_client):
        """Test tool call with exception."""
        mock_get_client.side_effect = Exception("Test error")
        
        result = await handle_call_tool("get_blog_entries", {})
        
        assert len(result) == 1
        assert "Error: Test error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_none_arguments(self):
        """Test tool call with None arguments."""
        with patch('hatena_blog_mcp.server.get_client') as mock_get_client:
            mock_client = Mock()
            mock_client.get_entries.return_value = []
            mock_get_client.return_value = mock_client
            
            result = await handle_call_tool("get_blog_entries", None)
            
            assert len(result) == 1
            assert "No blog entries found" in result[0].text
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_read_resource_entries(self, mock_get_client):
        """Test reading entries resource."""
        mock_client = Mock()
        mock_entry = BlogEntry(
            id="123",
            title="Test Entry",
            content="Test content",
            published=datetime(2024, 1, 1, 10, 0, 0),
            updated=datetime(2024, 1, 1, 10, 0, 0),
            author="test_user"
        )
        mock_client.get_entries.return_value = [mock_entry]
        mock_get_client.return_value = mock_client
        
        result = await handle_read_resource(AnyUrl("hatena://blog/entries"))
        
        assert "# Blog Entries" in result
        assert "Test Entry" in result
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_read_resource_categories(self, mock_get_client):
        """Test reading categories resource."""
        mock_client = Mock()
        mock_client.get_categories.return_value = ["Python", "Java"]
        mock_get_client.return_value = mock_client
        
        result = await handle_read_resource(AnyUrl("hatena://blog/categories"))
        
        assert "# Blog Categories" in result
        assert "Python" in result
        assert "Java" in result
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_read_resource_unknown(self, mock_get_client):
        """Test reading unknown resource."""
        mock_get_client.return_value = Mock()
        
        result = await handle_read_resource(AnyUrl("hatena://unknown"))
        
        assert "Error: Unknown resource" in result
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_read_resource_with_exception(self, mock_get_client):
        """Test reading resource with exception."""
        mock_get_client.side_effect = Exception("Test error")
        
        result = await handle_read_resource(AnyUrl("hatena://blog/entries"))
        
        assert "Error: Test error" in result


class TestFormatters:
    """Test cases for formatting functions."""
    
    def test_format_entry_summary(self):
        """Test formatting entry summary."""
        entry = BlogEntry(
            id="123",
            title="Test Entry",
            content="This is a test content that is longer than 200 characters. " * 5,
            published=datetime(2024, 1, 1, 10, 0, 0),
            updated=datetime(2024, 1, 1, 10, 0, 0),
            author="test_user",
            categories=["Python", "Testing"],
            is_draft=False
        )
        
        result = format_entry_summary(entry)
        
        assert "Test Entry" in result
        assert "✅ Published" in result
        assert "Python, Testing" in result
        assert "test_user" in result
        assert "2024-01-01 10:00" in result
        assert "..." in result  # Content should be truncated
    
    def test_format_entry_summary_draft(self):
        """Test formatting draft entry summary."""
        entry = BlogEntry(
            id="123",
            title="Draft Entry",
            content="Short content",
            published=datetime(2024, 1, 1, 10, 0, 0),
            updated=datetime(2024, 1, 1, 10, 0, 0),
            author="test_user",
            is_draft=True
        )
        
        result = format_entry_summary(entry)
        
        assert "📝 Draft" in result
        assert "No categories" in result
    
    def test_format_entry_detail(self):
        """Test formatting detailed entry."""
        entry = BlogEntry(
            id="123",
            title="Test Entry",
            content="Detailed content",
            published=datetime(2024, 1, 1, 10, 0, 0),
            updated=datetime(2024, 1, 1, 11, 0, 0),
            author="test_user",
            categories=["Python"],
            is_draft=False
        )
        
        result = format_entry_detail(entry)
        
        assert "# Test Entry ✅ Published" in result
        assert "**ID:** 123" in result
        assert "**Author:** test_user" in result
        assert "**Published:** 2024-01-01 10:00:00" in result
        assert "**Updated:** 2024-01-01 11:00:00" in result
        assert "**Categories:** Python" in result
        assert "## Content" in result
        assert "Detailed content" in result


class TestMain:
    """Test cases for main functions."""
    
    @pytest.mark.asyncio
    async def test_main(self):
        """Test main function with mocked stdio_server."""
        # Mock the local import in the main function
        with patch('mcp.server.stdio.stdio_server') as mock_stdio_server, \
             patch.object(app, 'run') as mock_app_run:
            
            # Create async context manager mock
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__.return_value = (Mock(), Mock())
            mock_context_manager.__aexit__.return_value = None
            mock_stdio_server.return_value = mock_context_manager
            mock_app_run.return_value = None
            
            await main()
            
            mock_stdio_server.assert_called_once()
            mock_app_run.assert_called_once()
    
    @patch('hatena_blog_mcp.server.asyncio.run')
    def test_cli_main_success(self, mock_asyncio_run):
        """Test CLI main function success."""
        mock_asyncio_run.return_value = None
        
        cli_main()
        
        mock_asyncio_run.assert_called_once()
    
    @patch('hatena_blog_mcp.server.asyncio.run')
    @patch('sys.exit')
    def test_cli_main_keyboard_interrupt(self, mock_exit, mock_asyncio_run):
        """Test CLI main function with keyboard interrupt."""
        mock_asyncio_run.side_effect = KeyboardInterrupt()
        
        cli_main()
        
        mock_exit.assert_called_once_with(0)
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_create_blog_entry(self, mock_get_client):
        """Test create_blog_entry tool call."""
        mock_client = Mock()
        mock_entry = BlogEntry(
            id="456",
            title="New Blog Post",
            content="This is a new blog post",
            published=datetime(2024, 1, 1, 15, 0, 0),
            updated=datetime(2024, 1, 1, 15, 0, 0),
            author="test_user",
            categories=["Tech", "Python"],
            is_draft=True
        )
        mock_client.create_entry.return_value = mock_entry
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("create_blog_entry", {
            "title": "New Blog Post",
            "content": "This is a new blog post",
            "categories": ["Tech", "Python"],
            "is_draft": True
        })
        
        assert len(result) == 1
        assert "Successfully created blog entry: 📝 Draft" in result[0].text
        assert "New Blog Post" in result[0].text
        assert "Tech, Python" in result[0].text
        mock_client.create_entry.assert_called_once_with(
            "New Blog Post",
            "This is a new blog post",
            ["Tech", "Python"],
            True
        )
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_create_blog_entry_published(self, mock_get_client):
        """Test create_blog_entry tool call for published entry."""
        mock_client = Mock()
        mock_entry = BlogEntry(
            id="457",
            title="Published Post",
            content="This is a published post",
            published=datetime(2024, 1, 1, 16, 0, 0),
            updated=datetime(2024, 1, 1, 16, 0, 0),
            author="test_user",
            is_draft=False
        )
        mock_client.create_entry.return_value = mock_entry
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("create_blog_entry", {
            "title": "Published Post",
            "content": "This is a published post",
            "is_draft": False
        })
        
        assert len(result) == 1
        assert "Successfully created blog entry: ✅ Published" in result[0].text
        assert "Published Post" in result[0].text
        mock_client.create_entry.assert_called_once_with(
            "Published Post",
            "This is a published post",
            [],
            False
        )
    
    @pytest.mark.asyncio
    @patch('hatena_blog_mcp.server.get_client')
    async def test_handle_call_tool_create_blog_entry_defaults(self, mock_get_client):
        """Test create_blog_entry tool call with default values."""
        mock_client = Mock()
        mock_entry = BlogEntry(
            id="458",
            title="Default Settings Post",
            content="Post with default settings",
            published=datetime(2024, 1, 1, 17, 0, 0),
            updated=datetime(2024, 1, 1, 17, 0, 0),
            author="test_user",
            is_draft=True
        )
        mock_client.create_entry.return_value = mock_entry
        mock_get_client.return_value = mock_client
        
        result = await handle_call_tool("create_blog_entry", {
            "title": "Default Settings Post",
            "content": "Post with default settings"
        })
        
        assert len(result) == 1
        assert "📝 Draft" in result[0].text
        mock_client.create_entry.assert_called_once_with(
            "Default Settings Post",
            "Post with default settings",
            [],
            True
        )