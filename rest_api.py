import httpx

from nicegui import ui, app

from typing import Optional

from datetime import datetime

class APIClient:
    """Centralized API client for making requests"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Optional[dict]:
        """GET request with optional headers"""
        try:
            # Default auth header if token exists and no headers provided
            request_headers = headers or {}
            token = app.storage.user.get("token")
            if token:
                request_headers["Authorization"] = f"Bearer {token}"

            response = await self.client.get(
                f"{self.base_url}{endpoint}", params=params, headers=request_headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            ui.notify(f"API Error: {str(e)}", color="negative")
        return None

    async def post(self, endpoint: str, data: dict):
        """POST request"""
        try:
            response = await self.client.post(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            ui.notify(f"API Error: {str(e)}", color="negative")
            return None

    async def put(self, endpoint: str, data: dict):
        """PUT request"""
        try:
            response = await self.client.put(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            ui.notify(f"API Error: {str(e)}", color="negative")
            return None

    async def delete(self, endpoint: str):
        """DELETE request"""
        try:
            response = await self.client.delete(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            ui.notify(f"API Error: {str(e)}", color="negative")
            return None


api = APIClient(base_url="http://localhost:5000")




async def get_pps_ave_diff():
    result = await api.get("/api/v1/pps")
    if result and "pps" in result:
        return result["pps"]