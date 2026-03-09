"""Configuration module tests"""

import os
import pytest

from optmath.core.config import (
    load_config,
    Config,
    InstanceGenerationConfig,
    BacktranslationConfig,
    LLMConfig,
    LLMProviderConfig,
)


def test_load_config_default():
    config = load_config()
    assert config is not None
    assert config.instance_generation.num_instances == 2500
    assert config.instance_generation.var_num_max == 50


def test_config_from_dict_partial():
    data = {
        "instance_generation": {"num_instances": 100},
    }
    config = Config.from_dict(data)
    assert config.instance_generation.num_instances == 100
    assert config.instance_generation.var_num_max == 50  # default value


def test_instance_generation_config_defaults():
    cfg = InstanceGenerationConfig()
    assert cfg.num_instances == 2500
    assert cfg.var_num_max == 50


def test_llm_config_has_providers():
    """Test LLM configuration loading"""
    config = load_config()
    assert config.llm is not None
    assert config.llm.default_model == "deepseek_official"
    assert "deepseek_official" in config.llm.providers
    assert "gpt" in config.llm.providers
    assert "claude" in config.llm.providers


def test_llm_provider_config():
    """Test LLM Provider configuration"""
    data = {
        "model": "test-model",
        "base_url": "https://api.test.com/v1",
        "api_key_env": "TEST_API_KEY",
    }
    provider = LLMProviderConfig(**data)
    assert provider.model == "test-model"
    assert provider.base_url == "https://api.test.com/v1"
    assert provider.api_key_env == "TEST_API_KEY"


def test_llm_config_from_dict():
    """Test LLMConfig creation from dict"""
    data = {
        "default_model": "gpt",
        "providers": {
            "deepseek": {
                "model": "deepseek-chat",
                "base_url": "https://api.deepseek.com/v1",
                "api_key_env": "DEEPSEEK_API_KEY",
            }
        },
    }
    cfg = LLMConfig.from_dict(data)
    assert cfg.default_model == "gpt"
    assert "deepseek" in cfg.providers
    assert cfg.providers["deepseek"].model == "deepseek-chat"


def test_llm_client_creation_requires_api_key():
    """Test LLM client creation requires environment variable"""
    from optmath.llm import create_llm_client

    # Ensure environment variables are not set
    key = os.environ.pop("LHL_DEEPSEEK_KEY", None)

    try:
        # Should raise ValueError
        with pytest.raises(ValueError, match="Environment variable .* not found"):
            create_llm_client("deepseek_official")
    finally:
        # Restore environment variables (if previously existed)
        if key:
            os.environ["LHL_DEEPSEEK_KEY"] = key


def test_llm_client_unknown_model_raises():
    """Unknown model names should not silently fall back to defaults."""
    from optmath.llm import create_llm_client

    with pytest.raises(ValueError, match="Configuration not found for model"):
        create_llm_client("does_not_exist")


def test_llm_client_creation_with_mock_key():
    """Test client creation with mock API key"""
    from optmath.llm import create_llm_client

    # Test deepseek_official
    os.environ["LHL_DEEPSEEK_KEY"] = "test-key-67890"
    try:
        client = create_llm_client("deepseek_official")
        assert client is not None
        assert "openai/" in client.model or "deepseek" in client.model.lower()
        assert client.api_base == "https://api.deepseek.com/v1"
    finally:
        os.environ.pop("LHL_DEEPSEEK_KEY", None)


def test_env_override_uses_section_prefixes(monkeypatch):
    monkeypatch.setenv("OPTMATH_INSTANCE_GENERATION_NUM_INSTANCES", "123")
    monkeypatch.setenv("OPTMATH_BACKTRANSLATION_MAX_WORKERS", "9")
    config = load_config()
    assert config.instance_generation.num_instances == 123
    assert config.backtranslation.max_workers == 9
