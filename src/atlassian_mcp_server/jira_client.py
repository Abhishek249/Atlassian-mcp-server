"""Jira API client with authentication and rate limiting."""

import asyncio
import base64
import logging
from typing import Any

import httpx

from .config import Settings

logger = logging.getLogger(__name__)


class JiraClient:
    """Async Jira API client with rate limiting and error handling."""

    def __init__(self, settings: Settings):
        """Initialize the Jira client."""
        self.settings = settings
        self.base_url = settings.jira_base_url

        # Create auth header
        auth_string = f"{settings.atlassian_email}:{settings.atlassian_api_token}"
        auth_bytes = auth_string.encode("utf-8")
        auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")

        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Rate limiting
        self._request_times: list[float] = []
        self._max_requests_per_second = 10  # Jira Cloud limit

    async def _rate_limit(self) -> None:
        """Implement rate limiting."""
        now = asyncio.get_event_loop().time()
        # Remove requests older than 1 second
        self._request_times = [t for t in self._request_times if now - t < 1.0]

        if len(self._request_times) >= self._max_requests_per_second:
            # Wait until oldest request is 1 second old
            sleep_time = 1.0 - (now - self._request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

        self._request_times.append(now)

    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an HTTP request to Jira API with rate limiting and error handling."""
        await self._rate_limit()

        url = f"{self.base_url}{endpoint}"
        logger.debug(f"{method} {url}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method,
                    url,
                    headers=self.headers,
                    timeout=30.0,
                    **kwargs,
                )
                response.raise_for_status()
                return response.json() if response.content else {}
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else "No details"
                logger.error(f"HTTP {e.response.status_code}: {error_detail}")
                raise ValueError(
                    f"Jira API error ({e.response.status_code}): {error_detail}"
                ) from e
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                raise ValueError(f"Network error: {str(e)}") from e

    async def get(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """GET request."""
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """POST request."""
        return await self.request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """PUT request."""
        return await self.request("PUT", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """DELETE request."""
        return await self.request("DELETE", endpoint, **kwargs)
