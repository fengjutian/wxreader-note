"""LLM Provider abstraction for multiple AI backends.

Supports OpenAI, Zhipuai (Qwen/DeepSeek), and other providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import openai
from openai.error import RateLimitError, APIError

from src.config import settings
from src.utils.logging import get_logger
from src.utils.exceptions import AIProviderException, AIRateLimitException

logger = get_logger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM API.

    Attributes:
        content: Response text content.
        model: Model used for generation.
        usage: Token usage statistics.
    """

    content: Optional[str]
    model: str
    usage: dict[str, int]


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate chat completion."""
        pass

    @abstractmethod
    def supports_streaming(self) -> bool:
        """Check if provider supports streaming."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider.

    Uses OpenAI's chat completions API for LLM interactions.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        base_url: Optional[str] = None,
        max_retries: int = 3,
    ) -> None:
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (defaults to settings).
            model: Model name (defaults to gpt-4).
            base_url: Custom base URL for API.
            max_retries: Maximum retry attempts for rate limits.
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model
        self.base_url = base_url or settings.openai_base_url
        self.max_retries = max_retries

        # Configure OpenAI client
        if self.base_url != "https://api.openai.com/v1":
            openai.api_base = self.base_url
        if self.api_key:
            openai.api_key = self.api_key

        self.logger = get_logger(self.__class__.__name__)

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate chat completion using OpenAI API.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Override model name.
            temperature: Sampling temperature (0-1).
            max_tokens: Maximum tokens in response.
            max_retries: Override max retry attempts.

        Returns:
            LLMResponse with content and metadata.

        Raises:
            AIProviderException: On API error.
            AIRateLimitException: On rate limit.
        """
        retries = max_retries if max_retries is not None else self.max_retries
        attempt = 0

        while attempt <= retries:
            try:
                response = openai.ChatCompletion.create(
                    model=model or self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )

                content = response["choices"][0]["message"]["content"]
                usage = response.get("usage", {})

                self.logger.debug(
                    "OpenAI response: model=%s, tokens=%d",
                    response.get("model", "unknown"),
                    usage.get("total_tokens", 0),
                )

                return LLMResponse(
                    content=content,
                    model=response.get("model", model or self.model),
                    usage=usage,
                )

            except RateLimitError as e:
                attempt += 1
                if attempt > retries:
                    self.logger.error("Rate limit exceeded after %d retries", retries)
                    raise AIRateLimitException() from e
                self.logger.warning(
                    "Rate limit hit, retrying (%d/%d)...",
                    attempt,
                    retries,
                )

            except APIError as e:
                self.logger.error("OpenAI API error: %s", str(e))
                raise AIProviderException(
                    provider="OpenAI",
                    message=str(e),
                    status_code=getattr(e, "code", None),
                ) from e

        # Should not reach here
        raise AIProviderException(provider="OpenAI", message="Max retries exceeded")

    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True


class ZhipuaiProvider(BaseLLMProvider):
    """Zhipuai API provider for Qwen/DeepSeek models.

    Uses Zhipuai's chat completion API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "glm-4",
        max_retries: int = 3,
    ) -> None:
        """Initialize Zhipuai provider.

        Args:
            api_key: Zhipuai API key.
            model: Model name.
            max_retries: Maximum retry attempts.
        """
        self.api_key = api_key or settings.zhipuai_api_key
        self.model = model
        self.max_retries = max_retries
        self.logger = get_logger(self.__class__.__name__)

        # Import zhipuai lazily
        try:
            import zhipuai
            self.zhipuai = zhipuai
        except ImportError:
            self.logger.warning("zhipuai package not installed")
            self.zhipuai = None

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate chat completion using Zhipuai API.

        Args:
            messages: List of message dicts.

        Returns:
            LLMResponse with content and metadata.
        """
        if not self.zhipuai:
            raise AIProviderException(
                provider="Zhipuai",
                message="zhipuai package not installed",
            )

        try:
            response = self.zhipuai.model_api.invoke(
                model=self.model,
                prompt=messages,
            )

            content = response.get("data", {}).get("choices", [{}])[0].get("content", "")

            return LLMResponse(
                content=content,
                model=self.model,
                usage=response.get("usage", {}),
            )

        except Exception as e:
            self.logger.error("Zhipuai API error: %s", str(e))
            raise AIProviderException(provider="Zhipuai", message=str(e)) from e

    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True


class LLMProvider:
    """Unified LLM provider that delegates to specific providers.

    Factory class that creates and manages the appropriate LLM backend
    based on configuration.
    """

    PROVIDER_MAP = {
        "openai": OpenAIProvider,
        "zhipuai": ZhipuaiProvider,
    }

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize LLM provider.

        Args:
            provider: Provider name (openai, zhipuai).
            model: Model name override.
            **kwargs: Additional provider-specific arguments.
        """
        self.provider_name = provider or settings.ai_provider
        self.model = model or settings.openai_model
        self.logger = get_logger(self.__class__.__name__)

        # Create provider instance
        provider_class = self.PROVIDER_MAP.get(self.provider_name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {self.provider_name}")

        self._provider = provider_class(**kwargs)
        self.logger.info(
            "Initialized LLM provider: %s (model: %s)",
            self.provider_name,
            self.model,
        )

    @property
    def provider(self) -> str:
        """Get provider name."""
        return self.provider_name

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate chat completion using the configured provider.

        Args:
            messages: List of messages.
            **kwargs: Provider-specific arguments.

        Returns:
            LLMResponse from the provider.
        """
        return self._provider.chat_completion(messages, **kwargs)

    def supports_streaming(self) -> bool:
        """Check if provider supports streaming."""
        return self._provider.supports_streaming()
