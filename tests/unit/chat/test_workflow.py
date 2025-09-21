"""Tests for chat workflow."""

from __future__ import annotations

from unittest.mock import Mock, patch

from src.chat.config import ChatConfig
from src.chat.models import ChatState
from src.chat.workflow import ChatWorkflow, create_chat_agent


class TestChatWorkflow:
    """Test ChatWorkflow class."""

    @patch("src.chat.workflow.OpenRouterClient")
    @patch("src.chat.workflow.MessageHandler")
    def test_init_default_config(self, mock_handler: Mock, mock_client: Mock) -> None:
        """Test ChatWorkflow initialization with default config."""
        workflow = ChatWorkflow()

        mock_client.assert_called_once()
        mock_handler.assert_called_once()
        assert isinstance(workflow._config, ChatConfig)  # type: ignore[reportPrivateUsage]

    @patch("src.chat.workflow.OpenRouterClient")
    @patch("src.chat.workflow.MessageHandler")
    def test_init_custom_config(self, mock_handler: Mock, mock_client: Mock) -> None:
        """Test ChatWorkflow initialization with custom config."""
        config = ChatConfig(model="custom/model")
        workflow = ChatWorkflow(config)

        assert workflow._config is config  # type: ignore[reportPrivateUsage]
        mock_client.assert_called_once_with(config)

    @patch("src.chat.workflow.StateGraph")
    @patch("src.chat.workflow.OpenRouterClient")
    @patch("src.chat.workflow.MessageHandler")
    def test_create_graph(
        self, mock_handler: Mock, mock_client: Mock, mock_state_graph: Mock
    ) -> None:
        """Test graph creation."""
        mock_workflow = Mock()
        mock_compiled_graph = Mock()
        mock_workflow.compile.return_value = mock_compiled_graph
        mock_state_graph.return_value = mock_workflow

        workflow = ChatWorkflow()
        result = workflow.create_graph()

        mock_state_graph.assert_called_once_with(ChatState)
        mock_workflow.add_node.assert_called_once_with("chat", workflow._chat_node)  # type: ignore[reportPrivateUsage]
        mock_workflow.set_entry_point.assert_called_once_with("chat")
        mock_workflow.add_conditional_edges.assert_called_once()
        assert result is mock_compiled_graph

    @patch("src.chat.workflow.OpenRouterClient")
    @patch("src.chat.workflow.MessageHandler")
    def test_chat_node(self, mock_handler_class: Mock, mock_client: Mock) -> None:
        """Test chat node delegates to message handler."""
        mock_handler = Mock()
        mock_handler.process_message.return_value = {"result": "processed"}
        mock_handler_class.return_value = mock_handler

        workflow = ChatWorkflow()
        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": "test",
            "response": None,
        }

        result = workflow._chat_node(state)  # type: ignore[reportPrivateUsage]

        mock_handler.process_message.assert_called_once_with(state)
        assert result == {"result": "processed"}

    @patch("src.chat.workflow.OpenRouterClient")
    @patch("src.chat.workflow.MessageHandler")
    def test_should_continue_with_continue_input(
        self, mock_handler: Mock, mock_client: Mock
    ) -> None:
        """Test should continue with normal input."""
        workflow = ChatWorkflow()
        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": "Hello",
            "response": None,
        }

        result = workflow._should_continue(state)  # type: ignore[reportPrivateUsage]
        assert result == "continue"

    @patch("src.chat.workflow.OpenRouterClient")
    @patch("src.chat.workflow.MessageHandler")
    def test_should_continue_with_quit_commands(
        self, mock_handler: Mock, mock_client: Mock
    ) -> None:
        """Test should continue with quit commands."""
        workflow = ChatWorkflow()

        quit_commands = ["quit", "exit", "bye", "QUIT", "Exit", "BYE"]
        for command in quit_commands:
            state: ChatState = {
                "messages": [],
                "chat_history": [],
                "user_input": command,
                "response": None,
            }

            result = workflow._should_continue(state)  # type: ignore[reportPrivateUsage]
            assert result == "end", f"Failed for command: {command}"

    @patch("src.chat.workflow.OpenRouterClient")
    @patch("src.chat.workflow.MessageHandler")
    def test_should_continue_with_no_input(
        self, mock_handler: Mock, mock_client: Mock
    ) -> None:
        """Test should continue with no user input."""
        workflow = ChatWorkflow()
        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": None,
            "response": None,
        }

        result = workflow._should_continue(state)  # type: ignore[reportPrivateUsage]
        assert result == "end"

    @patch("src.chat.workflow.OpenRouterClient")
    @patch("src.chat.workflow.MessageHandler")
    def test_should_continue_with_empty_input(
        self, mock_handler: Mock, mock_client: Mock
    ) -> None:
        """Test should continue with empty user input."""
        workflow = ChatWorkflow()
        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": "",
            "response": None,
        }

        result = workflow._should_continue(state)  # type: ignore[reportPrivateUsage]
        assert result == "end"


class TestCreateChatAgent:
    """Test create_chat_agent function."""

    @patch("src.chat.workflow.ChatWorkflow")
    def test_create_chat_agent_default_config(self, mock_workflow_class: Mock) -> None:
        """Test create_chat_agent with default config."""
        mock_workflow = Mock()
        mock_graph = Mock()
        mock_workflow.create_graph.return_value = mock_graph
        mock_workflow_class.return_value = mock_workflow

        result = create_chat_agent()

        mock_workflow_class.assert_called_once_with(None)
        mock_workflow.create_graph.assert_called_once()
        assert result is mock_graph

    @patch("src.chat.workflow.ChatWorkflow")
    def test_create_chat_agent_custom_config(self, mock_workflow_class: Mock) -> None:
        """Test create_chat_agent with custom config."""
        config = ChatConfig(model="custom/model")
        mock_workflow = Mock()
        mock_graph = Mock()
        mock_workflow.create_graph.return_value = mock_graph
        mock_workflow_class.return_value = mock_workflow

        result = create_chat_agent(config)

        mock_workflow_class.assert_called_once_with(config)
        mock_workflow.create_graph.assert_called_once()
        assert result is mock_graph
