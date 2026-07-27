from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


OrderStatus = Literal[
    "delivered",
    "refund_pending",
    "exchange_pending",
]
Resolution = Literal["refund", "exchange"]
Outcome = Literal[
    "refund_created",
    "exchange_created",
    "return_denied",
    "already_in_progress",
    "handoff",
]


@dataclass(frozen=True)
class Customer:
    customer_id: str
    timezone: str


@dataclass(frozen=True)
class OrderItem:
    order_id: str
    customer_id: str
    sku: str
    category: str
    unit_price_yen: int
    delivered_at: datetime
    status: OrderStatus = "delivered"


@dataclass(frozen=True)
class ReturnRequest:
    order_id: str
    reason: str
    preferred_resolution: Resolution
    requested_at: datetime


@dataclass
class Session:
    customer_id: str
    active_order_id: str | None = None
    turn_count: int = 0
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AgentResponse:
    outcome: Outcome
    message: str
    refund_amount_yen: int | None = None
    return_label_id: str | None = None
