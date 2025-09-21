from langgraph.graph import StateGraph, END
from typing import TypedDict, List


class AgentState(TypedDict):
    messages: List[str]
    current_task: str
    completed_tasks: List[str]


def reasoning_node(state: AgentState) -> AgentState:
    """Node that handles reasoning and decision making"""
    messages = state.get("messages", [])
    current_task = state.get("current_task", "")

    # Simple reasoning logic
    if current_task and current_task not in state.get("completed_tasks", []):
        new_message = f"Processing task: {current_task}"
        messages.append(new_message)

        # Mark task as completed
        completed_tasks = state.get("completed_tasks", [])
        completed_tasks.append(current_task)

        return {
            "messages": messages,
            "current_task": "",
            "completed_tasks": completed_tasks
        }

    return state


def should_continue(state: AgentState) -> str:
    """Decide whether to continue processing or end"""
    if state.get("current_task"):
        return "continue"
    return "end"


def create_simple_agent():
    """Create and return a simple agent graph"""

    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("reasoning", reasoning_node)

    # Set entry point
    workflow.set_entry_point("reasoning")

    # Add conditional edges
    workflow.add_conditional_edges(
        "reasoning",
        should_continue,
        {
            "continue": "reasoning",
            "end": END
        }
    )

    return workflow.compile()


def run_agent_example():
    """Run a simple example with the agent"""
    agent = create_simple_agent()

    # Initial state
    initial_state = {
        "messages": ["Agent starting up..."],
        "current_task": "analyze data",
        "completed_tasks": []
    }

    # Run the agent
    result = agent.invoke(initial_state)

    print("Agent execution completed!")
    print(f"Messages: {result['messages']}")
    print(f"Completed tasks: {result['completed_tasks']}")

    return result


if __name__ == "__main__":
    run_agent_example()