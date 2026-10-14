"""Tests for Anthropic async completion functionality."""
import json
import logging

import pytest
from pydantic import BaseModel

from crewai.llm import LLM
from crewai.llms.providers.anthropic.completion import AnthropicCompletion


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_basic_call():
    """Test basic async call with Anthropic."""
    llm = LLM(model="anthropic/claude-sonnet-4-0")

    result = await llm.acall("Say hello")

    assert result == "Hello! It's nice to meet you. How are you doing today?"


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_with_temperature():
    """Test async call with temperature parameter."""
    llm = LLM(model="anthropic/claude-sonnet-4-0", temperature=0.1)

    result = await llm.acall("Say the word 'test' once")

    assert result == "test"


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_with_max_tokens():
    """Test async call with max_tokens parameter."""
    llm = LLM(model="anthropic/claude-sonnet-4-0", max_tokens=10)

    result = await llm.acall("Write a very long story about a dragon.")

    assert result == "# The Last Song of Vaelthys"


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_with_system_message():
    """Test async call with system message."""
    llm = LLM(model="anthropic/claude-sonnet-4-0")

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"}
    ]

    result = await llm.acall(messages)

    assert result == "2 + 2 = 4"


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_conversation():
    """Test async call with conversation history."""
    llm = LLM(model="anthropic/claude-sonnet-4-0")

    messages = [
        {"role": "user", "content": "My name is Alice."},
        {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
        {"role": "user", "content": "What is my name?"}
    ]

    result = await llm.acall(messages)

    assert result == "Your name is Alice."


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_stop_sequences():
    """Test async call with stop sequences."""
    llm = LLM(
        model="anthropic/claude-sonnet-4-0",
        stop_sequences=["END", "STOP"]
    )

    result = await llm.acall("Count from 1 to 10")

    assert result == "1, 2, 3, 4, 5, 6, 7, 8, 9, 10"


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_multiple_calls():
    """Test making multiple async calls in sequence."""
    llm = LLM(model="anthropic/claude-sonnet-4-0")

    result1 = await llm.acall("What is 1+1?")
    result2 = await llm.acall("What is 2+2?")

    assert result1 == "1 + 1 = 2"
    assert result2 == "2 + 2 = 4"


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_with_response_format_none():
    """Test async call with response_format set to None."""
    llm = LLM(model="anthropic/claude-sonnet-4-0", response_format=None)

    result = await llm.acall("Tell me a short fact")

    assert result == (
        "Honey never spoils! Archaeologists have found edible honey in ancient "
        "Egyptian tombs that's over 3,000 years old."
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_with_response_format_json():
    """Test async call with JSON response format."""
    llm = LLM(model="anthropic/claude-sonnet-4-0", response_format={"type": "json_object"})

    result = await llm.acall("Return a JSON object devoid of ```json{x}```, where x is the json object, with a 'greeting' field")
    assert json.loads(result) == {"greeting": "Hello! How can I assist you today?"}


class GreetingResponse(BaseModel):
    """Response model for greeting test."""

    greeting: str
    language: str


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_with_response_model():
    """Test async call with Pydantic response_model for structured output."""
    llm = LLM(model="anthropic/claude-sonnet-4-0")

    result = await llm.acall(
        "Say hello in French",
        response_model=GreetingResponse
    )
    # When response_model is provided, the result is already a parsed Pydantic model instance
    assert result == GreetingResponse(greeting="Bonjour", language="French")


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_anthropic_async_with_tools():
    """Test async call with tools."""
    llm = AnthropicCompletion(model="claude-sonnet-4-0")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]

    result = await llm.acall(
        "What's the weather in San Francisco?",
        tools=tools
    )
    logging.debug("result: %s", result)

    assert [(call.id, call.name, call.input) for call in result] == [
        ("toolu_0133tWTcW1kwL2KtdJQbPahU", "get_weather", {"location": "San Francisco, CA"})
    ]
