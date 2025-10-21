"""Brand Centre connectivity adhering to DNB security requirements."""
from __future__ import annotations

import json
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, Optional, Protocol

try:  # pragma: no cover - optional dependency
    import requests  # type: ignore
except Exception:  # pragma: no cover - fallback to stdlib
    requests = None

import urllib.request


class SupportsRequest(Protocol):  # pragma: no cover - structural typing helper
    def request(self, method: str, url: str, headers: Dict[str, str], timeout: int) -> Any: ...


class BrandCenterError(RuntimeError):
    """Raised when guideline retrieval fails."""


@dataclass
class BrandGuidelines:
    """Encapsulate the guidelines returned by the Brand Centre."""

    tone_of_voice: str
    visual_style: str
    compliance_notes: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "tone_of_voice": self.tone_of_voice,
            "visual_style": self.visual_style,
            "compliance_notes": self.compliance_notes,
        }


class _UrlLibSession:
    """Minimal HTTP session using the standard library."""

    def request(self, method: str, url: str, headers: Dict[str, str], timeout: int):
        request = urllib.request.Request(url, method=method, headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
            payload = response.read()
            text = payload.decode()
            return SimpleNamespace(
                status_code=response.status,
                text=text,
                json=lambda: json.loads(text or "{}"),
            )


class BrandCenterClient:
    """Simple connector that enforces privacy and security controls."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        session: Optional[SupportsRequest] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        if session is not None:
            self.session = session
        elif requests is not None:  # pragma: no cover - environment-dependent
            self.session = requests.Session()
        else:
            self.session = _UrlLibSession()

    def fetch_guidelines(self, brand_id: str) -> BrandGuidelines:
        """Retrieve brand guidelines, ensuring sensitive data is safeguarded."""

        response = self._request("GET", f"/brands/{brand_id}/guidelines")
        payload = response.json()
        return BrandGuidelines(
            tone_of_voice=payload.get("tone_of_voice", ""),
            visual_style=payload.get("visual_style", ""),
            compliance_notes=payload.get("compliance_notes", ""),
        )

    def _request(self, method: str, path: str):
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = self.session.request(method, url, headers=headers, timeout=10)
        self._validate_response(response)
        return response

    def _validate_response(self, response) -> None:
        status_code = getattr(response, "status_code", 500)
        if status_code == 401:
            raise BrandCenterError("Authentication with Brand Centre failed")
        if status_code == 403:
            raise BrandCenterError("Access denied by Brand Centre policies")
        if status_code >= 400:
            detail = self._extract_error_detail(response)
            raise BrandCenterError(f"Brand Centre error {status_code}: {detail}")

    def _extract_error_detail(self, response) -> str:
        try:
            return response.json().get("detail", response.text)
        except Exception:  # pragma: no cover - safe fallback
            return getattr(response, "text", "")
