from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ChatState(TypedDict):
    messages: List[str]
    chat_history: List[dict]
    user_input: Optional[str]
    response: Optional[str]


def chat_node(state: ChatState) -> ChatState:
    """Node that handles chat interactions with OpenRouter"""

    # Check for OpenRouter API key (fallback to OpenAI key name for compatibility)
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        response = "Error: OPENROUTER_API_KEY or OPENAI_API_KEY environment variable not set"
        messages = state.get("messages", [])
        messages.append(response)
        return {
            **state,
            "messages": messages,
            "response": response
        }

    user_input = state.get("user_input")
    if not user_input:
        return state

    try:
        # Initialize the LLM with OpenRouter
        llm = ChatOpenAI(
            model="openai/gpt-5-mini",
            temperature=0.7,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )

        # Prepare messages
        chat_messages = [
            SystemMessage(content="You are a helpful assistant. Keep responses concise and friendly."),
            HumanMessage(content=user_input)
        ]

        # Get response from OpenAI
        response = llm.invoke(chat_messages)
        response_text = response.content

        # Update state
        messages = state.get("messages", [])
        messages.append(f"User: {user_input}")
        messages.append(f"Assistant: {response_text}")

        chat_history = state.get("chat_history", [])
        chat_history.append({"type": "user", "content": user_input})
        chat_history.append({"type": "assistant", "content": response_text})

        return {
            **state,
            "messages": messages,
            "chat_history": chat_history,
            "response": response_text,
            "user_input": None
        }

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        messages = state.get("messages", [])
        messages.append(error_msg)
        return {
            **state,
            "messages": messages,
            "response": error_msg
        }


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
    workflow.add_node("chat", chat_node)

    # Set entry point
    workflow.set_entry_point("chat")

    # Add conditional edges
    workflow.add_conditional_edges(
        "chat",
        should_continue_chat,
        {
            "continue": "chat",
            "end": END
        }
    )

    return workflow.compile()


def run_chat_example():
    """Run an interactive chat example"""
    agent = create_chat_agent()

    print("Chat Agent started! Type 'quit' to exit.")
    print("Note: Make sure OPENROUTER_API_KEY or OPENAI_API_KEY is set in your environment.")

    state = {
        "messages": [],
        "chat_history": [],
        "user_input": None,
        "response": None
    }

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit", "bye"]:
            break

        state["user_input"] = user_input
        result = agent.invoke(state)

        print(f"Assistant: {result.get('response', 'No response')}")
        state = result


if __name__ == "__main__":
    run_chat_example()