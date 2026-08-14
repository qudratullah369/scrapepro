"""Core processing pipeline for ScrapePro."""


class Pipeline:
    """Execute processing steps in sequence."""

    def __init__(self) -> None:
        """Initialize an empty pipeline."""
        self.steps = []

    def add(self, step) -> None:
        """Add a processing step to the pipeline."""
        self.steps.append(step)

    def run(self, data):
        """Run all pipeline steps against the provided data."""
        result = data

        for step in self.steps:
            result = step(result)

        return result
