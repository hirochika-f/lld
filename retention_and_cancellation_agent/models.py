from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Customer:
    customer_id: str
    email: str
    status: str
    plan: str
    monthly_price_cents: int
    tenure_months: int
    payment_failures: int
    last_retention_offer_date: Optional[date] = None


@dataclass
class Session:
    customer_id: Optional[str] = None
    pending_action: Optional[str] = None


@dataclass
class AgentResponse:
    message: str
    action: str
    trace: list[str] = field(default_factory=list)
