"""Client request validation for ScrapePro."""

from scrapepro.requests.specification import DataSpecification


SUPPORTED_SOURCES = frozenset(
    {
        "google_maps",
        "website",
        "ecommerce",
    }
)


class RequestValidator:
    """Validate a client data specification."""

    def validate(self, specification: DataSpecification) -> DataSpecification:
        """Validate and return a client data specification."""
        self._validate_source(specification)
        self._validate_fields(specification)

        return specification

    @staticmethod
    def _validate_source(specification: DataSpecification) -> None:
        """Validate the requested scraping source."""
        if (
            specification.source is not None
            and specification.source not in SUPPORTED_SOURCES
        ):
            raise ValueError(
                f"Unsupported scraping source: {specification.source}"
            )

    @staticmethod
    def _validate_fields(specification: DataSpecification) -> None:
        """Validate requested fields."""
        names = [field.name for field in specification.fields]

        if len(names) != len(set(names)):
            raise ValueError("Duplicate data fields are not allowed.")
