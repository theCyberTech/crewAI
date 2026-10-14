"""Tests for base interceptor functionality."""

import httpx
import pytest

from crewai.llms.hooks.base import BaseInterceptor


class SimpleInterceptor(BaseInterceptor[httpx.Request, httpx.Response]):
    """Simple test interceptor implementation."""

    def on_outbound(self, message: httpx.Request) -> httpx.Request:
        return message

    def on_inbound(self, message: httpx.Response) -> httpx.Response:
        return message


class TestBaseInterceptor:
    """Test suite for BaseInterceptor class."""

    def test_interceptor_requires_sync_hooks(self) -> None:
        """Test that a subclass must implement both sync hooks."""

        class OutboundOnly(BaseInterceptor[httpx.Request, httpx.Response]):
            def on_outbound(self, message: httpx.Request) -> httpx.Request:
                return message

        with pytest.raises(TypeError, match="on_inbound"):
            OutboundOnly()

    @pytest.mark.asyncio
    async def test_default_async_not_implemented(self) -> None:
        """Test that default async methods raise NotImplementedError."""
        interceptor = SimpleInterceptor()
        request = httpx.Request("GET", "https://api.example.com/test")
        response = httpx.Response(200)

        with pytest.raises(NotImplementedError):
            await interceptor.aon_outbound(request)

        with pytest.raises(NotImplementedError):
            await interceptor.aon_inbound(response)
