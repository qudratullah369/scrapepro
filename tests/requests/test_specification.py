import pytest

from scrapepro.requests.specification import DataSpecification


def test_data_specification_accepts_business_request():
    specification = DataSpecification(
        category="SaaS companies",
        location="United States",
        fields=["name", "website", "category"],
        limit=500,
        output="csv",
    )

    assert specification.category == "SaaS companies"
    assert specification.location == "United States"
    assert specification.fields == [
        "name",
        "website",
        "category",
    ]
    assert specification.limit == 500
    assert specification.output == "csv"


def test_data_specification_rejects_empty_category():
    with pytest.raises(ValueError, match="Category is required."):
        DataSpecification(category="   ")


def test_data_specification_rejects_invalid_limit():
    with pytest.raises(
        ValueError,
        match="Limit must be greater than zero.",
    ):
        DataSpecification(
            category="Hotels",
            limit=0,
        )


def test_data_specification_rejects_invalid_output():
    with pytest.raises(
        ValueError,
        match="Output must be csv, json, or excel.",
    ):
        DataSpecification(
            category="Hotels",
            output="pdf",
        )
