from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class CapitalAPIError(Exception):
    message: str
    status_code: int = 400


def _extract_error_code(response: httpx.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return str(payload.get("errorCode") or payload.get("message") or "")
    except Exception:
        pass
    return ""

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

    @staticmethod
    def _map_http_error(exc: httpx.HTTPStatusError) -> CapitalAPIError:
        code = exc.response.status_code
        api_reason = _extract_error_code(exc.response)
        suffix = f" API-Reason: {api_reason}" if api_reason else ""
        if code == 401:
            return CapitalAPIError(
                "Capital.com Login fehlgeschlagen (401). Prüfe API-Key, Identifier, Passwort, ob Demo/Live korrekt gesetzt ist und ob der API-Key für dieses Konto freigeschaltet ist." + suffix,
                status_code=401,
            )
        if code == 429:
            return CapitalAPIError(
                "Capital.com Rate Limit erreicht (429). Bitte 30-60 Sekunden warten und erneut synchronisieren." + suffix,
                status_code=429,
            )
        return CapitalAPIError(
            f"Capital.com API Fehler ({code}). Bitte später erneut versuchen." + suffix,
            status_code=400,
        )

    async def _auth_headers(self) -> dict[str, str]:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    f"{self.base_url}/session",
                    headers={
                        "X-CAP-API-KEY": self.api_key,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
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
        except httpx.HTTPStatusError as exc:
            raise self._map_http_error(exc) from exc
        except httpx.HTTPError as exc:
            raise CapitalAPIError("Netzwerkfehler bei Capital.com. Bitte Verbindung prüfen.", status_code=502) from exc

    async def fetch_closed_positions(self, limit: int = 200) -> list[dict[str, Any]]:
        headers = await self._auth_headers()
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(
                    f"{self.base_url}/positions",
                    headers=headers,
                    params={"status": "CLOSED", "limit": limit},
                )
                response.raise_for_status()
                payload = response.json()
                return payload.get("positions", payload if isinstance(payload, list) else [])
        except httpx.HTTPStatusError as exc:
            raise self._map_http_error(exc) from exc
        except httpx.HTTPError as exc:
            raise CapitalAPIError("Netzwerkfehler beim Abruf der Positionen.", status_code=502) from exc
