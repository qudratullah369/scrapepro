"""API schemas for client data requests."""

from pydantic import BaseModel, Field


class DataRequestBody(BaseModel):
    """Request body submitted by a client."""

    category: str = Field(..., min_length=1)
    location: str | None = None
    fields: list[str] = Field(default_factory=list)
    limit: int | None = Field(None, ge=1)
    source: str | None = Field(
        None,
        pattern="^(google_maps|website|ecommerce)$",
    )
    output: str | None = Field(
        None,
        pattern="^(csv|excel|json)$",
    )


class DataRequestResponse(BaseModel):
    """Response returned for a client data request."""

    count: int
    errors: list[str]
    records: list[dict]
    output: str | None = None
