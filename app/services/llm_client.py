"""
Token Golf - LLM Client Service

Abstraction layer for LLM provider interactions.
Supports Claude API (development/production) with token counting.

See ADR 007 for architecture decisions.
"""

import logging
from datetime import datetime
from typing import Optional

from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import Message
from pydantic import BaseModel, Field

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    """
    Structured response from LLM with token usage data.

    All tokens count toward scoring: input + output.
    System prompts are included in input token count.
    """

    response_text: str = Field(
        ..., description="The LLM's response text"
    )

    input_tokens: int = Field(
        ..., description="Input tokens (includes system prompt)"
    )

    output_tokens: int = Field(
        ..., description="Output tokens generated"
    )

    total_tokens: int = Field(
        ..., description="Total tokens (input + output)"
    )

    model: str = Field(
        ..., description="Model used for generation"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the response was generated"
    )

    stop_reason: Optional[str] = Field(
        None, description="Why the model stopped generating"
    )


class LLMClient:
    """
    Client for interacting with LLM providers.

    Currently supports Claude API via Anthropic SDK.
    Designed for easy swapping to OpenShift AI in production.

    Usage:
        client = LLMClient()
        response = await client.complete(
            prompt="Write a Python function...",
            system_prompt="You are a helpful coding assistant."
        )
        print(f"Tokens used: {response.total_tokens}")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 2,
    ):
        """
        Initialize LLM client.

        Args:
            api_key: Claude API key (defaults to settings.claude_api_key)
            model: Model to use (defaults to settings.claude_model)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts on failure
        """
        self.api_key = api_key or settings.claude_api_key
        self.model = model or settings.claude_model
        self.timeout = timeout
        self.max_retries = max_retries

        if not self.api_key:
            raise ValueError(
                "Claude API key not provided. Set CLAUDE_API_KEY environment variable."
            )

        # Initialize async Anthropic client
        self.client = AsyncAnthropic(
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

        logger.info(f"LLM Client initialized with model: {self.model}")

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> LLMResponse:
        """
        Generate a completion from the LLM.

        Args:
            prompt: User prompt/question
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            LLMResponse with text and token counts

        Raises:
            ValueError: If prompt is empty
            Exception: If API call fails after retries

        Example:
            response = await client.complete(
                prompt="Write a function that adds two numbers",
                system_prompt="You are a Python expert"
            )
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        logger.debug(
            f"Calling LLM with prompt length: {len(prompt)}, "
            f"system prompt: {bool(system_prompt)}"
        )

        try:
            # Call Claude API
            message: Message = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extract response text (handle multiple content blocks)
            response_text = self._extract_text(message)

            # Extract token usage
            usage = message.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            total_tokens = input_tokens + output_tokens

            # Build response
            llm_response = LLMResponse(
                response_text=response_text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                model=message.model,
                stop_reason=message.stop_reason,
            )

            logger.info(
                f"LLM response generated: {total_tokens} tokens "
                f"(in: {input_tokens}, out: {output_tokens})"
            )

            return llm_response

        except Exception as e:
            logger.error(f"LLM API error: {e}")
            raise

    def _extract_text(self, message: Message) -> str:
        """
        Extract text from Claude message response.

        Claude can return multiple content blocks. This concatenates
        all text blocks into a single string.

        Args:
            message: Anthropic Message object

        Returns:
            Concatenated text from all content blocks
        """
        text_parts = []

        for block in message.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)

        return "".join(text_parts)

    async def complete_with_context(
        self,
        prompt: str,
        context_files: Optional[list[str]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> LLMResponse:
        """
        Generate completion with context files included in prompt.

        Context files are prepended to the user prompt.
        Useful for challenges that provide reference data.

        Args:
            prompt: User prompt
            context_files: List of context file contents
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLMResponse with text and token counts

        Example:
            response = await client.complete_with_context(
                prompt="What's the total?",
                context_files=["numbers.txt: 1, 2, 3, 4, 5"]
            )
        """
        # Build full prompt with context
        full_prompt = self._build_prompt_with_context(prompt, context_files)

        # Call standard complete method
        return await self.complete(
            prompt=full_prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def _build_prompt_with_context(
        self,
        prompt: str,
        context_files: Optional[list[str]] = None,
    ) -> str:
        """
        Build prompt with context files prepended.

        Args:
            prompt: Base user prompt
            context_files: List of context file contents

        Returns:
            Full prompt with context
        """
        if not context_files:
            return prompt

        context_section = "\n\n".join(
            f"Context File:\n{content}" for content in context_files
        )

        return f"{context_section}\n\n---\n\n{prompt}"

    async def close(self):
        """Close the client and cleanup resources."""
        await self.client.close()
        logger.debug("LLM Client closed")


class MockLLMClient(LLMClient):
    """
    Mock LLM client for testing.

    Returns predefined responses without calling actual API.
    Useful for unit tests and development without API costs.

    Usage:
        client = MockLLMClient(
            mock_response="def add(a, b): return a + b"
        )
        response = await client.complete("Write an add function")
        # Returns mock_response with fake token counts
    """

    def __init__(
        self,
        mock_response: str = "This is a mock response.",
        mock_input_tokens: int = 10,
        mock_output_tokens: int = 5,
        **kwargs,
    ):
        """
        Initialize mock client.

        Args:
            mock_response: Response text to return
            mock_input_tokens: Fake input token count
            mock_output_tokens: Fake output token count
            **kwargs: Ignored (for compatibility with LLMClient)
        """
        self.mock_response = mock_response
        self.mock_input_tokens = mock_input_tokens
        self.mock_output_tokens = mock_output_tokens
        self.model = kwargs.get("model", "mock-model")

        logger.info("Mock LLM Client initialized")

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> LLMResponse:
        """
        Return mock response without calling API.

        Args:
            prompt: User prompt (logged but not used)
            system_prompt: System prompt (logged but not used)
            max_tokens: Ignored
            temperature: Ignored

        Returns:
            LLMResponse with mock data
        """
        logger.debug(f"Mock LLM called with prompt: {prompt[:50]}...")

        return LLMResponse(
            response_text=self.mock_response,
            input_tokens=self.mock_input_tokens,
            output_tokens=self.mock_output_tokens,
            total_tokens=self.mock_input_tokens + self.mock_output_tokens,
            model=self.model,
            stop_reason="end_turn",
        )

    async def close(self):
        """No-op for mock client."""
        logger.debug("Mock LLM Client closed")
