from scrapepro.core.task import ScrapeTask
from scrapepro.scrapers.ecommerce import EcommerceScraper


class FakeResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        pass


def test_ecommerce_scraper_extracts_product(monkeypatch):
    def fake_get(url, timeout, headers):
        assert url == "https://example.com/product"
        assert timeout == 15
        assert "User-Agent" in headers

        return FakeResponse(
            """
            <html>
                <head>
                    <script type="application/ld+json">
                    {
                        "@context": "https://schema.org",
                        "@type": "Product",
                        "name": "Test Coffee",
                        "category": "Coffee",
                        "aggregateRating": {
                            "ratingValue": "4.5",
                            "reviewCount": "120"
                        },
                        "offers": {
                            "price": "1499",
                            "priceCurrency": "PKR"
                        }
                    }
                    </script>
                </head>
            </html>
            """
        )

    monkeypatch.setattr(
        "scrapepro.scrapers.ecommerce.requests.get",
        fake_get,
    )

    scraper = EcommerceScraper()

    result = scraper.scrape(
        ScrapeTask(
            source="ecommerce",
            query="https://example.com/product",
        )
    )

    assert result.success is True
    assert result.count == 1
    assert result.errors == []

    record = result.records[0]

    assert record.name == "Test Coffee"
    assert record.category == "Coffee"
    assert record.website == "https://example.com/product"
    assert record.source == "ecommerce"
    assert record.rating == 4.5
    assert record.reviews == 120


def test_ecommerce_scraper_supports_graph(monkeypatch):
    def fake_get(url, timeout, headers):
        return FakeResponse(
            """
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@graph": [
                    {
                        "@type": "WebPage",
                        "name": "Product Page"
                    },
                    {
                        "@type": "Product",
                        "name": "Graph Product"
                    }
                ]
            }
            </script>
            """
        )

    monkeypatch.setattr(
        "scrapepro.scrapers.ecommerce.requests.get",
        fake_get,
    )

    result = EcommerceScraper().scrape(
        ScrapeTask(
            source="ecommerce",
            query="https://example.com/product",
        )
    )

    assert result.success is True
    assert result.records[0].name == "Graph Product"


def test_ecommerce_scraper_requires_url():
    result = EcommerceScraper().scrape(
        ScrapeTask(
            source="ecommerce",
            query="",
        )
    )

    assert result.success is False
    assert result.count == 0
    assert result.errors == ["Product URL is required."]


def test_ecommerce_scraper_handles_request_error(monkeypatch):
    def fake_get(url, timeout, headers):
        import requests

        raise requests.RequestException("connection failed")

    monkeypatch.setattr(
        "scrapepro.scrapers.ecommerce.requests.get",
        fake_get,
    )

    result = EcommerceScraper().scrape(
        ScrapeTask(
            source="ecommerce",
            query="https://example.com/product",
        )
    )

    assert result.success is False
    assert result.count == 0
    assert (
        "E-commerce request failed: connection failed"
        in result.errors[0]
    )


def test_ecommerce_scraper_handles_missing_product(monkeypatch):
    def fake_get(url, timeout, headers):
        return FakeResponse(
            """
            <html>
                <head>
                    <title>No Product</title>
                </head>
            </html>
            """
        )

    monkeypatch.setattr(
        "scrapepro.scrapers.ecommerce.requests.get",
        fake_get,
    )

    result = EcommerceScraper().scrape(
        ScrapeTask(
            source="ecommerce",
            query="https://example.com/no-product",
        )
    )

    assert result.success is False
    assert result.count == 0
    assert result.errors == [
        "No Product structured data found."
    ]
