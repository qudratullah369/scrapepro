from scrapepro.core.engine import ScrapeEngine
from scrapepro.core.pipeline import Pipeline
from scrapepro.core.task import ScrapeTask
from scrapepro.processors.cleaner import Cleaner
from scrapepro.processors.normalizer import Normalizer
from scrapepro.scrapers.google_maps import GoogleMapsScraper
from scrapepro.scrapers.google_maps_client import GoogleMapsClient


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

class MockPageResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


class MockPageSession:
    def __init__(self):
        self.headers = {}
        self.calls = []

    def post(self, url, json=None, timeout=30):
        self.calls.append(json)

        if len(self.calls) == 1:
            return MockPageResponse({
                "places": [
                    {
                        "displayName": {"text": "Cafe A"},
                        "id": "p1",
                    }
                ],
                "nextPageToken": "TOKEN_PAGE_2",
            })

        return MockPageResponse({
            "places": [
                {
                    "displayName": {"text": "Cafe B"},
                    "id": "p2",
                }
            ]
        })


def test_google_maps_client_pagination():
    client = GoogleMapsClient("dummy-api-key")

    session = MockPageSession()
    client.session = session

    result = client.search_text(
        query="restaurants",
        lat=31.5204,
        lng=74.3587,
        max_pages=3,
    )

    assert len(result) == 2
    assert result[0]["displayName"]["text"] == "Cafe A"
    assert result[1]["displayName"]["text"] == "Cafe B"

    assert len(session.calls) == 2
    assert session.calls[1]["pageToken"] == "TOKEN_PAGE_2"


def test_google_maps_client_max_pages():
    client = GoogleMapsClient("dummy-api-key")

    session = MockPageSession()
    client.session = session

    result = client.search_text(
        query="restaurants",
        lat=31.5204,
        lng=74.3587,
        max_pages=1,
    )

    assert len(result) == 1
    assert result[0]["displayName"]["text"] == "Cafe A"
    assert len(session.calls) == 1


def test_google_maps_client_invalid_max_pages():
    client = GoogleMapsClient("dummy-api-key")

    try:
        client.search_text(
            query="restaurants",
            lat=31.5204,
            lng=74.3587,
            max_pages=0,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "max_pages must be at least 1."
