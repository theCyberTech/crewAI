# CLAUDE.md - CrewAI Development Guide

## Project Overview

CrewAI is a Python framework for orchestrating AI agents to work together on complex tasks. It uses a monorepo workspace managed by UV with multiple packages:

- **lib/crewai/** - Core framework (agents, tasks, crews, flows)
- **lib/crewai-tools/** - Collection of tools for agents
- **lib/crewai-files/** - Multimodal file handling utilities
- **lib/devtools/** - Private development tools

## Quick Reference

```bash
# Install dependencies
uv lock && uv sync

# Create virtual environment
uv venv

# Install pre-commit hooks
pre-commit install

# Run all tests
uv run pytest .

# Run tests for specific package
cd lib/crewai && uv run pytest

# Type checking
uvx mypy src

# Lint and format
uvx ruff check --fix .
uvx ruff format .

# Build packages
uv build --all-packages
```

## Development Setup

**Requirements:** Python 3.10-3.13

1. Install UV package manager
2. Clone the repository
3. Run `uv lock && uv sync`
4. Run `pre-commit install`

## Testing

- **Framework:** pytest with pytest-asyncio, pytest-xdist
- **Parallelization:** 8 workers by default
- **Timeout:** 60 seconds per test
- **Network:** Blocked during tests (uses VCR cassettes for HTTP mocking)

```bash
# Run all tests
uv run pytest .

# Run with parallel splitting (CI style)
uv run pytest --splits 8 --group 1

# Run specific test file
uv run pytest lib/crewai/tests/test_agent.py
```

## Code Style

**Tools:** ruff (linter/formatter), mypy (type checker)

**Key Rules:**
- Target Python: 3.10
- Strict mypy enforcement
- 2-space indentation (per .editorconfig)
- UTF-8 encoding, LF line endings
- No print statements (use logging)

**Enabled Linters:** E, W, F, B, S (bandit), RUF, N, I (isort), T, PERF, ASYNC

```bash
# Check linting
uvx ruff check .

# Auto-fix issues
uvx ruff check --fix .

# Format code
uvx ruff format .

# Type check
uvx mypy src
```

## Architecture

### Core Entities (Pydantic BaseModel)

- **Agent** - AI entity with role, goal, backstory; uses tools for capabilities
- **Task** - Work unit with description, expected_output; assigned to an agent
- **Crew** - Orchestrates multiple agents and tasks (sequential/hierarchical)
- **Flow** - Event-driven workflows with @start, @listen, @router decorators

### Key Patterns

- **Pydantic everywhere** - All config classes inherit from BaseModel
- **Event bus** - Centralized event system for telemetry and tracing
- **Lazy loading** - Tools and dependencies loaded on demand
- **Tool framework** - BaseTool with _run()/_arun(), args_schema validation
- **OpenTelemetry** - Distributed tracing and observability

### Directory Structure (lib/crewai/src/crewai/)

```
agent/      - Agent core implementation
crews/      - Crew orchestration
flow/       - Flow-based workflows
tasks/      - Task definitions
llms/       - LLM integrations
memory/     - Memory management
knowledge/  - Knowledge base (RAG)
tools/      - Tool framework
events/     - Event bus system
cli/        - Command-line interface
```

## Building Tools

Tools extend `BaseTool` and implement:
- `args_schema` - Pydantic model for input validation
- `_run()` - Synchronous execution
- `_arun()` - Optional async execution
- `env_vars` - Required environment variables
- `package_dependencies` - Optional packages

See `lib/crewai-tools/BUILDING_TOOLS.md` for detailed guide.

## CI/CD

- **Tests:** Run on PRs across Python 3.10-3.13 matrix
- **Linting:** ruff check in CI
- **Type checking:** mypy in strict mode
- **Publishing:** Automated to PyPI via GitHub Actions

## Important Files

- `pyproject.toml` - Workspace and tool configuration
- `conftest.py` - Pytest configuration and fixtures
- `.pre-commit-config.yaml` - Git hooks configuration
- `lib/crewai/src/crewai/__init__.py` - Version definition (__version__)
