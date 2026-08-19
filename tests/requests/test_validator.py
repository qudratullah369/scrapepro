import pytest

from scrapepro.requests.fields import FieldRequirement
from scrapepro.requests.specification import DataSpecification
from scrapepro.requests.validator import RequestValidator


def test_request_validator_accepts_valid_request():
    specification = DataSpecification(
        category="Restaurants",
        location="Islamabad",
        fields=[
            FieldRequirement("name"),
            FieldRequirement("phone"),
            FieldRequirement("website"),
        ],
        limit=100,
        source="google_maps",
        output="csv",
    )

    result = RequestValidator().validate(specification)

    assert result is specification


def test_request_validator_accepts_all_supported_sources():
    validator = RequestValidator()

    for source in ("google_maps", "website", "ecommerce"):
        specification = DataSpecification(
            category="Businesses",
            source=source,
        )

        assert validator.validate(specification) is specification


def test_request_validator_rejects_unsupported_source():
    specification = DataSpecification(
        category="Businesses",
        source="unknown",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported scraping source: unknown",
    ):
        RequestValidator().validate(specification)


def test_request_validator_rejects_duplicate_fields():
    specification = DataSpecification(
        category="Restaurants",
        fields=[
            FieldRequirement("name"),
            FieldRequirement("phone"),
            FieldRequirement("name"),
        ],
    )

    with pytest.raises(
        ValueError,
        match="Duplicate data fields are not allowed.",
    ):
        RequestValidator().validate(specification)
