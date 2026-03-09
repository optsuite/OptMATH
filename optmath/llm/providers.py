"""LLM client implementation using LiteLLM unified interface

LiteLLM provides a unified interface to call 100+ LLM APIs, including:
- OpenAI, Anthropic, Cohere, Gemini, Azure OpenAI
- DeepSeek, Zhipu AI, and various OpenAI-compatible endpoints

Documentation: https://docs.litellm.ai/
"""

import os
from typing import Optional, Tuple

from .base import LLMClient, LLMResponse


class LiteLLMClient(LLMClient):
    """Unified LLM client using LiteLLM"""

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        """
        Initialize LiteLLM client

        Args:
            model: Model name, e.g., "gpt-4o", "claude-3-opus-20240229", "deepseek-chat", etc.
            api_key: API key (optional, environment variables take priority)
            api_base: Custom API endpoint (optional, for OpenAI-compatible endpoints)
        """
        self.model = model
        self.api_key = api_key
        self.api_base = api_base

    def complete(
        self,
        message: str,
        system_message: str = "You are a helpful assistant.",
        temperature: float = 0.8,
        max_tokens: int = 8192,
        max_retries: int = 3,
    ) -> Tuple[str, LLMResponse]:
        """
        Call LLM to get response (with retry mechanism)

        Args:
            message: User message
            system_message: System prompt
            temperature: Temperature parameter
            max_tokens: Maximum token count
            max_retries: Maximum retry attempts

        Returns:
            (response_content, usage_info)
        """
        import litellm
        import time

        # Build message list
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": message},
        ]

        # Build call parameters - ensure api_key is always passed
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "api_key": self.api_key,  # Always pass api_key
        }

        # Add optional parameters
        if self.api_base:
            kwargs["api_base"] = self.api_base

        # Call with retry
        last_error = None
        for attempt in range(max_retries):
            try:
                response = litellm.completion(**kwargs)

                # Extract response content
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from LLM")

                # Extract usage information
                usage = response.usage
                llm_resp = LLMResponse(
                    content=content,
                    prompt_tokens=usage.prompt_tokens if usage else 0,
                    completion_tokens=usage.completion_tokens if usage else 0,
                    total_tokens=usage.total_tokens if usage else 0,
                )

                return content, llm_resp

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    print(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # Last attempt failed
                    import sys
                    print(f"LiteLLM call failed (retried {max_retries} times): {e}", file=sys.stderr)
                    print(f"Model: {self.model}, api_base: {self.api_base}", file=sys.stderr)
                    raise

        # Should not reach here, but for type checking
        raise last_error


# Global configuration cache
_llm_config = None


def _get_llm_config():
    """Get LLM configuration (lazy loading)"""
    global _llm_config
    if _llm_config is None:
        from ..core.config import load_config
        cfg = load_config()
        _llm_config = cfg.llm
    return _llm_config


def create_llm_client(model_name: str = None, config: dict = None) -> LLMClient:
    """
    Create corresponding LLM client based on model_name

    Args:
        model_name: Model name, if None uses default_model from config
        config: Optional configuration dict (deprecated, kept for compatibility)

    Supported model_name values are defined in ``config/default.yaml``.
    By default this repository ships with:
        - deepseek_official
        - gpt
        - claude
        - gemini
        - minimax

    Unknown model names raise ``ValueError`` instead of silently falling back.
    """
    # Get configuration
    llm_cfg = _get_llm_config()

    # Determine model name to use
    if model_name is None:
        model_name = llm_cfg.default_model

    model_key = model_name.lower()

    # Get provider info from config
    provider_cfg = llm_cfg.providers.get(model_key)

    if provider_cfg is None:
        raise ValueError(
            f"Configuration not found for model '{model_name}', "
            f"available models: {', '.join(sorted(llm_cfg.providers))}"
        )

    # Get API key from environment variables
    api_key = os.getenv(provider_cfg.api_key_env)
    if not api_key:
        raise ValueError(
            f"Environment variable '{provider_cfg.api_key_env}' not found, "
            f"please set it first: export {provider_cfg.api_key_env}='your-api-key'"
        )

    # For custom OpenAI-compatible endpoints, use openai/ prefix
    if provider_cfg.base_url and provider_cfg.base_url != "https://api.openai.com/v1":
        # Use openai/ prefix + custom endpoint
        litellm_model = f"openai/{provider_cfg.model}"
        return LiteLLMClient(
            model=litellm_model,
            api_key=api_key,
            api_base=provider_cfg.base_url,
        )

    # Standard provider, use model name directly
    return LiteLLMClient(
        model=provider_cfg.model,
        api_key=api_key,
    )
