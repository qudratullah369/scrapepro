import pytest

from scrapepro.requests.fields import (
    ALLOWED_FIELDS,
    FieldRequirement,
)


def test_field_requirement_accepts_required_field():
    requirement = FieldRequirement("website")

    assert requirement.name == "website"
    assert requirement.required is True


def test_field_requirement_accepts_optional_field():
    requirement = FieldRequirement(
        "phone",
        required=False,
    )

    assert requirement.name == "phone"
    assert requirement.required is False


def test_field_requirement_rejects_unknown_field():
    with pytest.raises(
        ValueError,
        match="Unsupported data field: email",
    ):
        FieldRequirement("email")


def test_allowed_fields_are_defined():
    assert "name" in ALLOWED_FIELDS
    assert "website" in ALLOWED_FIELDS
    assert "country" in ALLOWED_FIELDS
