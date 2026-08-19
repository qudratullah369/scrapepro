import pytest
from pydantic import ValidationError

from scrapepro.api.request_schemas import DataRequestBody


def test_data_request_body_accepts_valid_request():
    request = DataRequestBody(
        category="Restaurants",
        location="Islamabad",
        fields=["name", "phone", "website"],
        limit=100,
        source="google_maps",
        output="csv",
    )

    assert request.category == "Restaurants"
    assert request.location == "Islamabad"
    assert request.fields == ["name", "phone", "website"]
    assert request.limit == 100
    assert request.source == "google_maps"
    assert request.output == "csv"


def test_data_request_body_defaults_optional_values():
    request = DataRequestBody(category="Restaurants")

    assert request.location is None
    assert request.fields == []
    assert request.limit is None
    assert request.source is None
    assert request.output is None


def test_data_request_body_rejects_invalid_limit():
    with pytest.raises(ValidationError):
        DataRequestBody(
            category="Restaurants",
            limit=0,
        )


def test_data_request_body_rejects_invalid_source():
    with pytest.raises(ValidationError):
        DataRequestBody(
            category="Restaurants",
            source="unknown",
        )


def test_data_request_body_rejects_invalid_output():
    with pytest.raises(ValidationError):
        DataRequestBody(
            category="Restaurants",
            output="pdf",
        )
