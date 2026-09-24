"""
Unit tests for LLMClient and MockLLMClient

Tests LLM client initialization, completions, token counting,
error handling, and mock client behavior.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.llm_client import LLMClient, MockLLMClient, LLMResponse


class TestLLMClientInit:
    """Test LLMClient initialization."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        with patch('app.services.llm_client.AsyncAnthropic'):
            client = LLMClient(api_key="test-key", model="claude-3-5-sonnet-20241022")

            assert client.api_key == "test-key"
            assert client.model == "claude-3-5-sonnet-20241022"
            assert client.timeout == 60.0
            assert client.max_retries == 2

    def test_init_without_api_key_raises_error(self):
        """Test initialization without API key raises ValueError."""
        with patch('app.services.llm_client.settings') as mock_settings:
            mock_settings.claude_api_key = None

            with pytest.raises(ValueError, match="Claude API key not provided"):
                LLMClient()

    def test_init_with_custom_timeout(self):
        """Test initialization with custom timeout."""
        with patch('app.services.llm_client.AsyncAnthropic'):
            client = LLMClient(api_key="test-key", timeout=30.0, max_retries=3)

            assert client.timeout == 30.0
            assert client.max_retries == 3


class TestLLMClientComplete:
    """Test LLM completion generation."""

    @pytest.mark.asyncio
    async def test_complete_success(self):
        """Test successful completion with token counts."""
        with patch('app.services.llm_client.AsyncAnthropic') as MockAnthropic:
            # Mock the API response
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="Test response")]
            mock_message.usage.input_tokens = 10
            mock_message.usage.output_tokens = 5
            mock_message.model = "claude-3-5-sonnet-20241022"
            mock_message.stop_reason = "end_turn"

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_message)
            MockAnthropic.return_value = mock_client

            client = LLMClient(api_key="test-key")
            response = await client.complete(prompt="Test prompt")

            assert response.response_text == "Test response"
            assert response.input_tokens == 10
            assert response.output_tokens == 5
            assert response.total_tokens == 15
            assert response.model == "claude-3-5-sonnet-20241022"
            assert response.stop_reason == "end_turn"

    @pytest.mark.asyncio
    async def test_complete_with_system_prompt(self):
        """Test completion with system prompt."""
        with patch('app.services.llm_client.AsyncAnthropic') as MockAnthropic:
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="Response")]
            mock_message.usage.input_tokens = 20
            mock_message.usage.output_tokens = 10
            mock_message.model = "claude-3-5-sonnet-20241022"
            mock_message.stop_reason = "end_turn"

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_message)
            MockAnthropic.return_value = mock_client

            client = LLMClient(api_key="test-key")
            response = await client.complete(
                prompt="Test prompt",
                system_prompt="You are a helpful assistant"
            )

            # Verify system prompt was passed
            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["system"] == "You are a helpful assistant"

    @pytest.mark.asyncio
    async def test_complete_empty_prompt_raises_error(self):
        """Test completion with empty prompt raises ValueError."""
        with patch('app.services.llm_client.AsyncAnthropic'):
            client = LLMClient(api_key="test-key")

            with pytest.raises(ValueError, match="Prompt cannot be empty"):
                await client.complete(prompt="")

            with pytest.raises(ValueError, match="Prompt cannot be empty"):
                await client.complete(prompt="   ")

    @pytest.mark.asyncio
    async def test_complete_api_error(self):
        """Test completion with API error raises exception."""
        with patch('app.services.llm_client.AsyncAnthropic') as MockAnthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(side_effect=Exception("API Error"))
            MockAnthropic.return_value = mock_client

            client = LLMClient(api_key="test-key")

            with pytest.raises(Exception, match="API Error"):
                await client.complete(prompt="Test")

    @pytest.mark.asyncio
    async def test_complete_multiple_content_blocks(self):
        """Test completion with multiple content blocks concatenates text."""
        with patch('app.services.llm_client.AsyncAnthropic') as MockAnthropic:
            mock_message = MagicMock()
            mock_message.content = [
                MagicMock(text="First part"),
                MagicMock(text=" Second part"),
            ]
            mock_message.usage.input_tokens = 10
            mock_message.usage.output_tokens = 5
            mock_message.model = "claude-3-5-sonnet-20241022"
            mock_message.stop_reason = "end_turn"

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_message)
            MockAnthropic.return_value = mock_client

            client = LLMClient(api_key="test-key")
            response = await client.complete(prompt="Test")

            assert response.response_text == "First part Second part"


class TestLLMClientCompleteWithContext:
    """Test completion with context files."""

    @pytest.mark.asyncio
    async def test_complete_with_context_files(self):
        """Test completion with context files prepended."""
        with patch('app.services.llm_client.AsyncAnthropic') as MockAnthropic:
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="Response")]
            mock_message.usage.input_tokens = 30
            mock_message.usage.output_tokens = 10
            mock_message.model = "claude-3-5-sonnet-20241022"
            mock_message.stop_reason = "end_turn"

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_message)
            MockAnthropic.return_value = mock_client

            client = LLMClient(api_key="test-key")
            response = await client.complete_with_context(
                prompt="What is the sum?",
                context_files=["numbers.txt: 1, 2, 3"]
            )

            # Verify context was prepended to prompt
            call_kwargs = mock_client.messages.create.call_args[1]
            prompt_sent = call_kwargs["messages"][0]["content"]
            assert "Context File:" in prompt_sent
            assert "numbers.txt: 1, 2, 3" in prompt_sent
            assert "What is the sum?" in prompt_sent

    @pytest.mark.asyncio
    async def test_complete_without_context_files(self):
        """Test completion without context files uses normal prompt."""
        with patch('app.services.llm_client.AsyncAnthropic') as MockAnthropic:
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="Response")]
            mock_message.usage.input_tokens = 10
            mock_message.usage.output_tokens = 5
            mock_message.model = "claude-3-5-sonnet-20241022"
            mock_message.stop_reason = "end_turn"

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_message)
            MockAnthropic.return_value = mock_client

            client = LLMClient(api_key="test-key")
            response = await client.complete_with_context(
                prompt="Test prompt",
                context_files=None
            )

            call_kwargs = mock_client.messages.create.call_args[1]
            prompt_sent = call_kwargs["messages"][0]["content"]
            assert prompt_sent == "Test prompt"


class TestMockLLMClient:
    """Test MockLLMClient for testing."""

    @pytest.mark.asyncio
    async def test_mock_client_init(self):
        """Test mock client initialization."""
        client = MockLLMClient(
            mock_response="Test response",
            mock_input_tokens=20,
            mock_output_tokens=10,
        )

        assert client.mock_response == "Test response"
        assert client.mock_input_tokens == 20
        assert client.mock_output_tokens == 10
        assert client.model == "mock-model"

    @pytest.mark.asyncio
    async def test_mock_client_complete(self):
        """Test mock client returns predefined response."""
        client = MockLLMClient(
            mock_response="Mock response",
            mock_input_tokens=15,
            mock_output_tokens=8,
        )

        response = await client.complete(
            prompt="Any prompt",
            system_prompt="Any system prompt"
        )

        assert response.response_text == "Mock response"
        assert response.input_tokens == 15
        assert response.output_tokens == 8
        assert response.total_tokens == 23
        assert response.model == "mock-model"
        assert response.stop_reason == "end_turn"

    @pytest.mark.asyncio
    async def test_mock_client_ignores_prompt(self):
        """Test mock client ignores actual prompt content."""
        client = MockLLMClient(mock_response="Fixed response")

        response1 = await client.complete(prompt="Prompt 1")
        response2 = await client.complete(prompt="Different prompt")

        assert response1.response_text == response2.response_text == "Fixed response"

    @pytest.mark.asyncio
    async def test_mock_client_close(self):
        """Test mock client close is no-op."""
        client = MockLLMClient()
        await client.close()  # Should not raise


class TestLLMResponse:
    """Test LLMResponse data model."""

    def test_llm_response_creation(self):
        """Test creating LLMResponse with all fields."""
        response = LLMResponse(
            response_text="Test",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            model="claude-3-5-sonnet-20241022",
            stop_reason="end_turn",
        )

        assert response.response_text == "Test"
        assert response.input_tokens == 10
        assert response.output_tokens == 5
        assert response.total_tokens == 15
        assert response.model == "claude-3-5-sonnet-20241022"
        assert response.stop_reason == "end_turn"
        assert isinstance(response.timestamp, datetime)

    def test_llm_response_default_timestamp(self):
        """Test LLMResponse has default timestamp."""
        response = LLMResponse(
            response_text="Test",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            model="test-model",
        )

        assert response.timestamp is not None
        assert isinstance(response.timestamp, datetime)

    def test_llm_response_optional_stop_reason(self):
        """Test LLMResponse with optional stop_reason."""
        response = LLMResponse(
            response_text="Test",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            model="test-model",
        )

        assert response.stop_reason is None


class TestLLMClientClose:
    """Test LLM client cleanup."""

    @pytest.mark.asyncio
    async def test_close(self):
        """Test client close calls cleanup."""
        with patch('app.services.llm_client.AsyncAnthropic') as MockAnthropic:
            mock_client = AsyncMock()
            mock_client.close = AsyncMock()
            MockAnthropic.return_value = mock_client

            client = LLMClient(api_key="test-key")
            await client.close()

            mock_client.close.assert_called_once()


class TestExtractText:
    """Test text extraction from Claude messages."""

    @pytest.mark.asyncio
    async def test_extract_single_text_block(self):
        """Test extracting text from single content block."""
        with patch('app.services.llm_client.AsyncAnthropic'):
            client = LLMClient(api_key="test-key")

            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="Single block")]

            text = client._extract_text(mock_message)

            assert text == "Single block"

    @pytest.mark.asyncio
    async def test_extract_multiple_text_blocks(self):
        """Test extracting and concatenating multiple text blocks."""
        with patch('app.services.llm_client.AsyncAnthropic'):
            client = LLMClient(api_key="test-key")

            mock_message = MagicMock()
            mock_message.content = [
                MagicMock(text="First"),
                MagicMock(text="Second"),
                MagicMock(text="Third"),
            ]

            text = client._extract_text(mock_message)

            assert text == "FirstSecondThird"

    @pytest.mark.asyncio
    async def test_extract_empty_content(self):
        """Test extracting from empty content list."""
        with patch('app.services.llm_client.AsyncAnthropic'):
            client = LLMClient(api_key="test-key")

            mock_message = MagicMock()
            mock_message.content = []

            text = client._extract_text(mock_message)

            assert text == ""


class TestBuildPromptWithContext:
    """Test prompt building with context files."""

    def test_build_with_context(self):
        """Test building prompt with context files."""
        with patch('app.services.llm_client.AsyncAnthropic'):
            client = LLMClient(api_key="test-key")

            prompt = client._build_prompt_with_context(
                prompt="Main question",
                context_files=["File 1 content", "File 2 content"]
            )

            assert "Context File:" in prompt
            assert "File 1 content" in prompt
            assert "File 2 content" in prompt
            assert "Main question" in prompt
            assert "---" in prompt

    def test_build_without_context(self):
        """Test building prompt without context files."""
        with patch('app.services.llm_client.AsyncAnthropic'):
            client = LLMClient(api_key="test-key")

            prompt = client._build_prompt_with_context(
                prompt="Just the question",
                context_files=None
            )

            assert prompt == "Just the question"

    def test_build_with_empty_context_list(self):
        """Test building prompt with empty context list."""
        with patch('app.services.llm_client.AsyncAnthropic'):
            client = LLMClient(api_key="test-key")

            prompt = client._build_prompt_with_context(
                prompt="Question",
                context_files=[]
            )

            assert prompt == "Question"
