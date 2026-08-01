from __future__ import annotations

from models import PendingAction, Session, Subscription
from scenarios import make_agent


def test_normal_plan_change_updates_authoritative_state() -> None:
    agent, store, backend = make_agent(
        session=Session("session-normal", "customer-a"),
        subscriptions=[Subscription("customer-a", "plan-a")],
        eligible_pairs={("customer-a", "plan-b")},
    )

    preview = agent.handle_message("session-normal", "Switch me to Plan B.")
    session = store.get_session("session-normal")
    assert preview.plan_id == "plan-b"
    assert session.pending_action == PendingAction(
        "action-plan-b", "customer-a", "plan-b"
    )

    response = agent.handle_message("session-normal", "Yes, confirm it.")
    assert len(backend.get_tool_calls()) == 1
    assert backend.get_subscription("customer-a").plan_id == "plan-b"
    assert response.plan_id == "plan-b"


def test_unverified_customer_is_rejected_without_side_effects() -> None:
    agent, store, backend = make_agent(
        session=Session("session-unverified", None),
        subscriptions=[Subscription("customer-a", "plan-a")],
        eligible_pairs={("customer-a", "plan-b")},
    )

    response = agent.handle_message("session-unverified", "Switch me to Plan B.")

    assert response.success is False
    assert store.get_session("session-unverified").pending_action is None
    assert backend.get_tool_calls() == []
    assert backend.get_subscription("customer-a").plan_id == "plan-a"


def test_ineligible_plan_is_rejected_without_side_effects() -> None:
    agent, store, backend = make_agent(
        session=Session("session-ineligible", "customer-a"),
        subscriptions=[Subscription("customer-a", "plan-a")],
        eligible_pairs={("customer-a", "plan-a")},
    )

    response = agent.handle_message("session-ineligible", "Switch me to Plan B.")

    assert response.success is False
    assert store.get_session("session-ineligible").pending_action is None
    assert backend.get_tool_calls() == []
    assert backend.get_subscription("customer-a").plan_id == "plan-a"
