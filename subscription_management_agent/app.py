from __future__ import annotations

import argparse

from agent import SubscriptionChangeAgent
from backend import SubscriptionBackend
from models import Plan, Session, Subscription
from scenarios import run_named_scenario
from sessions import SessionStore


def build_demo_agent() -> SubscriptionChangeAgent:
    store = SessionStore([Session("demo", "customer-a")])
    backend = SubscriptionBackend(
        subscriptions=[Subscription("customer-a", "plan-a")],
        plans=[Plan("plan-a", "Plan A"), Plan("plan-b", "Plan B")],
        eligible_pairs={
            ("customer-a", "plan-a"),
            ("customer-a", "plan-b"),
        },
    )
    return SubscriptionChangeAgent(store, backend)


def run_interactive_demo() -> None:
    agent = build_demo_agent()
    print("Subscription Change Agent. Type 'quit' to exit.")
    while True:
        message = input("Customer: ").strip()
        if message.casefold() in {"quit", "exit"}:
            return
        response = agent.handle_message("demo", message)
        print(f"Agent: {response.message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenario",
        choices=("handoff", "identity", "replacement"),
    )
    args = parser.parse_args()
    if args.scenario:
        run_named_scenario(args.scenario)
    else:
        run_interactive_demo()


if __name__ == "__main__":
    main()
