"""Core processing pipeline for ScrapePro."""

from scrapepro.processors.base import BaseProcessor


class Pipeline:
    """Execute processing steps in sequence."""

    def __init__(self) -> None:
        """Initialize an empty pipeline."""
        self.steps: list[BaseProcessor] = []

    def add(self, step: BaseProcessor) -> None:
        """Add a processor to the pipeline."""
        self.steps.append(step)

    def run(self, data):
        """Run all processors against the provided data."""
        result = data

        for step in self.steps:
            result = step.process(result)

        return result
