import os
from typing import Any, TypedDict

from dotenv import load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI  # type: ignore[import-not-found]
from langgraph.graph import END, StateGraph
from pydantic import SecretStr

# Load environment variables from .env file
load_dotenv()


class ChatState(TypedDict):
    messages: list[str]
    chat_history: list[dict[str, Any]]
    user_input: str | None
    response: str | None


def chat_node(state: ChatState) -> ChatState:
    """Node that handles chat interactions with OpenRouter"""

    # Check for OpenRouter API key (fallback to OpenAI key name for compatibility)
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        response = (
            "Error: OPENROUTER_API_KEY or OPENAI_API_KEY environment variable not set"
        )
        messages = state.get("messages", [])
        messages.append(response)
        return ChatState(
            messages=messages,
            chat_history=state.get("chat_history", []),
            user_input=state.get("user_input"),
            response=response,
        )

    user_input = state.get("user_input")
    if not user_input:
        return state

    try:
        # Initialize the LLM with OpenRouter
        llm = ChatOpenAI(  # type: ignore[misc]
            model="openai/gpt-5-mini",
            temperature=0.7,
            api_key=SecretStr(api_key),
            base_url="https://openrouter.ai/api/v1",
        )

        # Prepare messages
        chat_messages = [
            SystemMessage(
                content="You are a helpful assistant. Keep responses concise."
            ),
            HumanMessage(content=user_input),
        ]

        # Get response from OpenAI
        response = llm.invoke(chat_messages)  # type: ignore[misc]
        # Handle response content that can be various types
        content = response.content  # type: ignore[misc]
        if isinstance(content, str):
            response_text = content
        else:
            # Handle list or other types by converting to string
            response_text = str(content) if content else ""  # type: ignore[misc]

        # Update state
        messages = state.get("messages", [])
        messages.append(f"User: {user_input}")
        messages.append(f"Assistant: {response_text}")

        chat_history = state.get("chat_history", [])
        chat_history.append({"type": "user", "content": user_input})
        chat_history.append({"type": "assistant", "content": response_text})

        return ChatState(
            messages=messages,
            chat_history=chat_history,
            user_input=None,
            response=response_text,
        )

    except Exception as e:
        error_msg = f"Error: {e!s}"
        messages = state.get("messages", [])
        messages.append(error_msg)
        return ChatState(
            messages=messages,
            chat_history=state.get("chat_history", []),
            user_input=state.get("user_input"),
            response=error_msg,
        )


def should_continue_chat(state: ChatState) -> str:
    """Decide whether to continue or end the chat"""
    user_input = state.get("user_input")
    if user_input and user_input.lower() not in ["quit", "exit", "bye"]:
        return "continue"
    return "end"


def create_chat_agent():
    """Create and return a chat agent graph"""

    workflow = StateGraph(ChatState)

    # Add nodes
    workflow.add_node("chat", chat_node)  # type: ignore[arg-type]

    # Set entry point
    workflow.set_entry_point("chat")

    # Add conditional edges
    workflow.add_conditional_edges(
        "chat", should_continue_chat, {"continue": "chat", "end": END}
    )

    return workflow.compile()  # type: ignore[return-value]


def run_chat_example():
    """Run an interactive chat example"""
    agent = create_chat_agent()

    print("Chat Agent started! Type 'quit' to exit.")
    print("Note: Make sure OPENROUTER_API_KEY or OPENAI_API_KEY is set.")

    state: ChatState = {
        "messages": [],
        "chat_history": [],
        "user_input": None,
        "response": None,
    }

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit", "bye"]:
            break

        state["user_input"] = user_input
        result = agent.invoke(state)  # type: ignore[arg-type]

        print(f"Assistant: {result.get('response', 'No response')}")
        state = result  # type: ignore[assignment]


if __name__ == "__main__":
    run_chat_example()
