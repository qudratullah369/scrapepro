"""Configuration settings for ScrapePro."""

import os


class Settings:
    """Application configuration loaded from environment variables."""

    def __init__(self) -> None:
        self.google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    def require_google_maps_api_key(self) -> str:
        """Return the Google Maps API key or raise a clear error."""
        if not self.google_maps_api_key:
            raise ValueError(
                "GOOGLE_MAPS_API_KEY environment variable is not set."
            )

        return self.google_maps_api_key
