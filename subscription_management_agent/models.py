from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PendingAction:
    action_id: str
    customer_id: str
    target_plan_id: str


@dataclass
class Session:
    session_id: str
    verified_customer_id: str | None
    pending_action: PendingAction | None = None
    last_presented_action_id: str | None = None
    handoff: bool = False


@dataclass
class Subscription:
    customer_id: str
    plan_id: str


@dataclass(frozen=True)
class Plan:
    plan_id: str
    display_name: str


@dataclass(frozen=True)
class ToolCall:
    action_id: str
    customer_id: str
    target_plan_id: str


@dataclass(frozen=True)
class AgentResponse:
    success: bool
    message: str
    plan_id: str | None = None
    requires_handoff: bool = False
