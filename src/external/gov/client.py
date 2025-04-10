"""
Data.gov API async client for making requests to various Data.gov APIs.
This client provides a simple interface for making API calls to Data.gov endpoints.
"""

import httpx
import json
import typing
import asyncio
from urllib.parse import urljoin
from src.config.manager import settings
from src.utilities.logging.logger import logger

class DataGovClient:
    """
    Asynchronous client for interacting with Data.gov APIs.
    
    This client handles authentication, request formatting, and response parsing
    for Data.gov API endpoints. It supports various endpoints and data formats.
    """
    
    def __init__(self, max_retries=3, retry_delay=1):
        """
        Initialize the Data.gov API client.
        
        Args:
            max_retries: Maximum number of retry attempts for failed requests.
            retry_delay: Base delay between retries in seconds (will be exponentially increased).
        """
        self.base_url = settings.DATA_GOV_URL
        self.api_key = settings.DATA_GOV_API_KEY
        self.client = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    async def __aenter__(self):
        """Set up the httpx client when entering a context manager."""
        if self.client is None:
            self.client = httpx.AsyncClient()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the httpx client when exiting a context manager."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None
    
    async def _ensure_client(self):
        """Ensure a httpx client exists."""
        if self.client is None:
            self.client = httpx.AsyncClient()
    
    async def close(self):
        """Close the client session."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build a complete URL for a given endpoint.
        
        Args:
            endpoint: The API endpoint path.
            
        Returns:
            The complete URL with the base URL and endpoint.
        """
        return urljoin(self.base_url, endpoint)
    
    def _add_api_key(self, params: dict = None) -> dict:
        """
        Add the API key to request parameters.
        
        Args:
            params: Existing query parameters.
            
        Returns:
            Updated parameters with the API key added.
        """
        params = params or {}
        params['api-key'] = self.api_key
        return params
    
    async def _make_request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make an HTTP request with retry logic for transient errors.
        
        Args:
            method: HTTP method to use (get, post, etc.)
            url: The URL to request
            **kwargs: Additional arguments to pass to the httpx request
            
        Returns:
            The httpx Response object
            
        Raises:
            httpx.HTTPError: If the request fails after all retries
        """
        await self._ensure_client()
        
        request_method = getattr(self.client, method.lower())
        retries = 0
        last_exception = None
        
        while retries <= self.max_retries:
            try:
                if retries > 0:
                    # Only log retries, not the initial attempt
                    logger.info(f"Retry attempt {retries} for {method} request to {url}")
                
                response = await request_method(url, **kwargs)
                response.raise_for_status()
                return response
                
            except (httpx.HTTPError, httpx.NetworkError, httpx.TimeoutException) as e:
                last_exception = e
                # Only retry on certain status codes that indicate temporary issues
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code not in (408, 429, 500, 502, 503, 504):
                    # Don't retry on client errors except timeout (408) and rate limit (429)
                    raise
                
                retries += 1
                if retries > self.max_retries:
                    logger.error(f"Maximum retry attempts ({self.max_retries}) reached for {url}")
                    raise
                
                # Exponential backoff
                delay = self.retry_delay * (2 ** (retries - 1))
                logger.warning(f"Request failed: {str(e)}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
        
        # This should not be reached, but just in case
        if last_exception:
            raise last_exception
        raise httpx.RequestError(f"Failed to make request to {url} after {self.max_retries} retries")
    
    async def get(self, endpoint: str, params: dict = None) -> typing.Dict:
        """
        Make a GET request to a Data.gov API endpoint.
        
        Args:
            endpoint: The API endpoint path.
            params: Query parameters to include in the request.
            
        Returns:
            The JSON response data as a dictionary.
            
        Raises:
            httpx.HTTPError: If the request fails after all retries.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        params = self._add_api_key(params)
        url = self._build_url(endpoint)
        
        try:
            logger.info(f"Making GET request to {url}")
            response = await self._make_request_with_retry('get', url, params=params)
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from {url}: {str(e)}")
            raise
    
    async def post(self, endpoint: str, data: dict = None, params: dict = None) -> typing.Dict:
        """
        Make a POST request to a Data.gov API endpoint.
        
        Args:
            endpoint: The API endpoint path.
            data: JSON data to include in the request body.
            params: Query parameters to include in the request.
            
        Returns:
            The JSON response data as a dictionary.
            
        Raises:
            httpx.HTTPError: If the request fails after all retries.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        params = self._add_api_key(params)
        url = self._build_url(endpoint)
        
        try:
            logger.info(f"Making POST request to {url}")
            response = await self._make_request_with_retry('post', url, json=data, params=params)
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from {url}: {str(e)}")
            raise
    
    async def put(self, endpoint: str, data: dict = None, params: dict = None) -> typing.Dict:
        """
        Make a PUT request to a Data.gov API endpoint.
        
        Args:
            endpoint: The API endpoint path.
            data: JSON data to include in the request body.
            params: Query parameters to include in the request.
            
        Returns:
            The JSON response data as a dictionary.
        """
        params = self._add_api_key(params)
        url = self._build_url(endpoint)
        
        try:
            logger.info(f"Making PUT request to {url}")
            response = await self._make_request_with_retry('put', url, json=data, params=params)
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from {url}: {str(e)}")
            raise
    
    async def delete(self, endpoint: str, params: dict = None) -> typing.Dict:
        """
        Make a DELETE request to a Data.gov API endpoint.
        
        Args:
            endpoint: The API endpoint path.
            params: Query parameters to include in the request.
            
        Returns:
            The JSON response data as a dictionary.
        """
        params = self._add_api_key(params)
        url = self._build_url(endpoint)
        
        try:
            logger.info(f"Making DELETE request to {url}")
            response = await self._make_request_with_retry('delete', url, params=params)
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from {url}: {str(e)}")
            raise

    # Example of a specific API method for a Data.gov dataset
    async def get_agricultural_data(self, dataset_id: str, query_params: dict = None) -> typing.Dict:
        """
        Get agricultural data from a specific Data.gov dataset.
        
        Args:
            dataset_id: The ID of the dataset to query.
            query_params: Additional query parameters.
            
        Returns:
            The agricultural data as a dictionary.
        """
        endpoint = f"/api/datasets/{dataset_id}/data"
        params = query_params or {}
        return await self.get(endpoint, params)
    
    async def get_mandi_prices(self, 
                               format: str = "json", 
                               offset: int = 0, 
                               limit: int = 10, 
                               state: str = None, 
                               district: str = None, 
                               market: str = None, 
                               commodity: str = None, 
                               variety: str = None, 
                               grade: str = None) -> typing.Dict:
        """
        Get current daily price of various commodities from various markets (Mandi).
        
        Args:
            format: Output format (json, xml, or csv). Defaults to "json".
            offset: Number of records to skip for pagination. Defaults to 0.
            limit: Maximum number of records to return. Defaults to 10.
            state: Filter by state.
            district: Filter by district.
            market: Filter by market.
            commodity: Filter by commodity.
            variety: Filter by variety.
            grade: Filter by grade.
            
        Returns:
            The commodity price data as a dictionary.
        """
        endpoint = "/resource/9ef84268-d588-465a-a308-a864a43d0070"
        
        # Build query parameters
        params = {
            'format': format,
            'offset': offset,
            'limit': limit
        }
        
        # Add optional filters if provided
        if state:
            params['filters[state.keyword]'] = state
        if district:
            params['filters[district]'] = district
        if market:
            params['filters[market]'] = market
        if commodity:
            params['filters[commodity]'] = commodity
        if variety:
            params['filters[variety]'] = variety
        if grade:
            params['filters[grade]'] = grade
        
        return await self.get(endpoint, params)
    
    # Add more specific methods for other Data.gov APIs as needed