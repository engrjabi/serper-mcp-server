import os
import ssl
import json
import certifi
import aiohttp
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
from .schemas import BaseRequest, WebpageRequest


class SearchService(ABC):
    """Abstract base class for search services"""
    
    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
    
    @abstractmethod
    async def search(self, request: BaseRequest) -> Dict[str, Any]:
        """Perform search with the service"""
        pass


class ScrapeService(ABC):
    """Abstract base class for scrape services"""
    
    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
    
    @abstractmethod
    async def scrape(self, request: WebpageRequest) -> Dict[str, Any]:
        """Scrape webpage with the service"""
        pass


class SerperSearchService(SearchService):
    """Serper search service implementation"""
    
    async def search(self, request: BaseRequest) -> Dict[str, Any]:
        # Extract the search type from the tool name
        tool_name = getattr(request, '_tool_name', 'search')
        uri_path = tool_name.split('_')[-1] if '_' in tool_name else 'search'
        url = f"https://google.serper.dev/{uri_path}"
        
        payload = request.model_dump(exclude_none=True)
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                return await response.json()


class SerperScrapeService(ScrapeService):
    """Serper scrape service implementation"""
    
    async def scrape(self, request: WebpageRequest) -> Dict[str, Any]:
        url = "https://scrape.serper.dev"
        payload = request.model_dump(exclude_none=True)
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                return await response.json()


class TavilySearchService(SearchService):
    """Tavily search service implementation"""
    
    async def search(self, request: BaseRequest) -> Dict[str, Any]:
        url = "https://api.tavily.com/search"
        
        # Transform request to Tavily format
        payload = {
            "api_key": self.api_key,
            "query": getattr(request, 'q', ''),
            "search_depth": "basic",
            "include_answer": False,
            "max_results": getattr(request, 'num', 10)
        }
        
        headers = {'Content-Type': 'application/json'}
        
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                
                # Transform response to Serper-like format
                return self._transform_tavily_response(result)
    
    def _transform_tavily_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Tavily response to match Serper format"""
        organic = []
        for item in result.get('results', []):
            organic.append({
                'title': item.get('title', ''),
                'link': item.get('url', ''),
                'snippet': item.get('content', ''),
                'position': len(organic) + 1
            })
        
        return {
            'organic': organic,
            'searchParameters': {
                'q': result.get('query', ''),
                'type': 'search',
                'engine': 'tavily'
            }
        }


class BraveSearchService(SearchService):
    """Brave search service implementation"""
    
    async def search(self, request: BaseRequest) -> Dict[str, Any]:
        base_url = "https://api.search.brave.com/res/v1/web/search"
        
        # Build query parameters
        params = {
            'q': getattr(request, 'q', ''),
            'count': getattr(request, 'num', 10)
        }
        
        # Add optional parameters if they exist
        if hasattr(request, 'gl') and request.gl:
            params['country'] = request.gl
        if hasattr(request, 'hl') and request.hl:
            params['search_lang'] = request.hl
        
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': self.api_key
        }
        
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(base_url, headers=headers, params=params) as response:
                response.raise_for_status()
                result = await response.json()
                
                # Transform response to Serper-like format
                return self._transform_brave_response(result, params['q'])
    
    def _transform_brave_response(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Transform Brave response to match Serper format"""
        organic = []
        for item in result.get('web', {}).get('results', []):
            organic.append({
                'title': item.get('title', ''),
                'link': item.get('url', ''),
                'snippet': item.get('description', ''),
                'position': len(organic) + 1
            })
        
        return {
            'organic': organic,
            'searchParameters': {
                'q': query,
                'type': 'search',
                'engine': 'brave'
            }
        }


class JinaSearchService(SearchService):
    """Jina search service implementation (using s.jina.ai endpoint)"""
    
    async def search(self, request: BaseRequest) -> Dict[str, Any]:
        url = "https://s.jina.ai/"
        
        # Transform request to Jina format
        payload = {
            "q": getattr(request, 'q', ''),
            "options": "Markdown"
        }
        
        # Add optional parameters if available
        if hasattr(request, 'gl') and request.gl:
            payload['gl'] = request.gl
        if hasattr(request, 'hl') and request.hl:
            payload['hl'] = request.hl
        if hasattr(request, 'num') and request.num:
            payload['num'] = min(request.num, 10)  # Jina has limits
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                
                # Transform response to Serper-like format
                return self._transform_jina_response(result, payload['q'])
    
    def _transform_jina_response(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Transform Jina response to match Serper format"""
        organic = []
        
        # Jina returns results in 'data' field
        for i, item in enumerate(result.get('data', [])):
            organic.append({
                'title': item.get('title', ''),
                'link': item.get('url', ''),
                'snippet': item.get('description', ''),
                'position': i + 1
            })
        
        return {
            'organic': organic,
            'searchParameters': {
                'q': query,
                'type': 'search',
                'engine': 'jina'
            }
        }


class JinaScrapeService(ScrapeService):
    """Jina scrape service implementation"""
    
    async def scrape(self, request: WebpageRequest) -> Dict[str, Any]:
        # Jina uses URL-based scraping
        url = f"https://r.jina.ai/{request.url}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'x-respond-with': 'json',
            'x-no-cache': 'true'
        }
        
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                result = await response.json()
                
                # Transform response to Serper-like format
                return self._transform_jina_response(result, request.url)
    
    def _transform_jina_response(self, result: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Transform Jina response to match Serper format"""
        return {
            'url': url,
            'title': result.get('title', ''),
            'text': result.get('content', ''),
            'success': True,
            'engine': 'jina'
        }


# Service factory functions
def create_search_services() -> list[SearchService]:
    """Create list of search services in priority order"""
    services = []
    
    # Serper (primary)
    if serper_key := os.getenv('SERPER_API_KEY'):
        services.append(SerperSearchService(serper_key))
    
    # Tavily (fallback 1)
    if tavily_key := os.getenv('TAVILY_API_KEY'):
        services.append(TavilySearchService(tavily_key))
    
    # Brave (fallback 2)  
    if brave_key := os.getenv('BRAVE_API_KEY'):
        services.append(BraveSearchService(brave_key))
    
    # Jina (fallback 3) - currently not implemented
    if jina_key := os.getenv('JINA_API_KEY'):
        services.append(JinaSearchService(jina_key))
    
    return services


def create_scrape_services() -> list[ScrapeService]:
    """Create list of scrape services in priority order"""
    services = []
    
    # Serper (primary)
    if serper_key := os.getenv('SERPER_API_KEY'):
        services.append(SerperScrapeService(serper_key))
    
    # Jina (fallback)
    if jina_key := os.getenv('JINA_API_KEY'):
        services.append(JinaScrapeService(jina_key))
    
    return services