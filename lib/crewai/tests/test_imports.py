"""Test that all public API classes are properly importable."""

from crewai import CrewOutput, TaskOutput
from crewai.crews import crew_output
from crewai.tasks import task_output


def test_task_output_import():
    """Test that TaskOutput can be imported from crewai."""
    assert TaskOutput is task_output.TaskOutput


def test_crew_output_import():
    """Test that CrewOutput can be imported from crewai."""
    assert CrewOutput is crew_output.CrewOutput
