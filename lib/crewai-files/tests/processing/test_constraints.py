"""Tests for provider constraints."""

import dataclasses

from crewai_files.processing.constraints import (
    ANTHROPIC_CONSTRAINTS,
    GEMINI_CONSTRAINTS,
    OPENAI_CONSTRAINTS,
    ImageConstraints,
    ProviderConstraints,
    get_constraints_for_provider,
    get_supported_content_types,
)
import pytest


class TestImageConstraints:
    """Tests for ImageConstraints dataclass."""

    def test_image_constraints_frozen(self):
        """Test that image constraints are immutable."""
        constraints = ImageConstraints(max_size_bytes=1000)

        with pytest.raises(dataclasses.FrozenInstanceError):
            constraints.max_size_bytes = 2000
        assert constraints.max_size_bytes == 1000


class TestPDFConstraints:
    """Tests for PDFConstraints dataclass."""

    @pytest.mark.parametrize("provider", ["openai", "gpt", "gpt-4o-mini"])
    def test_openai_responses_supports_pdf_for_gpt_aliases(self, provider):
        """OpenAI Responses PDF support applies to concrete GPT model names."""
        supported_types = get_supported_content_types(provider, api="responses")

        assert "application/pdf" in supported_types


class TestGetSupportedContentTypes:
    """Tests for get_supported_content_types function."""

    @pytest.mark.parametrize(
        ("provider", "expected"),
        [
            ("anthropic", ["image/", "application/pdf"]),
            ("openai", ["image/"]),
            ("gemini", ["image/", "application/pdf", "audio/", "video/", "text/"]),
            ("bedrock", ["image/", "application/pdf"]),
            ("unknown-provider", []),
        ],
    )
    def test_supported_content_types_by_provider(self, provider, expected):
        """Supported content types reflect which media each provider accepts."""
        assert get_supported_content_types(provider) == expected


class TestGetConstraintsForProvider:
    """Tests for get_constraints_for_provider function."""

    def test_get_by_exact_name(self):
        """Test getting constraints by exact provider name."""
        result = get_constraints_for_provider("anthropic")
        assert result == ANTHROPIC_CONSTRAINTS

        result = get_constraints_for_provider("openai")
        assert result == OPENAI_CONSTRAINTS

        result = get_constraints_for_provider("gemini")
        assert result == GEMINI_CONSTRAINTS

    def test_get_by_alias(self):
        """Test getting constraints by alias name."""
        result = get_constraints_for_provider("claude")
        assert result == ANTHROPIC_CONSTRAINTS

        result = get_constraints_for_provider("gpt")
        assert result == OPENAI_CONSTRAINTS

        result = get_constraints_for_provider("google")
        assert result == GEMINI_CONSTRAINTS

    def test_get_case_insensitive(self):
        """Test case-insensitive lookup."""
        result = get_constraints_for_provider("ANTHROPIC")
        assert result == ANTHROPIC_CONSTRAINTS

        result = get_constraints_for_provider("OpenAI")
        assert result == OPENAI_CONSTRAINTS

    def test_get_with_provider_constraints_object(self):
        """Test passing ProviderConstraints object returns it unchanged."""
        custom = ProviderConstraints(name="custom")
        result = get_constraints_for_provider(custom)
        assert result is custom

    def test_get_unknown_provider(self):
        """Test unknown provider returns None."""
        result = get_constraints_for_provider("unknown-provider")
        assert result is None

    def test_get_by_partial_match(self):
        """Test partial match in provider string."""
        result = get_constraints_for_provider("claude-3-sonnet")
        assert result == ANTHROPIC_CONSTRAINTS

        result = get_constraints_for_provider("gpt-4o")
        assert result == OPENAI_CONSTRAINTS

        result = get_constraints_for_provider("gemini-pro")
        assert result == GEMINI_CONSTRAINTS
