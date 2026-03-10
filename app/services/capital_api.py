from __future__ import annotations

from typing import Any

import httpx


class CapitalComClient:
    """Minimal Capital.com API client focused on trade history sync."""

    def __init__(
        self,
        api_key: str,
        identifier: str,
        password: str,
        demo_mode: bool = True,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.base_url = base_url or (
            "https://demo-api-capital.backend-capital.com/api/v1"
            if demo_mode
            else "https://api-capital.backend-capital.com/api/v1"
        )

    async def _auth_headers(self) -> dict[str, str]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/session",
                headers={"X-CAP-API-KEY": self.api_key},
                json={"identifier": self.identifier, "password": self.password},
            )
            response.raise_for_status()
            cst = response.headers.get("CST", "")
            security_token = response.headers.get("X-SECURITY-TOKEN", "")
            return {
                "X-CAP-API-KEY": self.api_key,
                "CST": cst,
                "X-SECURITY-TOKEN": security_token,
            }

    async def fetch_closed_positions(self, limit: int = 200) -> list[dict[str, Any]]:
        headers = await self._auth_headers()
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/positions",
                headers=headers,
                params={"status": "CLOSED", "limit": limit},
            )
            response.raise_for_status()
            payload = response.json()
            return payload.get("positions", payload if isinstance(payload, list) else [])
