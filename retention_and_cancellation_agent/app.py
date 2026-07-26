from backend import Backend
from agent import SupportAgent
from models import Session


def main() -> None:
    backend = Backend()
    agent = SupportAgent(backend)
    session = Session()

    print("Subscription Retention Agent")
    identifier = input("Customer ID or email: ")

    while True:
        message = input("> ")
        if message.strip().lower() == "quit":
            break

        response = agent.respond(identifier, message, session)
        print(response.message)
        print(f"[action] {response.action}")
        print(f"[trace] {' | '.join(response.trace)}")


if __name__ == "__main__":
    main()
