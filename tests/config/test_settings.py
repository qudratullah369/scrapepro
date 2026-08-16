import pytest

from scrapepro.config.settings import Settings


def test_settings_reads_google_maps_api_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test-api-key")

    settings = Settings()

    assert settings.google_maps_api_key == "test-api-key"
    assert settings.require_google_maps_api_key() == "test-api-key"


def test_settings_requires_google_maps_api_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)

    settings = Settings()

    with pytest.raises(
        ValueError,
        match="GOOGLE_MAPS_API_KEY environment variable is not set",
    ):
        settings.require_google_maps_api_key()
