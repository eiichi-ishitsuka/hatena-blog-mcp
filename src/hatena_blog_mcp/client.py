"""Hatena Blog AtomPub API client."""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional
import requests
from pydantic import BaseModel


class BlogEntry(BaseModel):
    """Represents a blog entry."""
    
    id: str
    title: str
    content: str
    published: datetime
    updated: datetime
    author: str
    categories: List[str] = []
    is_draft: bool = False
    edit_url: Optional[str] = None


class HatenaBlogClient:
    """Client for Hatena Blog AtomPub API."""
    
    def __init__(self, hatena_id: str, api_key: str, blog_id: str):
        """Initialize the client.
        
        Args:
            hatena_id: Hatena user ID
            api_key: API key from account settings
            blog_id: Blog ID (domain name part)
        """
        self.hatena_id = hatena_id
        self.api_key = api_key
        self.blog_id = blog_id
        
        self.base_url = f"https://blog.hatena.ne.jp/{hatena_id}/atom"
        
        self.auth = (hatena_id, api_key)
        
        # XML namespaces
        self.ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'app': 'http://www.w3.org/2007/app'
        }
        
        # Discover the actual entry collection URL
        self._entry_collection_url = None
        self._discover_entry_collection_url()
    
    def _discover_entry_collection_url(self):
        """Discover the actual entry collection URL from the service document."""
        try:
            response = requests.get(self.base_url, auth=self.auth)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            
            # Find the collection with entry type
            for collection in root.findall('.//app:collection', self.ns):
                href = collection.get('href')
                accept = collection.find('app:accept', self.ns)
                if accept is not None and 'type=entry' in accept.text:
                    self._entry_collection_url = href
                    break
            
            # Fallback to the old method if discovery fails
            if not self._entry_collection_url:
                self._entry_collection_url = f"{self.base_url}/entry"
                
        except Exception:
            # Fallback to the old method if discovery fails
            self._entry_collection_url = f"{self.base_url}/entry"
    
    def get_entries(self, page: int = 1) -> List[BlogEntry]:
        """Get blog entries.
        
        Args:
            page: Page number (1-based)
            
        Returns:
            List of blog entries
        """
        url = self._entry_collection_url
        params = {"page": page} if page > 1 else {}
        
        response = requests.get(url, auth=self.auth, params=params)
        response.raise_for_status()
        
        return self._parse_feed(response.text)
    
    def get_entry(self, entry_id: str) -> Optional[BlogEntry]:
        """Get a specific blog entry.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Blog entry or None if not found
        """
        url = f"{self._entry_collection_url}/{entry_id}"
        
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            entries = self._parse_feed(response.text)
            return entries[0] if entries else None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def search_entries(self, query: str, max_results: int = 10) -> List[BlogEntry]:
        """Search blog entries by title or content.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of matching blog entries
        """
        results = []
        page = 1
        total_searched = 0
        
        while len(results) < max_results and total_searched < 100:  # Limit search scope
            entries = self.get_entries(page)
            if not entries:
                break
            
            for entry in entries:
                total_searched += 1
                if (query.lower() in entry.title.lower() or 
                    query.lower() in entry.content.lower()):
                    results.append(entry)
                    if len(results) >= max_results:
                        break
            
            page += 1
            
        return results[:max_results]
    
    def get_categories(self) -> List[str]:
        """Get available categories.
        
        Returns:
            List of category names
        """
        url = f"{self.base_url}/category"
        
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        
        root = ET.fromstring(response.text)
        categories = []
        
        for category in root.findall('.//atom:category', self.ns):
            term = category.get('term')
            if term:
                categories.append(term)
        
        return categories
    
    def _parse_feed(self, xml_content: str) -> List[BlogEntry]:
        """Parse Atom feed XML.
        
        Args:
            xml_content: XML content
            
        Returns:
            List of blog entries
        """
        root = ET.fromstring(xml_content)
        entries = []
        
        for entry_elem in root.findall('.//atom:entry', self.ns):
            entry = self._parse_entry(entry_elem)
            if entry:
                entries.append(entry)
        
        return entries
    
    def _parse_entry(self, entry_elem: ET.Element) -> Optional[BlogEntry]:
        """Parse a single entry element.
        
        Args:
            entry_elem: Entry XML element
            
        Returns:
            Blog entry or None if parsing fails
        """
        try:
            # Extract basic information
            id_elem = entry_elem.find('atom:id', self.ns)
            title_elem = entry_elem.find('atom:title', self.ns)
            content_elem = entry_elem.find('atom:content', self.ns)
            published_elem = entry_elem.find('atom:published', self.ns)
            updated_elem = entry_elem.find('atom:updated', self.ns)
            author_elem = entry_elem.find('.//atom:author/atom:name', self.ns)
            
            if not all([id_elem is not None, title_elem is not None, content_elem is not None, published_elem is not None]):
                return None
            
            # Extract entry ID from URL
            entry_id = id_elem.text.split('/')[-1] if id_elem.text else ""
            
            # Parse dates
            published = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
            updated = published
            if updated_elem is not None:
                updated = datetime.fromisoformat(updated_elem.text.replace('Z', '+00:00'))
            
            # Extract categories
            categories = []
            for cat_elem in entry_elem.findall('atom:category', self.ns):
                term = cat_elem.get('term')
                if term:
                    categories.append(term)
            
            # Check if draft
            draft_elem = entry_elem.find('.//app:draft', self.ns)
            is_draft = draft_elem is not None and draft_elem.text == 'yes'
            
            # Find edit URL
            edit_url = None
            for link in entry_elem.findall('atom:link', self.ns):
                if link.get('rel') == 'edit':
                    edit_url = link.get('href')
                    break
            
            return BlogEntry(
                id=entry_id,
                title=title_elem.text or "",
                content=content_elem.text or "",
                published=published,
                updated=updated,
                author=author_elem.text if author_elem is not None else "",
                categories=categories,
                is_draft=is_draft,
                edit_url=edit_url
            )
        
        except Exception:
            return None