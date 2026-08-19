import pytest

from scrapepro.requests.fields import FieldRequirement
from scrapepro.requests.specification import DataSpecification


def test_data_specification_accepts_business_request():
    specification = DataSpecification(
        category="SaaS companies",
        location="United States",
        fields=[
            FieldRequirement("name"),
            FieldRequirement("website"),
            FieldRequirement("category"),
        ],
        limit=500,
        output="csv",
    )

    assert specification.category == "SaaS companies"
    assert specification.location == "United States"
    assert [item.name for item in specification.fields] == [
        "name",
        "website",
        "category",
    ]
    assert all(item.required for item in specification.fields)
    assert specification.limit == 500
    assert specification.output == "csv"


def test_data_specification_converts_field_names():
    specification = DataSpecification(
        category="Hotels",
        fields=["name", "website"],
    )

    assert all(
        isinstance(item, FieldRequirement)
        for item in specification.fields
    )


def test_data_specification_accepts_optional_fields():
    specification = DataSpecification(
        category="Restaurants",
        fields=[
            FieldRequirement("name"),
            FieldRequirement("phone", required=False),
        ],
    )

    assert specification.fields[0].required is True
    assert specification.fields[1].required is False


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


def test_data_specification_rejects_unknown_field():
    with pytest.raises(
        ValueError,
        match="Unsupported data field: email",
    ):
        DataSpecification(
            category="SaaS companies",
            fields=["name", "email"],
        )
