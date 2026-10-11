import sys

from voice_agent.conversation import AgentState, get_next_question, handle_customer_utterance

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    state = AgentState()
    print("Home Credit LAP Qualification Demo")
    print("===================================")
    print("Type 'exit' at any time to end the demo.")

    while True:
        question = get_next_question(state)
        if question is None:
            print("Call ended.")
            break

        try:
            user_input = input(f"\n{question}\n> ")
        except EOFError:
            print("\nInput stream closed. Ending demo.")
            break

        if user_input.strip().lower() in {"exit", "quit"}:
            print("Ending demo.")
            break

        result = handle_customer_utterance(state, user_input)
        print(f"\nBot: {result['response']}")

        status = result["status"]
        if status in {"callback", "transfer", "disqualified", "ended", "complete"}:
            print("\nFinal state:")
            print(state)
            break


if __name__ == "__main__":
    main()
