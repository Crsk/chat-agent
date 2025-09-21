"""Workflow management for chat agent using LangGraph."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from src.chat.config import ChatConfig
from src.chat.llm_client import OpenRouterClient
from src.chat.message_handler import MessageHandler
from src.chat.models import ChatState


class ChatWorkflow:
    """Manages the chat workflow graph."""

    def __init__(self, config: ChatConfig | None = None) -> None:
        """Initialize chat workflow."""
        self._config = config or ChatConfig()
        self._llm_client = OpenRouterClient(self._config)
        self._message_handler = MessageHandler(self._llm_client, self._config)

    def create_graph(self) -> Any:
        """Create and return the compiled workflow graph."""
        workflow = StateGraph(ChatState)

        # Add nodes
        workflow.add_node("chat", self._chat_node)  # type: ignore[arg-type]

        # Set entry point
        workflow.set_entry_point("chat")

        # Add conditional edges
        workflow.add_conditional_edges(
            "chat", self._should_continue, {"continue": "chat", "end": END}
        )

        return workflow.compile()  # type: ignore[return-value]

    def _chat_node(self, state: ChatState) -> ChatState:
        """Chat node that processes messages."""
        return self._message_handler.process_message(state)

    def _should_continue(self, state: ChatState) -> str:
        """Decide whether to continue or end the chat."""
        user_input = state.get("user_input")
        if user_input and user_input.lower() not in ["quit", "exit", "bye"]:
            return "continue"
        return "end"


def create_chat_agent(config: ChatConfig | None = None) -> Any:
    """Create and return a chat agent graph."""
    workflow = ChatWorkflow(config)
    return workflow.create_graph()
