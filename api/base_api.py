import base64
import binascii
import json
import os
from json import JSONDecodeError
from typing import Optional, Union

import httpx
import xmltodict
from httpx._transports.default import HTTPTransport


# Custom DNS caching transport to improve request performance by keeping DNS resolutions in memory
class CashingHTTPTransport(HTTPTransport):
    """
    A custom transport implementation that extends httpx's HTTPTransport
    to enable persistent DNS caching.

    This reduces DNS lookup overhead for repeated requests to the same hosts by
    storing resolved IP addresses in memory, which can significantly improve
    performance for applications making multiple requests to the same endpoints.

    The DNS cache is implemented as a dictionary stored in the connection pool's
    _dns_cache attribute, mapping hostnames to their resolved IP addresses.

    Note: DNS records have TTLs (Time To Live) that this simple implementation
    doesn't respect. For production systems with long-running processes, consider
    implementing cache invalidation strategies.
    """

    def __init__(self, *args, **kwargs) -> None:
        # Initialize the parent HTTPTransport class
        super().__init__(*args, **kwargs)
        # Enable DNS caching by initializing the _dns_cache dictionary in the connection pool
        # This will store hostname → IP address mappings across requests
        self._pool._dns_cache = {}


class BaseApi:
    """
    BaseApi class handles basic HTTP operations (GET, POST, PUT, PATCH, DELETE, etc.)
    with functionality to check response status codes, parse responses to JSON or XML,
    and manage API authentication.

    Attributes:
        base_url (str): The base URL for the API.
        headers (dict): Default headers used for API requests.
        timeout (int): Timeout duration for requests.
        client (httpx.Client): Persistent HTTP client for efficient request handling.
    """

    def __init__(self, session_token: str) -> None:
        """
        Initialize the BaseApi class with a session token.

        This constructor sets up a persistent HTTP client with optimized connection settings,
        customized headers for authentication and content negotiation, and DNS caching for
        improved performance.

        Args:
            session_token (str): The session token used for authentication with the API.
                This is included in the Cookie header of all requests.
        """
        # Base URL for all API requests
        self.base_url = 'Https://base.url.com'

        # Standard headers used for all requests
        self.headers = {
            'Cookie': f'session={session_token}',  # Authentication via session cookie
            # for user-agent need to choose BROWSER_VERSION here {{os.getenv("BROWSER_VERSION")}}
            'User-Agent': f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          f'Chrome/{{os.getenv("BROWSER_VERSION")}} Safari/537.36',  # Emulates a standard browser
            'Content-Type': 'application/json',  # Indicates JSON request bodies
            'Accept-language': 'en-GB,en;q=0.9',  # Preferred response language
            'Accept-Encoding': 'gzip, deflate, br',  # Supports compressed responses for better perfomance
        }

        # Default timeout for all requests in seconds
        self.timeout = 30

        # Initialize persistent HTTP client with optimized settings
        # - Reuses connections for better performance
        # - Enables HTTP/2 for multiplexed requests
        # - Uses custom DNS caching transport for reduced lookup overhead
        self.client = httpx.Client(
            headers=self.headers,
            timeout=self.timeout,
            limits=httpx.Limits(
                max_connections=100,  # Maximum concurrent connections to maintain
                max_keepalive_connections=20,  # Maximum idle persistent connections to keep
                keepalive_expiry=60,  # Connection idle timeout before closing (seconds)
            ),
            http2=True,  # Enable HTTP/2 protocol for efficient requests
            transport=CashingHTTPTransport()  # Use custom transport with DNS caching
        )

    def __del__(self):
        """Enshure the HHTP client is properly closed."""
        self.client.close()

    def request(self, method: str, url: str, headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """
        Generic request method using httpx.Client with performance optimization and timing logs.

        Args:
            method (str): HTTP method (GET, POST, etc.).
            url (str): API endpoint.
            headers (Optional[dict]): Additional headers.
            **kwargs: Extra arguments like data, params, etc.

        Returns:
            httpx.Response: The server response.
        """
        # Pre-compute full URL to avoid string concatenation during request
        full_url = f"{self.base_url}{url}"

        # Use passed headers or class headers
        request_headers = headers or self.headers

        # Extract response code expectation
        response_code = kwargs.pop('response_code', None)

        # For POST/PUT requests, pre-convert data to JSON if needed
        if method in ("POST", "PUT", "PATCH") and 'data' in kwargs:
            data = kwargs.pop('data')
            if isinstance(data, (dict, list)) and not isinstance(data, str):
                kwargs['json'] = data  # Use JSON parameter for automatic serialization
                kwargs.pop('data')  # Remove data to avoid confusing

        # Make the request
        response = self.client.request(method, full_url, headers=request_headers, **kwargs)

        # Validate response
        if response_code:
            self.check_status_code(response, response_code)
        else:
            self.check_status_code_success(response)

        return response

    def get(self, url: str, headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """
        Send a GET request.

        Args:
            url (str): API endpoint.
            headers (Optional[dict]): Additional headers.
            **kwargs: Extra arguments like params, etc.

        Returns:
            httpx.Response: The server response.
        """
        return self.request('GET', url, headers=headers, **kwargs)

    def head(self, url: str, headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """
        Send a HEAD request.

        Args:
            url (str): API endpoint.
            headers (Optional[dict]): Additional headers.
            **kwargs: Extra arguments like params, etc.

        Returns:
            httpx.Response: The server response.
        """
        return self.request('HEAD', url, headers=headers, **kwargs)

    def post(self, url: str, data: Union[list, dict, str], headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """
        Send a POST request with a JSON payload.

        Args:
            url (str): API endpoint.
            data (Union[list, dict, str]): JSON payload.
            headers (Optional[dict]): Additional headers.
            **kwargs: Extra arguments like params, etc.

        Returns:
            httpx.Response: The server response.
        """
        return self.request('POST', url, data=data if isinstance(data, (list, dict)) else data, headers=headers,
                            **kwargs)

    def patch(self, url: str, data: Union[list, dict], headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """
        Send a PATCH request with a JSON payload.

        Args:
            url (str): API endpoint.
            data (Union[list, dict]): JSON payload.
            headers (Optional[dict]): Additional headers.
            **kwargs: Extra arguments like params, etc.

        Returns:
            httpx.Response: The server response.
        """
        return self.request('PATCH', url, data=data, headers=headers, **kwargs)

    def put(self, url: str, data: Union[list, dict], headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """
        Send a PUT request with a JSON payload.

        Args:
            url (str): API endpoint.
            data (Union[list, dict]): JSON payload.
            headers (Optional[dict]): Additional headers.
            **kwargs: Extra arguments like params, etc.

        Returns:
            httpx.Response: The server response.
        """
        return self.request('PUT', url, data=data, headers=headers, **kwargs)

    def delete(self, url: str, headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """
        Send a DELETE request.

        Args:
            url (str): API endpoint.
            headers (Optional[dict]): Additional headers.
            **kwargs: Extra arguments like params, etc.

        Returns:
            httpx.Response: The server response.
        """
        return self.request('DELETE', url, headers=headers, **kwargs)

    def options(self, url: str, headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """
        Send an OPTIONS request.

        Args:
            url (str): API endpoint.
            headers (Optional[dict]): Additional headers.
            **kwargs: Extra arguments like params, etc.

        Returns:
            httpx.Response: The server response.
        """
        return self.request('OPTIONS', url, headers=headers, **kwargs)

    @staticmethod
    def check_status_code_success(response: httpx.Response) -> None:
        """
        Ensure response status is in the 2xx range.

        Args:
            response (httpx.Response): The server response.

        Raises:
            AssertionError: If the response status code is not in the 2xx range.
        """
        assert str(response.status_code).startswith('2'), \
            f'Response status code = {response.status_code}, error = {response.reason_phrase} {response.text}'

    @staticmethod
    def check_status_code(response: httpx.Response, expected_code: int) -> None:
        """
        Ensure response status matches the expected code.

        Args:
            response (httpx.Response): The server response.
            expected_code (int): The expected HTTP status code.

        Raises:
            AssertionError: If the response status code does not match the expected code.
        """
        try:
            error = BaseApi.parse_response_to_json(response)
        except JSONDecodeError:
            error = 'Unable to parse error'

        assert response.status_code == expected_code, \
            f'Wrong response code. Expected = {expected_code}, received = {response.status_code} | error = {error}'

    @staticmethod
    def parse_response_to_json(response: httpx.Response) -> Union[dict, list]:
        """
        Parse response content to JSON.

        Args:
            response (httpx.Response): The server response.

        Returns:
            Union[list, dict]: Parsed JSON content.
        """
        return response.json()

    @staticmethod
    def parse_xml_to_json(response: httpx.Response) -> dict:
        """
        Convert XML response to JSON format.

        Args:
            response (httpx.Response): The server response.

        Returns:
            dict: Parsed JSON content.
        """
        xml_response = response.content
        return json.loads(json.dumps(xmltodict.parse(xml_response)))

    def get_token(self) -> str:
        """
        Retrieve an access token using client credentials.

        Returns:
            str: The access token.
        """
        url = "https://get.tokens.api-key.com/token"

        payload = {
            "grant_type": "client_credentials",
            # Some additional payload
            "client_id": "some test_id"
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            # Some additional headers
            'Cookie': "Some cookie value"
        }

        response = self.client.post(url, data=payload, headers=headers)
        self.check_status_code_success(response)

        return self.parse_response_to_json(response)['access_token']

    @staticmethod
    def parse_base64_to_dict(encoded_data: str) -> dict:
        """
        Decode a Base64 string and parse it into a Python dictionary.

        Args:
            encoded_data (str): Base64-encoded string.

        Returns:
            dict: Decoded JSON content.

        Raises:
            ValueError: If decoding or parsing fails.
        """
        if not encoded_data:
            return {}

        try:
            decoded_bytes = base64.b64decode(encoded_data)
            decoded_str = decoded_bytes.decode('utf-8')
            return json.loads(decoded_str)
        except (binascii.Error, JSONDecodeError) as e:
            raise ValueError(f'Failed to parse Base64 to dict: {e}')
