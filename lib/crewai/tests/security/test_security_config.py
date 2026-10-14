"""Test for the SecurityConfig class."""

from datetime import datetime
import json
import uuid

from crewai.security import Fingerprint, SecurityConfig


def test_security_config_creation_with_defaults():
    """Test creating a SecurityConfig with default values."""
    config = SecurityConfig()

    assert isinstance(config.fingerprint, Fingerprint)
    assert config.fingerprint.metadata == {}


def test_security_config_fingerprint_generation():
    """Test that SecurityConfig automatically generates fingerprints."""
    config = SecurityConfig()
    other_config = SecurityConfig()

    assert uuid.UUID(config.fingerprint.uuid_str).version == 4
    assert config.fingerprint.uuid_str != other_config.fingerprint.uuid_str


def test_security_config_init_params():
    """Test that SecurityConfig can be initialized and modified."""
    config = SecurityConfig()

    fingerprint = Fingerprint(metadata={"version": "1.0"})

    config.fingerprint = fingerprint

    assert config.fingerprint is fingerprint
    assert config.fingerprint.metadata == {"version": "1.0"}


def test_security_config_to_dict():
    """Test converting SecurityConfig to dictionary."""
    config = SecurityConfig()
    config.fingerprint.metadata = {"version": "1.0"}

    config_dict = config.to_dict()

    assert "fingerprint" in config_dict
    assert isinstance(config_dict["fingerprint"], dict)
    assert config_dict["fingerprint"]["metadata"] == {"version": "1.0"}


def test_security_config_from_dict():
    """Test creating SecurityConfig from dictionary."""
    fingerprint_dict = {
        "uuid_str": "b723c6ff-95de-5e87-860b-467b72282bd8",
        "created_at": datetime.now().isoformat(),
        "metadata": {"version": "1.0"},
    }

    config_dict = {"fingerprint": fingerprint_dict}

    config = SecurityConfig.from_dict(config_dict)

    assert config.fingerprint.uuid_str == "b723c6ff-95de-5e87-860b-467b72282bd8"
    assert config.fingerprint.metadata == {"version": "1.0"}


def test_security_config_json_serialization():
    """Test that SecurityConfig can be JSON serialized and deserialized."""
    config = SecurityConfig()
    config.fingerprint.metadata = {"version": "1.0"}

    config_dict = config.to_dict()

    assert isinstance(config_dict["fingerprint"], dict)

    json_str = json.dumps(config_dict)

    parsed_dict = json.loads(json_str)

    assert parsed_dict["fingerprint"]["metadata"] == {"version": "1.0"}

    new_config = SecurityConfig.from_dict(parsed_dict)

    assert new_config.fingerprint.uuid_str == config.fingerprint.uuid_str
    assert new_config.fingerprint.metadata == {"version": "1.0"}
