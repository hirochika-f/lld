from __future__ import annotations

from agent import TroubleshootingAgent
from backend import Backend
from models import Session


def main() -> None:
    backend = Backend()
    agent = TroubleshootingAgent(backend)
    session = Session(
        session_id="demo-session",
        customer_id="cust-router",
        device_id="router-1",
    )
    response = agent.start(session)
    print(response.message)
    while response.action not in {"handoff", "review_resolution"}:
        user_input = input("> ")
        response = agent.confirm_current_step(session, user_input)
        print(response.message)


if __name__ == "__main__":
    main()
