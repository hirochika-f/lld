from __future__ import annotations

from dataclasses import dataclass
import re

from backend import SubscriptionBackend
from models import AgentResponse, PendingAction
from policies import (
    is_confirmation,
    is_plan_eligible,
    requires_handoff,
    requires_verified_identity,
)
from sessions import SessionStore


PLAN_PATTERN = re.compile(r"\bplan[ -]?([ab])\b", re.IGNORECASE)
CUSTOMER_PATTERN = re.compile(r"\bcustomer[ -]?([a-z])\b", re.IGNORECASE)


@dataclass(frozen=True)
class ParsedMessage:
    requested_plan_id: str | None
    referenced_customer_id: str | None
    confirmation: bool
    handoff: bool


def parse_message(message: str) -> ParsedMessage:
    plan_match = PLAN_PATTERN.search(message)
    customer_match = CUSTOMER_PATTERN.search(message)
    requested_plan_id = (
        f"plan-{plan_match.group(1).casefold()}" if plan_match else None
    )
    referenced_customer_id = (
        f"customer-{customer_match.group(1).casefold()}"
        if customer_match
        else None
    )
    return ParsedMessage(
        requested_plan_id=requested_plan_id,
        referenced_customer_id=referenced_customer_id,
        confirmation=is_confirmation(message),
        handoff=requires_handoff(message),
    )


def action_id_for(plan_id: str) -> str:
    return f"action-{plan_id}"


class SubscriptionChangeAgent:
    def __init__(
        self,
        session_store: SessionStore,
        backend: SubscriptionBackend,
    ) -> None:
        self.session_store = session_store
        self.backend = backend

    def handle_message(self, session_id: str, message: str) -> AgentResponse:
        session = self.session_store.get_session(session_id)

        if session.handoff:
            return AgentResponse(
                success=False,
                message="A human agent will continue this conversation.",
                requires_handoff=True,
            )

        parsed = parse_message(message)

        if not requires_verified_identity(session):
            return AgentResponse(
                success=False,
                message="Please verify your identity before changing a plan.",
            )

        handoff_response: AgentResponse | None = None
        if parsed.handoff:
            session.handoff = True
            handoff_response = AgentResponse(
                success=False,
                message="A human agent will continue this conversation.",
                requires_handoff=True,
            )

        if parsed.requested_plan_id is not None:
            preview = self._prepare_plan_change(
                session_id=session_id,
                plan_id=parsed.requested_plan_id,
                referenced_customer_id=parsed.referenced_customer_id,
            )
            if not parsed.confirmation:
                return handoff_response or preview

        if parsed.confirmation:
            confirmation_response = self._confirm_pending_action(session_id)
            return handoff_response or confirmation_response

        if handoff_response is not None:
            return handoff_response

        return AgentResponse(
            success=False,
            message="Tell me which plan you want to change to.",
        )

    def _prepare_plan_change(
        self,
        *,
        session_id: str,
        plan_id: str,
        referenced_customer_id: str | None,
    ) -> AgentResponse:
        session = self.session_store.get_session(session_id)
        assert session.verified_customer_id is not None

        if not is_plan_eligible(
            self.backend,
            session.verified_customer_id,
            plan_id,
        ):
            session.pending_action = None
            session.last_presented_action_id = None
            plan = self.backend.get_plan(plan_id)
            return AgentResponse(
                success=False,
                message=f"{plan.display_name} is not eligible for this customer.",
                plan_id=plan_id,
            )

        pending_action = PendingAction(
            action_id=action_id_for(plan_id),
            customer_id=(
                referenced_customer_id or session.verified_customer_id
            ),
            target_plan_id=plan_id,
        )

        if session.pending_action is None:
            session.pending_action = pending_action
        session.last_presented_action_id = pending_action.action_id

        plan = self.backend.get_plan(plan_id)
        return AgentResponse(
            success=True,
            message=f"{plan.display_name} is ready. Please confirm the change.",
            plan_id=plan_id,
        )

    def _confirm_pending_action(self, session_id: str) -> AgentResponse:
        session = self.session_store.get_session(session_id)
        pending_action = session.pending_action
        if pending_action is None:
            return AgentResponse(
                success=False,
                message="There is no pending plan change to confirm.",
            )

        self.backend.change_subscription(
            action_id=pending_action.action_id,
            customer_id=pending_action.customer_id,
            target_plan_id=pending_action.target_plan_id,
        )
        authoritative = self.backend.get_subscription(pending_action.customer_id)
        plan = self.backend.get_plan(authoritative.plan_id)
        session.pending_action = None
        session.last_presented_action_id = None
        return AgentResponse(
            success=True,
            message=f"Your subscription is now {plan.display_name}.",
            plan_id=authoritative.plan_id,
        )
