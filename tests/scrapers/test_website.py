from scrapepro.core.task import ScrapeTask
from scrapepro.scrapers.website import WebsiteScraper


class FakeResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        pass


def test_website_scraper_extracts_title(monkeypatch):
    def fake_get(url, timeout, headers):
        assert url == "https://example.com"
        assert timeout == 15
        assert "User-Agent" in headers

        return FakeResponse(
            """
            <html>
                <head>
                    <title>Example Business</title>
                </head>
                <body>
                    <h1>Example Heading</h1>
                </body>
            </html>
            """
        )

    monkeypatch.setattr(
        "scrapepro.scrapers.website.requests.get",
        fake_get,
    )

    scraper = WebsiteScraper()

    task = ScrapeTask(
        source="website",
        query="https://example.com",
    )

    result = scraper.scrape(task)

    assert result.success is True
    assert result.count == 1
    assert result.errors == []

    record = result.records[0]

    assert record.name == "Example Business"
    assert record.website == "https://example.com"
    assert record.source == "website"


def test_website_scraper_uses_h1_when_title_missing(monkeypatch):
    def fake_get(url, timeout, headers):
        return FakeResponse(
            """
            <html>
                <body>
                    <h1>My Business</h1>
                </body>
            </html>
            """
        )

    monkeypatch.setattr(
        "scrapepro.scrapers.website.requests.get",
        fake_get,
    )

    scraper = WebsiteScraper()

    task = ScrapeTask(
        source="website",
        query="https://example.com/business",
    )

    result = scraper.scrape(task)

    assert result.success is True
    assert result.records[0].name == "My Business"


def test_website_scraper_requires_url():
    scraper = WebsiteScraper()

    task = ScrapeTask(
        source="website",
        query="",
    )

    result = scraper.scrape(task)

    assert result.success is False
    assert result.count == 0
    assert result.errors == ["Website URL is required."]


def test_website_scraper_handles_request_error(monkeypatch):
    def fake_get(url, timeout, headers):
        import requests

        raise requests.RequestException("connection failed")

    monkeypatch.setattr(
        "scrapepro.scrapers.website.requests.get",
        fake_get,
    )

    scraper = WebsiteScraper()

    task = ScrapeTask(
        source="website",
        query="https://example.com",
    )

    result = scraper.scrape(task)

    assert result.success is False
    assert result.count == 0
    assert "Website request failed: connection failed" in result.errors[0]
