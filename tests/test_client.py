"""Tests for Hatena Blog client."""

import requests
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from hatena_blog_mcp.client import HatenaBlogClient, BlogEntry


class TestHatenaBlogClient:
    """Test cases for HatenaBlogClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = HatenaBlogClient("test_user", "test_key", "test_blog")
    
    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.hatena_id == "test_user"
        assert self.client.api_key == "test_key"
        assert self.client.blog_id == "test_blog"
        assert self.client.base_url == "https://blog.hatena.ne.jp/test_user/atom"
        assert self.client.auth == ("test_user", "test_key")
    
    @patch('hatena_blog_mcp.client.requests.get')
    def test_get_entries(self, mock_get):
        """Test getting blog entries."""
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>https://test.hatenablog.com/entry/123</id>
        <title>Test Entry</title>
        <content type="text/plain">Test content</content>
        <published>2024-01-01T10:00:00Z</published>
        <updated>2024-01-01T10:00:00Z</updated>
        <author><name>test_user</name></author>
        <category term="test" />
    </entry>
</feed>'''
        mock_get.return_value = mock_response
        
        entries = self.client.get_entries()
        
        assert len(entries) == 1
        entry = entries[0]
        assert entry.id == "123"
        assert entry.title == "Test Entry"
        assert entry.content == "Test content"
        assert entry.author == "test_user"
        assert "test" in entry.categories
        
        mock_get.assert_called_once_with(
            "https://blog.hatena.ne.jp/test_user/atom/entry",
            auth=("test_user", "test_key"),
            params={}
        )
    
    @patch('hatena_blog_mcp.client.requests.get')
    def test_get_entries_with_page(self, mock_get):
        """Test getting entries with page parameter."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"></feed>'''
        mock_get.return_value = mock_response
        
        self.client.get_entries(page=2)
        
        mock_get.assert_called_once_with(
            "https://blog.hatena.ne.jp/test_user/atom/entry",
            auth=("test_user", "test_key"),
            params={"page": 2}
        )
    
    def test_get_entry(self):
        """Test getting a specific entry."""
        # Mock get_entries to return test data
        with patch.object(self.client, 'get_entries') as mock_get_entries:
            mock_entries_page1 = [
                BlogEntry(
                    id="123",
                    title="Test Entry",
                    content="Test content",
                    published=datetime.now(),
                    updated=datetime.now(),
                    author="test_user"
                ),
                BlogEntry(
                    id="456",
                    title="Another Entry",
                    content="Another content",
                    published=datetime.now(),
                    updated=datetime.now(),
                    author="test_user"
                )
            ]
            # Return entries on first page, empty on second page
            mock_get_entries.side_effect = [mock_entries_page1, []]
            
            entry = self.client.get_entry("123")
            
            assert entry is not None
            assert entry.id == "123"
            assert entry.title == "Test Entry"
            
            # Should call get_entries with page 1
            mock_get_entries.assert_called_with(1)
    
    def test_get_entry_not_found(self):
        """Test getting a non-existent entry."""
        # Mock get_entries to return empty results
        with patch.object(self.client, 'get_entries') as mock_get_entries:
            mock_get_entries.return_value = []
            
            entry = self.client.get_entry("nonexistent")
            
            assert entry is None
    
    def test_search_entries(self):
        """Test searching entries."""
        # Mock get_entries to return test data
        with patch.object(self.client, 'get_entries') as mock_get_entries:
            mock_entries = [
                BlogEntry(
                    id="1",
                    title="Python Tutorial",
                    content="Learn Python programming",
                    published=datetime.now(),
                    updated=datetime.now(),
                    author="test_user"
                ),
                BlogEntry(
                    id="2",
                    title="Java Guide",
                    content="Java programming guide",
                    published=datetime.now(),
                    updated=datetime.now(),
                    author="test_user"
                )
            ]
            # Mock to return entries once, then empty list to stop search
            mock_get_entries.side_effect = [mock_entries, []]
            
            results = self.client.search_entries("Python")
            
            assert len(results) == 1
            assert results[0].title == "Python Tutorial"
    
    @patch('hatena_blog_mcp.client.requests.get')
    def test_get_categories(self, mock_get):
        """Test getting categories."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <category term="Python" />
    <category term="Java" />
</feed>'''
        mock_get.return_value = mock_response
        
        categories = self.client.get_categories()
        
        assert "Python" in categories
        assert "Java" in categories
        assert len(categories) == 2
        
        mock_get.assert_called_once_with(
            "https://blog.hatena.ne.jp/test_user/atom/category",
            auth=("test_user", "test_key")
        )
    
    @patch('hatena_blog_mcp.client.requests.get')
    def test_discover_entry_collection_url_success(self, mock_get):
        """Test successful discovery of entry collection URL."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '''<?xml version="1.0" encoding="utf-8"?>
<service xmlns="http://www.w3.org/2007/app" xmlns:atom="http://www.w3.org/2005/Atom">
    <workspace>
        <collection href="https://blog.hatena.ne.jp/test_user/atom/entry">
            <accept>application/atom+xml;type=entry</accept>
        </collection>
    </workspace>
</service>'''
        mock_get.return_value = mock_response
        
        client = HatenaBlogClient("test_user", "test_key", "test_blog")
        
        assert client._entry_collection_url == "https://blog.hatena.ne.jp/test_user/atom/entry"
    
    @patch('hatena_blog_mcp.client.requests.get')
    def test_discover_entry_collection_url_fallback_no_collection(self, mock_get):
        """Test fallback when no collection is found."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '''<?xml version="1.0" encoding="utf-8"?>
<service xmlns="http://www.w3.org/2007/app" xmlns:atom="http://www.w3.org/2005/Atom">
    <workspace>
    </workspace>
</service>'''
        mock_get.return_value = mock_response
        
        client = HatenaBlogClient("test_user", "test_key", "test_blog")
        
        assert client._entry_collection_url == "https://blog.hatena.ne.jp/test_user/atom/entry"
    
    @patch('hatena_blog_mcp.client.requests.get')
    def test_discover_entry_collection_url_fallback_exception(self, mock_get):
        """Test fallback when discovery raises exception."""
        mock_get.side_effect = Exception("Network error")
        
        client = HatenaBlogClient("test_user", "test_key", "test_blog")
        
        assert client._entry_collection_url == "https://blog.hatena.ne.jp/test_user/atom/entry"
    
    def test_get_entry_multiple_pages(self):
        """Test getting entry that requires searching multiple pages."""
        with patch.object(self.client, 'get_entries') as mock_get_entries:
            # Entry not found on first page, found on second page
            mock_entries_page1 = [
                BlogEntry(
                    id="111",
                    title="First Entry",
                    content="First content",
                    published=datetime.now(),
                    updated=datetime.now(),
                    author="test_user"
                )
            ]
            mock_entries_page2 = [
                BlogEntry(
                    id="123",
                    title="Target Entry",
                    content="Target content",
                    published=datetime.now(),
                    updated=datetime.now(),
                    author="test_user"
                )
            ]
            mock_get_entries.side_effect = [mock_entries_page1, mock_entries_page2, []]
            
            entry = self.client.get_entry("123")
            
            assert entry is not None
            assert entry.id == "123"
            assert entry.title == "Target Entry"
            
            # Should call get_entries with page 1 and 2
            assert mock_get_entries.call_count == 2
    
    def test_search_entries_max_search_limit(self):
        """Test search entries respects max search limit."""
        with patch.object(self.client, 'get_entries') as mock_get_entries:
            # Mock to return entries that don't match the query for 100 searches
            mock_entries = [
                BlogEntry(
                    id="1",
                    title="Unrelated Title",
                    content="Unrelated content",
                    published=datetime.now(),
                    updated=datetime.now(),
                    author="test_user"
                )
            ]
            mock_get_entries.return_value = mock_entries
            
            results = self.client.search_entries("NonExistentQuery")
            
            assert len(results) == 0
            # Should stop after 100 total searches
            assert mock_get_entries.call_count == 100
    
    def test_search_entries_max_results_break(self):
        """Test search entries breaks when max_results is reached."""
        with patch.object(self.client, 'get_entries') as mock_get_entries:
            # Mock to return matching entries
            mock_entries = [
                BlogEntry(
                    id=str(i),
                    title=f"Python Tutorial {i}",
                    content="Learn Python programming",
                    published=datetime.now(),
                    updated=datetime.now(),
                    author="test_user"
                ) for i in range(10)
            ]
            mock_get_entries.return_value = mock_entries
            
            # Search with max_results=3
            results = self.client.search_entries("Python", max_results=3)
            
            assert len(results) == 3
            # Should only call get_entries once since we get 3 results immediately
            assert mock_get_entries.call_count == 1
    
    def test_parse_entry_missing_required_fields(self):
        """Test parsing entry with missing required fields."""
        import xml.etree.ElementTree as ET
        
        # Create entry with missing title
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
    <id>https://test.hatenablog.com/entry/123</id>
    <content type="text/plain">Test content</content>
    <published>2024-01-01T10:00:00Z</published>
</entry>'''
        
        entry_elem = ET.fromstring(xml_content)
        result = self.client._parse_entry(entry_elem)
        
        assert result is None
    
    def test_parse_entry_with_exception(self):
        """Test parsing entry that raises exception."""
        import xml.etree.ElementTree as ET
        
        # Create malformed entry
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
    <id>https://test.hatenablog.com/entry/123</id>
    <title>Test Entry</title>
    <content type="text/plain">Test content</content>
    <published>invalid-date</published>
</entry>'''
        
        entry_elem = ET.fromstring(xml_content)
        result = self.client._parse_entry(entry_elem)
        
        assert result is None
    
    def test_parse_entry_with_edit_url(self):
        """Test parsing entry with edit URL."""
        import xml.etree.ElementTree as ET
        
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
    <id>https://test.hatenablog.com/entry/123</id>
    <title>Test Entry</title>
    <content type="text/plain">Test content</content>
    <published>2024-01-01T10:00:00Z</published>
    <author><name>test_user</name></author>
    <link rel="edit" href="https://blog.hatena.ne.jp/test_user/atom/entry/123" />
</entry>'''
        
        entry_elem = ET.fromstring(xml_content)
        result = self.client._parse_entry(entry_elem)
        
        assert result is not None
        assert result.edit_url == "https://blog.hatena.ne.jp/test_user/atom/entry/123"
    
    @patch('hatena_blog_mcp.client.requests.post')
    def test_create_entry(self, mock_post):
        """Test creating a new blog entry."""
        # Mock response for successful creation
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app">
    <entry>
        <id>https://test.hatenablog.com/entry/123</id>
        <title>New Test Entry</title>
        <content type="text/html">Test content</content>
        <published>2024-01-01T10:00:00Z</published>
        <updated>2024-01-01T10:00:00Z</updated>
        <author><name>test_user</name></author>
        <category term="test" />
        <app:draft>yes</app:draft>
    </entry>
</feed>'''
        mock_post.return_value = mock_response
        
        entry = self.client.create_entry(
            title="New Test Entry",
            content="Test content",
            categories=["test"],
            is_draft=True
        )
        
        assert entry.id == "123"
        assert entry.title == "New Test Entry"
        assert entry.content == "Test content"
        assert entry.is_draft is True
        assert "test" in entry.categories
        
        # Verify the POST request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://blog.hatena.ne.jp/test_user/atom/entry"
        assert call_args[1]['auth'] == ("test_user", "test_key")
        assert call_args[1]['headers']['Content-Type'] == 'application/xml; charset=utf-8'
        
        # Check that XML was properly formed
        xml_data = call_args[1]['data'].decode('utf-8')
        assert '<title>New Test Entry</title>' in xml_data
        assert '<content type="text/html">Test content</content>' in xml_data
        assert '<category term="test"' in xml_data
        assert (':control>' in xml_data or '<app:control>' in xml_data) and ':draft>yes</' in xml_data
    
    @patch('hatena_blog_mcp.client.requests.post')
    def test_create_entry_published(self, mock_post):
        """Test creating a published blog entry."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>https://test.hatenablog.com/entry/124</id>
        <title>Published Entry</title>
        <content type="text/html">Published content</content>
        <published>2024-01-01T10:00:00Z</published>
        <updated>2024-01-01T10:00:00Z</updated>
        <author><name>test_user</name></author>
    </entry>
</feed>'''
        mock_post.return_value = mock_response
        
        entry = self.client.create_entry(
            title="Published Entry",
            content="Published content",
            is_draft=False
        )
        
        assert entry.is_draft is False
        
        # Check that no control/draft elements are included for published entries
        xml_data = mock_post.call_args[1]['data'].decode('utf-8')
        assert ':control>' not in xml_data
    
    @patch('hatena_blog_mcp.client.requests.post')
    def test_create_entry_no_categories(self, mock_post):
        """Test creating entry with no categories."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>https://test.hatenablog.com/entry/125</id>
        <title>No Categories Entry</title>
        <content type="text/html">Content without categories</content>
        <published>2024-01-01T10:00:00Z</published>
        <updated>2024-01-01T10:00:00Z</updated>
        <author><name>test_user</name></author>
    </entry>
</feed>'''
        mock_post.return_value = mock_response
        
        entry = self.client.create_entry(
            title="No Categories Entry",
            content="Content without categories"
        )
        
        assert len(entry.categories) == 0
        
        # Check that no category elements are included
        xml_data = mock_post.call_args[1]['data'].decode('utf-8')
        assert '<category' not in xml_data
    
    @patch('hatena_blog_mcp.client.requests.post')
    def test_create_entry_http_error(self, mock_post):
        """Test creating entry with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            self.client.create_entry("Test Title", "Test Content")
    
    @patch('hatena_blog_mcp.client.requests.post')
    def test_create_entry_parse_error(self, mock_post):
        """Test creating entry with parse error in response."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>'''  # Empty feed
        mock_post.return_value = mock_response
        
        with pytest.raises(ValueError, match="Failed to parse created entry from response"):
            self.client.create_entry("Test Title", "Test Content")
    
    def test_create_entry_xml_generation(self):
        """Test XML generation for entry creation."""
        xml = self.client._create_entry_xml(
            title="Test Title",
            content="<p>Test content</p>",
            categories=["cat1", "cat2"],
            is_draft=True
        )
        
        assert '<title>Test Title</title>' in xml
        assert '<content type="text/html">&lt;p&gt;Test content&lt;/p&gt;</content>' in xml
        assert '<category term="cat1"' in xml
        assert '<category term="cat2"' in xml
        assert (':control>' in xml or '<app:control>' in xml) and ':draft>yes</' in xml
        assert 'xmlns="http://www.w3.org/2005/Atom"' in xml
        assert 'xmlns:app="http://www.w3.org/2007/app"' in xml
    
    def test_create_entry_xml_generation_no_draft(self):
        """Test XML generation without control/draft elements for published entries."""
        xml = self.client._create_entry_xml(
            title="Published Title",
            content="Published content",
            categories=[],
            is_draft=False
        )
        
        assert ':control>' not in xml
        assert '<category' not in xml