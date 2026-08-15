from scrapepro.core.engine import ScrapeEngine
from scrapepro.core.pipeline import Pipeline
from scrapepro.core.task import ScrapeTask
from scrapepro.processors.cleaner import Cleaner
from scrapepro.processors.normalizer import Normalizer
from scrapepro.scrapers.google_maps import GoogleMapsScraper


class MockResolver:
    def resolve(self, location):
        return (33.6844, 73.0479)


class MockClient:
    def search_text(self, query, lat, lng, radius=5000):
        return [
            {
                "displayName": {"text": "  Cafe A  "},
                "formattedAddress": "  Main St  ",
                "rating": 4.7,
                "userRatingCount": 120,
                "id": "p1",
                "internationalPhoneNumber": "+923001234567",
                "websiteUri": "https://example.com",
                "location": {
                    "latitude": 33.6844,
                    "longitude": 73.0479,
                },
                "types": ["cafe"],
            },
            {
                "displayName": {"text": "  Restaurant B  "},
                "formattedAddress": "  Second St  ",
                "rating": 3.9,
                "userRatingCount": 45,
                "id": "p2",
                "internationalPhoneNumber": "+923009876543",
                "websiteUri": "https://example2.com",
                "location": {
                    "latitude": 33.6844,
                    "longitude": 73.0479,
                },
                "types": ["restaurant"],
            },
        ]


def test_google_maps_full_integration():
    scraper = GoogleMapsScraper(
        api_key="dummy",
        client=MockClient(),
        resolver=MockResolver(),
    )

    pipeline = Pipeline()
    pipeline.add(Cleaner())
    pipeline.add(Normalizer())

    engine = ScrapeEngine(
        scraper=scraper,
        pipeline=pipeline,
    )

    task = ScrapeTask(
        source="google_maps",
        query="restaurants",
        location="Islamabad",
    )

    result = engine.run(task)

    assert result.success is True
    assert result.errors == []
    assert result.count == 2

    assert result.records[0].name == "Cafe A"
    assert result.records[0].address == "Main St"
    assert result.records[0].rating == 4.7
    assert result.records[0].category == "cafe"

    assert result.records[1].name == "Restaurant B"
    assert result.records[1].address == "Second St"
    assert result.records[1].rating == 3.9
    assert result.records[1].category == "restaurant"
