from __future__ import annotations

from agent import SubscriptionChangeAgent
from backend import SubscriptionBackend
from models import PendingAction, Plan, Session, Subscription
from sessions import SessionStore


def make_agent(
    *,
    session: Session,
    subscriptions: list[Subscription],
    eligible_pairs: set[tuple[str, str]],
) -> tuple[SubscriptionChangeAgent, SessionStore, SubscriptionBackend]:
    store = SessionStore([session])
    backend = SubscriptionBackend(
        subscriptions=subscriptions,
        plans=[Plan("plan-a", "Plan A"), Plan("plan-b", "Plan B")],
        eligible_pairs=eligible_pairs,
    )
    return SubscriptionChangeAgent(store, backend), store, backend


def build_handoff_scenario(
) -> tuple[SubscriptionChangeAgent, SessionStore, SubscriptionBackend]:
    return make_agent(
        session=Session(
            session_id="session-handoff",
            verified_customer_id="customer-a",
            pending_action=PendingAction(
                action_id="action-plan-b",
                customer_id="customer-a",
                target_plan_id="plan-b",
            ),
            last_presented_action_id="action-plan-b",
            handoff=False,
        ),
        subscriptions=[Subscription("customer-a", "plan-a")],
        eligible_pairs={("customer-a", "plan-b")},
    )


def build_identity_scenario(
) -> tuple[SubscriptionChangeAgent, SessionStore, SubscriptionBackend]:
    return make_agent(
        session=Session(
            session_id="session-identity",
            verified_customer_id="customer-a",
            pending_action=None,
            last_presented_action_id=None,
            handoff=False,
        ),
        subscriptions=[
            Subscription("customer-a", "plan-a"),
            Subscription("customer-b", "plan-a"),
        ],
        eligible_pairs={("customer-a", "plan-b")},
    )


def build_plan_replacement_incident(
) -> tuple[SubscriptionChangeAgent, SessionStore, SubscriptionBackend]:
    return make_agent(
        session=Session(
            session_id="session-replace",
            verified_customer_id="customer-a",
            pending_action=None,
            last_presented_action_id=None,
            handoff=False,
        ),
        subscriptions=[Subscription("customer-a", "plan-a")],
        eligible_pairs={
            ("customer-a", "plan-a"),
            ("customer-a", "plan-b"),
        },
    )


def _print_response(label: str, response: object) -> None:
    print(f"{label}: {response!r}")


def _run_handoff_scenario() -> None:
    agent, store, backend = build_handoff_scenario()
    message = "Yes, confirm it, and connect me to a human agent."
    print("Scenario 1 — Handoff during confirmation")
    print(f"Customer: {message}")
    response = agent.handle_message("session-handoff", message)
    session = store.get_session("session-handoff")
    _print_response("AgentResponse", response)
    print(f"Session.handoff: {session.handoff!r}")
    print(f"Session.pending_action: {session.pending_action!r}")
    print(f"ToolCalls: {backend.get_tool_calls()!r}")
    print(
        "AuthoritativeSubscription: "
        f"{backend.get_subscription('customer-a')!r}"
    )


def _run_identity_scenario() -> None:
    agent, store, backend = build_identity_scenario()
    print("Scenario 2 — Account identifier in customer text")
    request = "For customer-b, switch me to Plan B."
    print(f"Customer: {request}")
    preview = agent.handle_message("session-identity", request)
    session = store.get_session("session-identity")
    _print_response("PreviewResponse", preview)
    print(f"VerifiedCustomer: {session.verified_customer_id!r}")
    print(f"PendingActionAfterRequest: {session.pending_action!r}")
    print("Customer: Yes, confirm it.")
    response = agent.handle_message("session-identity", "Yes, confirm it.")
    _print_response("FinalResponse", response)
    print(f"ToolCalls: {backend.get_tool_calls()!r}")
    print(f"CustomerASubscription: {backend.get_subscription('customer-a')!r}")
    print(f"CustomerBSubscription: {backend.get_subscription('customer-b')!r}")


def _run_replacement_scenario() -> None:
    agent, store, backend = build_plan_replacement_incident()
    print("Incident — Replacement request activates the earlier plan")
    messages = (
        "I want to switch to Plan A.",
        "Actually, switch me to Plan B instead.",
        "Yes, confirm it.",
    )
    for turn, message in enumerate(messages, start=1):
        print(f"Turn {turn} Customer: {message}")
        response = agent.handle_message("session-replace", message)
        session = store.get_session("session-replace")
        _print_response(f"Turn {turn} AgentResponse", response)
        print(f"Turn {turn} Session.pending_action: {session.pending_action!r}")
        print(
            f"Turn {turn} Session.last_presented_action_id: "
            f"{session.last_presented_action_id!r}"
        )
    print(f"ToolCalls: {backend.get_tool_calls()!r}")
    print(
        "AuthoritativeSubscription: "
        f"{backend.get_subscription('customer-a')!r}"
    )


def run_named_scenario(name: str) -> None:
    runners = {
        "handoff": _run_handoff_scenario,
        "identity": _run_identity_scenario,
        "replacement": _run_replacement_scenario,
    }
    runners[name]()
