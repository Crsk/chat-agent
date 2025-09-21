"""Tests for CLI chat runner."""

from __future__ import annotations

from unittest.mock import Mock, patch

from src.chat.config import ChatConfig
from src.chat.models import ChatState
from src.cli.chat_runner import ChatRunner, run_chat_example


class TestChatRunner:
    """Test ChatRunner class."""

    @patch("src.cli.chat_runner.create_chat_agent")
    def test_init_default_config(self, mock_create_agent: Mock) -> None:
        """Test ChatRunner initialization with default config."""
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent

        runner = ChatRunner()

        assert isinstance(runner._config, ChatConfig)  # type: ignore[reportPrivateUsage]
        assert runner._agent is mock_agent  # type: ignore[reportPrivateUsage]
        mock_create_agent.assert_called_once()

    @patch("src.cli.chat_runner.create_chat_agent")
    def test_init_custom_config(self, mock_create_agent: Mock) -> None:
        """Test ChatRunner initialization with custom config."""
        config = ChatConfig(model="custom/model")
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent

        runner = ChatRunner(config)

        assert runner._config is config  # type: ignore[reportPrivateUsage]
        assert runner._agent is mock_agent  # type: ignore[reportPrivateUsage]
        mock_create_agent.assert_called_once_with(config)

    def test_create_initial_state(self) -> None:
        """Test initial state creation."""
        with patch("src.cli.chat_runner.create_chat_agent"):
            runner = ChatRunner()
            state = runner._create_initial_state()  # type: ignore[reportPrivateUsage]

            expected: ChatState = {
                "messages": [],
                "chat_history": [],
                "user_input": None,
                "response": None,
            }
            assert state == expected

    @patch("src.cli.chat_runner.create_chat_agent")
    def test_process_input(self, mock_create_agent: Mock) -> None:
        """Test input processing."""
        mock_agent = Mock()
        mock_result = {"response": "Test response"}
        mock_agent.invoke.return_value = mock_result
        mock_create_agent.return_value = mock_agent

        runner = ChatRunner()
        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": None,
            "response": None,
        }

        result = runner._process_input(state, "Hello")  # type: ignore[reportPrivateUsage]

        assert result == mock_result
        assert state["user_input"] == "Hello"
        mock_agent.invoke.assert_called_once_with(state)

    @patch("src.cli.chat_runner.create_chat_agent")
    @patch("builtins.print")
    def test_display_response(self, mock_print: Mock, mock_create_agent: Mock) -> None:
        """Test response display."""
        runner = ChatRunner()
        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": None,
            "response": "Test response",
        }

        runner._display_response(state)  # type: ignore[reportPrivateUsage]
        mock_print.assert_called_once_with("Assistant: Test response")

    @patch("src.cli.chat_runner.create_chat_agent")
    @patch("builtins.print")
    def test_display_response_no_response(
        self, mock_print: Mock, mock_create_agent: Mock
    ) -> None:
        """Test response display with no response."""
        runner = ChatRunner()
        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": None,
            "response": None,
        }

        runner._display_response(state)  # type: ignore[reportPrivateUsage]
        mock_print.assert_called_once_with("Assistant: No response")

    @patch("src.cli.chat_runner.create_chat_agent")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_run_interactive_session_quit(
        self, mock_print: Mock, mock_input: Mock, mock_create_agent: Mock
    ) -> None:
        """Test interactive session with immediate quit."""
        mock_input.return_value = "quit"
        runner = ChatRunner()

        runner.run_interactive_session()

        # Should print startup messages
        assert mock_print.call_count >= 2
        mock_input.assert_called_once_with("\nYou: ")

    @patch("src.cli.chat_runner.create_chat_agent")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_run_interactive_session_conversation(
        self, mock_print: Mock, mock_input: Mock, mock_create_agent: Mock
    ) -> None:
        """Test interactive session with one exchange."""
        mock_agent = Mock()
        mock_agent.invoke.return_value = {
            "messages": ["User: Hello", "Assistant: Hi"],
            "chat_history": [],
            "user_input": None,
            "response": "Hi",
        }
        mock_create_agent.return_value = mock_agent

        # First input "Hello", then "quit"
        mock_input.side_effect = ["Hello", "quit"]
        runner = ChatRunner()

        runner.run_interactive_session()

        # Should call input twice (Hello, then quit)
        assert mock_input.call_count == 2
        # Should display response
        mock_print.assert_any_call("Assistant: Hi")

    @patch("src.cli.chat_runner.create_chat_agent")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_run_interactive_session_exit_commands(
        self, mock_print: Mock, mock_input: Mock, mock_create_agent: Mock
    ) -> None:
        """Test interactive session with different exit commands."""
        exit_commands = ["quit", "exit", "bye"]

        for command in exit_commands:
            mock_input.return_value = command
            mock_print.reset_mock()
            mock_input.reset_mock()

            runner = ChatRunner()
            runner.run_interactive_session()

            mock_input.assert_called_once_with("\nYou: ")


class TestRunChatExample:
    """Test run_chat_example function."""

    @patch("src.cli.chat_runner.ChatRunner")
    def test_run_chat_example_success(self, mock_runner_class: Mock) -> None:
        """Test successful run_chat_example."""
        mock_runner = Mock()
        mock_runner_class.return_value = mock_runner

        run_chat_example()

        mock_runner_class.assert_called_once()
        mock_runner.run_interactive_session.assert_called_once()

    @patch("src.cli.chat_runner.ChatRunner")
    @patch("builtins.print")
    def test_run_chat_example_value_error(
        self, mock_print: Mock, mock_runner_class: Mock
    ) -> None:
        """Test run_chat_example with ValueError."""
        mock_runner_class.side_effect = ValueError("Config error")

        run_chat_example()

        mock_print.assert_called_once_with("Configuration error: Config error")

    @patch("src.cli.chat_runner.ChatRunner")
    @patch("builtins.print")
    def test_run_chat_example_keyboard_interrupt(
        self, mock_print: Mock, mock_runner_class: Mock
    ) -> None:
        """Test run_chat_example with KeyboardInterrupt."""
        mock_runner = Mock()
        mock_runner.run_interactive_session.side_effect = KeyboardInterrupt()
        mock_runner_class.return_value = mock_runner

        run_chat_example()

        mock_print.assert_called_once_with("\nChat session ended by user.")

    @patch("src.cli.chat_runner.ChatRunner")
    @patch("builtins.print")
    def test_run_chat_example_unexpected_error(
        self, mock_print: Mock, mock_runner_class: Mock
    ) -> None:
        """Test run_chat_example with unexpected error."""
        mock_runner_class.side_effect = RuntimeError("Unexpected error")

        run_chat_example()

        mock_print.assert_called_once_with("Unexpected error: Unexpected error")
