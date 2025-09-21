"""Message handling and state management."""

from __future__ import annotations

from src.chat.config import ChatConfig
from src.chat.llm_client import LLMClient
from src.chat.models import ChatMessage, ChatState


class MessageHandler:
    """Handles message processing and state updates."""

    def __init__(self, llm_client: LLMClient, config: ChatConfig) -> None:
        """Initialize message handler."""
        self._llm_client = llm_client
        self._config = config

    def process_message(self, state: ChatState) -> ChatState:
        """Process user message and update state."""
        user_input = state.get("user_input")
        if not user_input:
            return state

        try:
            response_text = self._llm_client.generate_response(
                user_input, self._config.system_message
            )
            return self._update_state_success(state, user_input, response_text)
        except Exception as e:
            return self._update_state_error(state, str(e))

    def _update_state_success(
        self, state: ChatState, user_input: str, response_text: str
    ) -> ChatState:
        """Update state with successful response."""
        messages = state.get("messages", []).copy()
        messages.extend([f"User: {user_input}", f"Assistant: {response_text}"])

        chat_history = state.get("chat_history", []).copy()
        chat_history.extend(
            [
                ChatMessage(type="user", content=user_input),
                ChatMessage(type="assistant", content=response_text),
            ]
        )

        return ChatState(
            messages=messages,
            chat_history=chat_history,
            user_input=None,
            response=response_text,
        )

    def _update_state_error(self, state: ChatState, error_message: str) -> ChatState:
        """Update state with error response."""
        error_msg = f"Error: {error_message}"
        messages = state.get("messages", []).copy()
        messages.append(error_msg)

        return ChatState(
            messages=messages,
            chat_history=state.get("chat_history", []),
            user_input=state.get("user_input"),
            response=error_msg,
        )
