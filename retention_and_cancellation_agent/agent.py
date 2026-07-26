from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import TypeVar

from backend import (
    Backend,
    CustomerNotFoundError,
    TransientBackendError,
)
from models import AgentResponse, Customer, Session
from policies import retention_eligible


T = TypeVar("T")


class SupportAgent:
    def __init__(self, backend: Backend) -> None:
        self._backend = backend

    def respond(
        self,
        identifier: str,
        message: str,
        session: Session = Session(),
    ) -> AgentResponse:
        trace: list[str] = []

        try:
            customer = self._backend.get_customer(identifier)
        except CustomerNotFoundError:
            return AgentResponse(
                message="I could not find that customer.",
                action="customer_not_found",
                trace=[f"lookup:miss:{identifier}"],
            )

        trace.append(f"lookup:hit:{customer.customer_id}")
        session.customer_id = customer.customer_id
        trace.append(f"session:pending={session.pending_action}")

        if session.pending_action == "retention_offer":
            return self._handle_retention_follow_up(
                customer,
                message,
                session,
                trace,
            )

        if session.pending_action == "cancel_confirmation":
            return self._handle_cancel_confirmation(
                customer,
                message,
                session,
                trace,
            )

        intent = self._classify_intent(message)
        trace.append(f"intent:{intent}")

        if intent == "subscription_status":
            return AgentResponse(
                message=(
                    f"Your {customer.plan} subscription is "
                    f"{customer.status}."
                ),
                action="show_status",
                trace=trace,
            )

        if intent == "cancel_subscription":
            if customer.status != "active":
                return AgentResponse(
                    message="This subscription is already inactive.",
                    action="already_inactive",
                    trace=trace,
                )

            eligible = retention_eligible(customer, date.today())
            trace.append(f"policy:retention_eligible={eligible}")
            if eligible:
                session.pending_action = "retention_offer"
                return AgentResponse(
                    message=(
                        "I can apply a 20% retention discount. "
                        "Reply 'accept' to take it or 'decline' "
                        "to continue cancellation."
                    ),
                    action="offer_retention",
                    trace=trace,
                )

            session.pending_action = "cancel_confirmation"
            return AgentResponse(
                message=(
                    "Please reply 'yes' to confirm cancellation, "
                    "or 'no' to keep the subscription."
                ),
                action="request_cancellation_confirmation",
                trace=trace,
            )

        return AgentResponse(
            message="I am not sure how to help with that request.",
            action="unknown_intent",
            trace=trace,
        )

    def _handle_retention_follow_up(
        self,
        customer: Customer,
        message: str,
        session: Session,
        trace: list[str],
    ) -> AgentResponse:
        normalized = message.strip().lower()
        if normalized == "accept":
            self._backend.apply_retention_offer(customer.customer_id)
            session.pending_action = None
            return AgentResponse(
                message="The 20% retention discount has been applied.",
                action="retention_applied",
                trace=trace + ["tool:apply_retention_offer"],
            )

        if normalized == "decline":
            session.pending_action = "cancel_confirmation"
            return AgentResponse(
                message="Reply 'yes' to confirm cancellation.",
                action="request_cancellation_confirmation",
                trace=trace,
            )

        return AgentResponse(
            message="Please reply 'accept' or 'decline'.",
            action="clarify_retention_response",
            trace=trace,
        )

    def _handle_cancel_confirmation(
        self,
        customer: Customer,
        message: str,
        session: Session,
        trace: list[str],
    ) -> AgentResponse:
        normalized = message.strip().lower()
        if normalized == "no":
            session.pending_action = None
            return AgentResponse(
                message="Your subscription will remain active.",
                action="cancellation_aborted",
                trace=trace,
            )

        if normalized != "yes":
            return AgentResponse(
                message="Please reply 'yes' or 'no'.",
                action="clarify_cancellation_confirmation",
                trace=trace,
            )

        self._run_with_retry(
            lambda: self._backend.cancel_subscription(customer.customer_id),
            max_attempts=2,
            trace=trace,
        )
        session.pending_action = None
        return AgentResponse(
            message="Your subscription has been canceled.",
            action="subscription_canceled",
            trace=trace,
        )

    @staticmethod
    def _classify_intent(message: str) -> str:
        normalized = message.lower()
        if "cancel" in normalized or "terminate" in normalized:
            return "cancel_subscription"
        if "status" in normalized or "plan" in normalized:
            return "subscription_status"
        return "unknown"

    @staticmethod
    def _run_with_retry(
        operation: Callable[[], T],
        max_attempts: int,
        trace: list[str],
    ) -> T:
        for attempt in range(1, max_attempts):
            trace.append(f"tool:attempt={attempt}")
            try:
                return operation()
            except TransientBackendError:
                trace.append(f"tool:transient_failure={attempt}")
                if attempt == max_attempts:
                    raise
        raise RuntimeError("operation did not return")
