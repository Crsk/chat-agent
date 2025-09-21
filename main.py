from src.simple_agent import run_agent_example
from src.chat_agent import run_chat_example


def main():
    print("=== Agent Test Examples ===")
    print("1. Simple Agent (no API key required)")
    print("2. Chat Agent (requires OPENAI_API_KEY)")

    choice = input("\nSelect an example (1 or 2): ").strip()

    if choice == "1":
        print("\n--- Running Simple Agent ---")
        run_agent_example()
    elif choice == "2":
        print("\n--- Running Chat Agent ---")
        run_chat_example()
    else:
        print("Invalid choice. Running simple agent by default.")
        run_agent_example()


if __name__ == "__main__":
    main()
