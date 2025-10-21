from types import SimpleNamespace

from mark_lang.brand_center.api_client import BrandCenterClient, BrandGuidelines, BrandCenterError


class DummyResponse:
    def __init__(self, status_code: int, payload: dict | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self) -> dict:
        return self._payload


class DummySession:
    def __init__(self, response: DummyResponse):
        self.response = response
        self.last_request = None

    def request(self, method, url, headers=None, timeout=None):
        self.last_request = SimpleNamespace(method=method, url=url, headers=headers, timeout=timeout)
        return self.response


def test_fetch_guidelines_success():
    response = DummyResponse(
        200,
        {
            "tone_of_voice": "Friendly",
            "visual_style": "Bold",
            "compliance_notes": "GDPR compliant",
        },
    )
    client = BrandCenterClient(base_url="https://brand", api_key="token", session=DummySession(response))
    guidelines = client.fetch_guidelines("dnb")
    assert isinstance(guidelines, BrandGuidelines)
    assert guidelines.visual_style == "Bold"


def test_fetch_guidelines_error_raises():
    response = DummyResponse(403, {"detail": "Forbidden"})
    client = BrandCenterClient(base_url="https://brand", api_key="token", session=DummySession(response))
    try:
        client.fetch_guidelines("dnb")
    except BrandCenterError as exc:
        assert "Access denied" in str(exc)
    else:  # pragma: no cover - ensures failure if no exception
        raise AssertionError("Expected BrandCenterError")
