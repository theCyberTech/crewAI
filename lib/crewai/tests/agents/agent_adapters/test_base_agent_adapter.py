from typing import Any

import pytest
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.agents.agent_adapters.base_agent_adapter import BaseAgentAdapter
from crewai.tools.base_tool import BaseTool
from crewai.agents.agent_builder.utilities.base_token_process import TokenProcess


# Concrete implementation for testing
class ConcreteAgentAdapter(BaseAgentAdapter):
    def configure_tools(
        self, tools: list[BaseTool] | None = None, **kwargs: Any
    ) -> None:
        self.tools = tools or []

    def execute_task(
        self,
        task: Any,
        context: str | None = None,
        tools: list[Any] | None = None,
    ) -> str:
        # Dummy implementation needed due to BaseAgent inheritance
        return "Task executed"

    def create_agent_executor(self, tools: list[BaseTool] | None = None) -> Any:
        # Dummy implementation
        return None

    def get_delegation_tools(
        self, tools: list[BaseTool], tool_map: dict[str, BaseTool] | None
    ) -> list[BaseTool]:
        # Dummy implementation
        return []

    def _parse_output(self, agent_output: Any, token_process: TokenProcess):
        # Dummy implementation
        pass

    def get_output_converter(self, tools: list[BaseTool] | None = None) -> Any:
        # Dummy implementation
        return None

    def get_platform_tools(self, apps: Any) -> list[BaseTool]:
        # Dummy implementation
        return []

    def get_mcp_tools(self, mcps: list[str]) -> list[BaseTool]:
        # Dummy implementation for MCP tools
        return []

    def configure_structured_output(self, task: Any) -> None:
        # Dummy implementation for structured output
        pass

    async def aexecute_task(
        self,
        task: Any,
        context: str | None = None,
        tools: list[Any] | None = None,
    ) -> str:
        # Dummy async implementation
        return "Task executed"


def test_base_agent_adapter_initialization():
    """Test initialization of the concrete agent adapter."""
    adapter = ConcreteAgentAdapter(
        role="test role", goal="test goal", backstory="test backstory"
    )
    assert isinstance(adapter, BaseAgent)
    assert isinstance(adapter, BaseAgentAdapter)
    assert adapter.role == "test role"
    assert adapter.adapted_agent is True
    assert adapter._agent_config is None
    assert adapter.adapted_structured_output is False


def test_base_agent_adapter_initialization_with_config():
    """Test initialization with agent_config."""
    config = {"model": "gpt-4"}
    adapter = ConcreteAgentAdapter(
        agent_config=config,
        role="test role",
        goal="test goal",
        backstory="test backstory",
    )
    assert adapter._agent_config == config


class ConcreteAgentAdapterWithoutRequiredMethods(BaseAgentAdapter):
    pass


def test_base_agent_adapter_fails_without_required_methods():
    """Test that BaseAgentAdapter fails without required methods."""
    with pytest.raises(TypeError):
        ConcreteAgentAdapterWithoutRequiredMethods()  # type: ignore
