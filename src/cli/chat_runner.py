"""CLI interface for running chat interactions."""

from __future__ import annotations

from src.chat.config import ChatConfig
from src.chat.models import ChatState
from src.chat.workflow import create_chat_agent


class ChatRunner:
    """Handles CLI chat interactions."""

    def __init__(self, config: ChatConfig | None = None) -> None:
        """Initialize chat runner."""
        self._config = config or ChatConfig()
        self._agent = create_chat_agent(self._config)

    def run_interactive_session(self) -> None:
        """Run an interactive chat session."""
        print("Chat Agent started! Type 'quit' to exit.")
        print("Note: Make sure OPENROUTER_API_KEY or OPENAI_API_KEY is set.")

        state = self._create_initial_state()

        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["quit", "exit", "bye"]:
                break

            state = self._process_input(state, user_input)
            self._display_response(state)

    def _create_initial_state(self) -> ChatState:
        """Create initial chat state."""
        return ChatState(
            messages=[],
            chat_history=[],
            user_input=None,
            response=None,
        )

    def _process_input(self, state: ChatState, user_input: str) -> ChatState:
        """Process user input and return updated state."""
        state["user_input"] = user_input
        result = self._agent.invoke(state)  # type: ignore[arg-type]
        return result  # type: ignore[return-value]

    def _display_response(self, state: ChatState) -> None:
        """Display the assistant's response."""
        response = state.get("response") or "No response"
        print(f"Assistant: {response}")


def run_chat_example() -> None:
    """Run an interactive chat example."""
    try:
        runner = ChatRunner()
        runner.run_interactive_session()
    except ValueError as e:
        print(f"Configuration error: {e}")
    except KeyboardInterrupt:
        print("\nChat session ended by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
