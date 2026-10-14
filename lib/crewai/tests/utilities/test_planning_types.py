"""Tests for planning types (PlanStep, TodoItem, TodoList)."""

import pytest
from uuid import UUID

from crewai.utilities.planning_types import (
    PlanStep,
    TodoItem,
    TodoList,
    TodoStatus,
)


class TestPlanStep:
    """Tests for the PlanStep model."""

    def test_plan_step_with_required_fields(self):
        """Test PlanStep creation with only required fields."""
        step = PlanStep(
            step_number=1,
            description="Research the topic",
        )

        assert step.step_number == 1
        assert step.description == "Research the topic"
        assert step.tool_to_use is None
        assert step.depends_on == []

    def test_plan_step_requires_step_number(self):
        """Test that step_number is required."""
        with pytest.raises(ValueError):
            PlanStep(description="Missing step number")

    def test_plan_step_requires_description(self):
        """Test that description is required."""
        with pytest.raises(ValueError):
            PlanStep(step_number=1)


class TestTodoItem:
    """Tests for the TodoItem model."""

    def test_todo_item_with_required_fields(self):
        """Test TodoItem creation with only required fields."""
        todo = TodoItem(
            step_number=1,
            description="First task",
        )

        assert todo.step_number == 1
        assert todo.description == "First task"
        assert todo.status == "pending"
        assert todo.tool_to_use is None
        assert todo.depends_on == []
        assert todo.result is None
        # ID should be auto-generated
        assert todo.id is not None
        UUID(todo.id)

    def test_todo_item_rejects_unknown_status(self):
        """Test that status is limited to pending, running, and completed."""
        with pytest.raises(ValueError):
            TodoItem(step_number=1, description="Test", status="done")

    def test_todo_item_auto_generates_unique_ids(self):
        """Test that each TodoItem gets a unique auto-generated ID."""
        todo1 = TodoItem(step_number=1, description="Task 1")
        todo2 = TodoItem(step_number=2, description="Task 2")

        assert todo1.id != todo2.id


class TestTodoList:
    """Tests for the TodoList model."""

    @pytest.fixture
    def empty_todo_list(self):
        """Create an empty TodoList."""
        return TodoList()

    @pytest.fixture
    def sample_todo_list(self):
        """Create a TodoList with sample items."""
        return TodoList(
            items=[
                TodoItem(step_number=1, description="Step 1", status="completed"),
                TodoItem(step_number=2, description="Step 2", status="running"),
                TodoItem(step_number=3, description="Step 3", status="pending"),
                TodoItem(step_number=4, description="Step 4", status="pending"),
            ]
        )

    def test_empty_todo_list(self, empty_todo_list):
        """Test empty TodoList properties."""
        assert empty_todo_list.items == []
        assert empty_todo_list.current_todo is None
        assert empty_todo_list.next_pending is None
        assert empty_todo_list.is_complete is False
        assert empty_todo_list.pending_count == 0
        assert empty_todo_list.completed_count == 0

    def test_current_todo_property(self, sample_todo_list):
        """Test current_todo returns the running item."""
        current = sample_todo_list.current_todo
        assert current is not None
        assert current.step_number == 2
        assert current.status == "running"

    def test_current_todo_returns_none_when_no_running(self):
        """Test current_todo returns None when no running items."""
        todo_list = TodoList(
            items=[
                TodoItem(step_number=1, description="Step 1", status="completed"),
                TodoItem(step_number=2, description="Step 2", status="pending"),
            ]
        )
        assert todo_list.current_todo is None

    def test_next_pending_property(self, sample_todo_list):
        """Test next_pending returns the first pending item."""
        next_item = sample_todo_list.next_pending
        assert next_item is not None
        assert next_item.step_number == 3
        assert next_item.status == "pending"

    def test_next_pending_returns_none_when_no_pending(self):
        """Test next_pending returns None when no pending items."""
        todo_list = TodoList(
            items=[
                TodoItem(step_number=1, description="Step 1", status="completed"),
                TodoItem(step_number=2, description="Step 2", status="completed"),
            ]
        )
        assert todo_list.next_pending is None

    def test_is_complete_property_when_complete(self):
        """Test is_complete returns True when all items completed."""
        todo_list = TodoList(
            items=[
                TodoItem(step_number=1, description="Step 1", status="completed"),
                TodoItem(step_number=2, description="Step 2", status="completed"),
            ]
        )
        assert todo_list.is_complete is True

    def test_is_complete_property_when_not_complete(self, sample_todo_list):
        """Test is_complete returns False when items are pending."""
        assert sample_todo_list.is_complete is False

    def test_is_complete_false_for_empty_list(self, empty_todo_list):
        """Test is_complete returns False for empty list."""
        assert empty_todo_list.is_complete is False

    def test_pending_count(self, sample_todo_list):
        """Test pending_count returns correct count."""
        assert sample_todo_list.pending_count == 2

    def test_completed_count(self, sample_todo_list):
        """Test completed_count returns correct count."""
        assert sample_todo_list.completed_count == 1

    def test_get_by_step_number(self, sample_todo_list):
        """Test get_by_step_number returns correct item."""
        item = sample_todo_list.get_by_step_number(3)
        assert item is not None
        assert item.step_number == 3
        assert item.description == "Step 3"

    def test_get_by_step_number_returns_none_for_missing(self, sample_todo_list):
        """Test get_by_step_number returns None for non-existent step."""
        item = sample_todo_list.get_by_step_number(99)
        assert item is None

    def test_mark_running(self, sample_todo_list):
        """Test mark_running changes status correctly."""
        sample_todo_list.mark_running(3)
        item = sample_todo_list.get_by_step_number(3)
        assert item.status == "running"

    def test_mark_running_does_nothing_for_missing(self, sample_todo_list):
        """Test mark_running handles missing step gracefully."""
        sample_todo_list.mark_running(99)

        assert [item.status for item in sample_todo_list.items] == [
            "completed",
            "running",
            "pending",
            "pending",
        ]

    def test_mark_completed(self, sample_todo_list):
        """Test mark_completed changes status correctly."""
        sample_todo_list.mark_completed(3)
        item = sample_todo_list.get_by_step_number(3)
        assert item.status == "completed"
        assert item.result is None

    def test_mark_completed_with_result(self, sample_todo_list):
        """Test mark_completed with result."""
        sample_todo_list.mark_completed(3, result="Task output")
        item = sample_todo_list.get_by_step_number(3)
        assert item.status == "completed"
        assert item.result == "Task output"

    def test_mark_completed_does_nothing_for_missing(self, sample_todo_list):
        """Test mark_completed handles missing step gracefully."""
        sample_todo_list.mark_completed(99, result="Some result")

        assert [
            (item.status, item.result) for item in sample_todo_list.items
        ] == [
            ("completed", None),
            ("running", None),
            ("pending", None),
            ("pending", None),
        ]

    def test_todo_list_workflow(self):
        """Test a complete workflow through TodoList."""
        todo_list = TodoList(
            items=[
                TodoItem(
                    step_number=1,
                    description="Research",
                    tool_to_use="search_tool",
                ),
                TodoItem(
                    step_number=2,
                    description="Analyze",
                    depends_on=[1],
                ),
                TodoItem(
                    step_number=3,
                    description="Report",
                    depends_on=[1, 2],
                ),
            ]
        )

        # Initial state
        assert todo_list.pending_count == 3
        assert todo_list.completed_count == 0
        assert todo_list.is_complete is False

        todo_list.mark_running(1)
        assert todo_list.current_todo.step_number == 1
        assert todo_list.next_pending.step_number == 2

        # Complete first task
        todo_list.mark_completed(1, result="Research done")
        assert todo_list.current_todo is None
        assert todo_list.completed_count == 1

        todo_list.mark_running(2)
        todo_list.mark_completed(2, result="Analysis complete")
        assert todo_list.completed_count == 2

        todo_list.mark_running(3)
        todo_list.mark_completed(3, result="Report generated")

        # Final state
        assert todo_list.is_complete is True
        assert todo_list.pending_count == 0
        assert todo_list.completed_count == 3
        assert todo_list.current_todo is None
        assert todo_list.next_pending is None
