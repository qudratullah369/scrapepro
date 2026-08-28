from scrapepro.core.task import ScrapeTask
from scrapepro.requests.specification import DataSpecification
from scrapepro.requests.task_builder import TaskBuilder


def test_task_builder_creates_google_maps_task():
    specification = DataSpecification(
        category="Restaurants",
        location="Islamabad",
        source="google_maps",
        output="csv",
    )

    task = TaskBuilder().build(specification)

    assert isinstance(task, ScrapeTask)
    assert task.source == "google_maps"
    assert task.query == "Restaurants"
    assert task.location == "Islamabad"
    assert task.output == "csv"


def test_task_builder_defaults_to_google_maps():
    specification = DataSpecification(
        category="Hotels",
        location="Lahore",
    )

    task = TaskBuilder().build(specification)

    assert task.source == "google_maps"
    assert task.query == "Hotels"
    assert task.location == "Lahore"


def test_task_builder_supports_website():
    specification = DataSpecification(
        category="https://example.com",
        source="website",
    )

    task = TaskBuilder().build(specification)

    assert task.source == "website"
    assert task.query == "https://example.com"


def test_task_builder_supports_ecommerce():
    specification = DataSpecification(
        category="https://example.com/product",
        source="ecommerce",
    )

    task = TaskBuilder().build(specification)

    assert task.source == "ecommerce"
    assert task.query == "https://example.com/product"


def test_task_builder_rejects_invalid_source():
    specification = DataSpecification(
        category="Restaurants",
        source="unknown",
    )

    try:
        TaskBuilder().build(specification)
    except ValueError as error:
        assert str(error) == "Unsupported scraping source: unknown"
    else:
        raise AssertionError("Expected ValueError")


def test_task_builder_passes_fields_and_limit():
    specification = DataSpecification(
        category="Restaurants",
        location="Islamabad",
        fields=["name", "phone", "website"],
        limit=100,
        source="google_maps",
        output="csv",
    )

    task = TaskBuilder().build(specification)

    assert task.fields == ["name", "phone", "website"]
    assert task.limit == 100
