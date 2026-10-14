"""Tests for human approval functionality in hooks."""

from __future__ import annotations

from unittest.mock import Mock, call, patch

from crewai.hooks.llm_hooks import LLMCallHookContext
from crewai.hooks.tool_hooks import ToolCallHookContext
import pytest


@pytest.fixture
def mock_executor():
    """Create a mock executor for LLM hook context."""
    executor = Mock()
    executor.messages = [{"role": "system", "content": "Test message"}]
    executor.agent = Mock(role="Test Agent")
    executor.task = Mock(description="Test Task")
    executor.crew = Mock()
    executor.llm = Mock()
    executor.iterations = 0
    return executor


@pytest.fixture
def mock_tool():
    """Create a mock tool for tool hook context."""
    tool = Mock()
    tool.name = "test_tool"
    tool.description = "Test tool description"
    return tool


@pytest.fixture
def mock_agent():
    """Create a mock agent."""
    agent = Mock()
    agent.role = "Test Agent"
    return agent


@pytest.fixture
def mock_task():
    """Create a mock task."""
    task = Mock()
    task.description = "Test task"
    return task


class TestLLMHookHumanInput:
    """Test request_human_input() on LLMCallHookContext."""

    @patch("builtins.input", return_value="test response")
    @patch("crewai.hooks.llm_hooks.event_listener")
    def test_request_human_input_returns_user_response(
        self, mock_event_listener, mock_input, mock_executor
    ):
        """Test that request_human_input returns the user's input."""
        mock_formatter = Mock()
        mock_event_listener.formatter = mock_formatter

        context = LLMCallHookContext(executor=mock_executor)

        with patch("crewai.hooks.llm_hooks.PRINTER") as mock_printer:
            response = context.request_human_input(
                prompt="Test prompt", default_message="Test default message"
            )

        assert response == "test response"
        mock_input.assert_called_once_with()
        assert mock_printer.print.call_args_list == [
            call(content="\nTest prompt", color="bold_yellow"),
            call(content="Test default message", color="cyan"),
            call(content="\nProcessing your input...", color="cyan"),
        ]

    @patch("builtins.input", return_value="")
    @patch("crewai.hooks.llm_hooks.event_listener")
    def test_request_human_input_returns_empty_string_on_enter(
        self, mock_event_listener, mock_input, mock_executor
    ):
        """Test that pressing Enter returns empty string."""
        mock_formatter = Mock()
        mock_event_listener.formatter = mock_formatter

        context = LLMCallHookContext(executor=mock_executor)

        with patch("crewai.hooks.llm_hooks.PRINTER") as mock_printer:
            response = context.request_human_input(prompt="Test")

        assert response == ""
        mock_input.assert_called_once_with()
        assert mock_printer.print.call_args_list == [
            call(content="\nTest", color="bold_yellow"),
            call(
                content="Press Enter to continue, or provide feedback:", color="cyan"
            ),
        ]

    @patch("builtins.input", return_value="test")
    @patch("crewai.hooks.llm_hooks.event_listener")
    def test_request_human_input_pauses_and_resumes_live_updates(
        self, mock_event_listener, mock_input, mock_executor
    ):
        """Test that live updates are paused and resumed."""
        mock_formatter = Mock()
        mock_event_listener.formatter = mock_formatter

        order: list[str] = []
        mock_formatter.pause_live_updates.side_effect = lambda: order.append("pause")
        mock_formatter.resume_live_updates.side_effect = lambda: order.append("resume")
        mock_input.side_effect = lambda: order.append("input") or "test"

        context = LLMCallHookContext(executor=mock_executor)

        context.request_human_input(prompt="Test")

        assert order == ["pause", "input", "resume"]

    @patch("builtins.input", side_effect=Exception("Input error"))
    @patch("crewai.hooks.llm_hooks.event_listener")
    def test_request_human_input_resumes_on_exception(
        self, mock_event_listener, mock_input, mock_executor
    ):
        """Test that live updates are resumed even if input raises exception."""
        mock_formatter = Mock()
        mock_event_listener.formatter = mock_formatter

        context = LLMCallHookContext(executor=mock_executor)

        with pytest.raises(Exception, match="Input error"):
            context.request_human_input(prompt="Test")

        mock_formatter.resume_live_updates.assert_called_once()

    @patch("builtins.input", return_value="  test response  ")
    @patch("crewai.hooks.llm_hooks.event_listener")
    def test_request_human_input_strips_whitespace(
        self, mock_event_listener, mock_input, mock_executor
    ):
        """Test that user input is stripped of leading/trailing whitespace."""
        mock_formatter = Mock()
        mock_event_listener.formatter = mock_formatter

        context = LLMCallHookContext(executor=mock_executor)

        response = context.request_human_input(prompt="Test")

        assert response == "test response"


class TestToolHookHumanInput:
    """Test request_human_input() on ToolCallHookContext."""

    @patch("builtins.input", return_value="approve")
    @patch("crewai.hooks.tool_hooks.event_listener")
    def test_request_human_input_returns_user_response(
        self, mock_event_listener, mock_input, mock_tool, mock_agent, mock_task
    ):
        """Test that request_human_input returns the user's input."""
        mock_formatter = Mock()
        mock_event_listener.formatter = mock_formatter

        context = ToolCallHookContext(
            tool_name="test_tool",
            tool_input={"arg": "value"},
            tool=mock_tool,
            agent=mock_agent,
            task=mock_task,
        )

        response = context.request_human_input(
            prompt="Approve this tool?", default_message="Type 'approve':"
        )

        assert response == "approve"
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="")
    @patch("crewai.hooks.tool_hooks.event_listener")
    def test_request_human_input_handles_empty_input(
        self, mock_event_listener, mock_input, mock_tool
    ):
        """Test that empty input (Enter key) is handled correctly."""
        mock_formatter = Mock()
        mock_event_listener.formatter = mock_formatter

        context = ToolCallHookContext(
            tool_name="test_tool",
            tool_input={},
            tool=mock_tool,
        )

        response = context.request_human_input(prompt="Test")

        assert response == ""

    @patch("builtins.input", return_value="test")
    @patch("crewai.hooks.tool_hooks.event_listener")
    def test_request_human_input_pauses_and_resumes(
        self, mock_event_listener, mock_input, mock_tool
    ):
        """Test that live updates are properly paused and resumed."""
        mock_formatter = Mock()
        mock_event_listener.formatter = mock_formatter

        order: list[str] = []
        mock_formatter.pause_live_updates.side_effect = lambda: order.append("pause")
        mock_formatter.resume_live_updates.side_effect = lambda: order.append("resume")
        mock_input.side_effect = lambda: order.append("input") or "test"

        context = ToolCallHookContext(
            tool_name="test_tool",
            tool_input={},
            tool=mock_tool,
        )

        context.request_human_input(prompt="Test")

        assert order == ["pause", "input", "resume"]

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    @patch("crewai.hooks.tool_hooks.event_listener")
    def test_request_human_input_resumes_on_keyboard_interrupt(
        self, mock_event_listener, mock_input, mock_tool
    ):
        """Test that live updates are resumed even on keyboard interrupt."""
        mock_formatter = Mock()
        mock_event_listener.formatter = mock_formatter

        context = ToolCallHookContext(
            tool_name="test_tool",
            tool_input={},
            tool=mock_tool,
        )

        with pytest.raises(KeyboardInterrupt):
            context.request_human_input(prompt="Test")

        mock_formatter.resume_live_updates.assert_called_once()

