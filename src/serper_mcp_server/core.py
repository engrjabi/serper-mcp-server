import os
import ssl
from typing import Dict, Any
import certifi
import aiohttp
from pydantic import BaseModel
from .enums import SerperTools
from .schemas import WebpageRequest, BaseRequest
from .services import create_search_services, create_scrape_services, SearchService, ScrapeService

SERPER_API_KEY = str.strip(os.getenv("SERPER_API_KEY", ""))
AIOHTTP_TIMEOUT = int(os.getenv("AIOHTTP_TIMEOUT", "15"))

# Initialize service pools
_search_services = None
_scrape_services = None

def get_search_services() -> list[SearchService]:
    """Get search services, initializing if needed"""
    global _search_services
    if _search_services is None:
        _search_services = create_search_services()
    return _search_services

def get_scrape_services() -> list[ScrapeService]:
    """Get scrape services, initializing if needed"""
    global _scrape_services
    if _scrape_services is None:
        _scrape_services = create_scrape_services()
    return _scrape_services


async def google(tool: SerperTools, request: BaseModel) -> Dict[str, Any]:
    """Search with fallback across multiple services"""
    services = get_search_services()
    
    if not services:
        raise Exception("No search services configured")
    
    # Add tool name to request for service-specific handling
    if hasattr(request, '_tool_name'):
        request._tool_name = tool.value
    else:
        # Create a new request with the tool name
        request_dict = request.model_dump()
        request_dict['_tool_name'] = tool.value
        # Recreate the request with the tool name (this is a bit hacky but works)
        setattr(request, '_tool_name', tool.value)
    
    last_exception = None
    for service in services:
        try:
            result = await service.search(request)
            return result
        except (aiohttp.ClientError, aiohttp.ClientResponseError) as e:
            last_exception = e
            # Continue to next service on client errors (4xx, 5xx, network issues)
            continue
        except Exception as e:
            # For other exceptions, re-raise immediately
            raise e
    
    # If all services failed, raise the last exception
    if last_exception:
        raise last_exception
    else:
        raise Exception("All search services failed")


async def scape(request: WebpageRequest) -> Dict[str, Any]:
    """Scrape with fallback across multiple services"""
    services = get_scrape_services()
    
    if not services:
        raise Exception("No scrape services configured")
    
    last_exception = None
    for service in services:
        try:
            result = await service.scrape(request)
            return result
        except (aiohttp.ClientError, aiohttp.ClientResponseError) as e:
            last_exception = e
            # Continue to next service on client errors (4xx, 5xx, network issues)
            continue
        except Exception as e:
            # For other exceptions, re-raise immediately
            raise e
    
    # If all services failed, raise the last exception
    if last_exception:
        raise last_exception
    else:
        raise Exception("All scrape services failed")


async def fetch_json(url: str, request: BaseModel) -> Dict[str, Any]:
    payload = request.model_dump(exclude_none=True)
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    timeout = aiohttp.ClientTimeout(total=AIOHTTP_TIMEOUT)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()
            return await response.json()
