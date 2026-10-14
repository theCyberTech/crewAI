"""Tests for OpenAI async completion functionality."""

import json

import pytest

from crewai import Agent, Task, Crew
from crewai.llm import LLM


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_openai_async_basic_call():
    """Test basic async call with OpenAI."""
    llm = LLM(model="gpt-4o-mini")

    result = await llm.acall("Say hello")

    assert result == "Hello! How can I assist you today?"


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_openai_async_with_temperature():
    """Test async call with temperature parameter."""
    llm = LLM(model="gpt-4o-mini", temperature=0.1)

    result = await llm.acall("Say the word 'test' once")

    assert result == "Test."


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_openai_async_with_max_tokens():
    """Test async call with max_tokens parameter."""
    llm = LLM(model="gpt-4o-mini", max_tokens=10)

    result = await llm.acall("Write a very long story about a dragon.")

    assert result == "**Title: The Last Ember of Eldoria**\n\n"


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_openai_async_with_system_message():
    """Test async call with system message."""
    llm = LLM(model="gpt-4o-mini")

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"}
    ]

    result = await llm.acall(messages)

    assert result == "2 + 2 equals 4."


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_openai_async_conversation():
    """Test async call with conversation history."""
    llm = LLM(model="gpt-4o-mini")

    messages = [
        {"role": "user", "content": "My name is Alice."},
        {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
        {"role": "user", "content": "What is my name?"}
    ]

    result = await llm.acall(messages)

    assert result == "Your name is Alice."


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_openai_async_multiple_calls():
    """Test making multiple async calls in sequence."""
    llm = LLM(model="gpt-4o-mini")

    result1 = await llm.acall("What is 1+1?")
    result2 = await llm.acall("What is 2+2?")

    assert result1 == "1 + 1 equals 2."
    assert result2 == "2 + 2 equals 4."


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_openai_async_with_response_format_none():
    """Test async call with response_format set to None."""
    llm = LLM(model="gpt-4o-mini", response_format=None)

    result = await llm.acall("Tell me a short fact")

    assert result == (
        "Octopuses have three hearts and blue blood. Two hearts pump blood to the "
        "gills, where it picks up oxygen, while the third heart pumps it to the "
        "rest of the body."
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_openai_async_with_response_format_json():
    """Test async call with JSON response format."""
    llm = LLM(model="gpt-4o-mini", response_format={"type": "json_object"})

    result = await llm.acall("Return a JSON object with a 'greeting' field")

    assert json.loads(result) == {"greeting": "Hello, world!"}


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_openai_async_with_parameters():
    """Test async call with multiple parameters."""
    llm = LLM(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=100,
        top_p=0.9,
        frequency_penalty=0.5,
        presence_penalty=0.3
    )

    result = await llm.acall("Tell me a short fact")

    assert result == (
        "Octopuses have three hearts: two pump blood to the gills, while the "
        "third pumps it to the rest of the body."
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_openai_async_streaming_returns_usage_metrics():
    """
    Test that OpenAI async streaming calls return proper token usage metrics.
    """
    agent = Agent(
        role="Research Assistant",
        goal="Find information about the capital of Italy",
        backstory="You are a helpful research assistant.",
        llm=LLM(model="gpt-4o-mini", stream=True),
        verbose=True,
    )

    task = Task(
        description="What is the capital of Italy?",
        expected_output="The capital of Italy",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task])
    result = await crew.kickoff_async()

    assert result.token_usage.prompt_tokens == 168
    assert result.token_usage.completion_tokens == 127
    assert result.token_usage.total_tokens == 295
    assert result.token_usage.successful_requests == 1
