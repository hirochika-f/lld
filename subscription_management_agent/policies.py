from __future__ import annotations

import re

from backend import SubscriptionBackend
from models import Session


HANDOFF_PHRASES = (
    "human agent",
    "speak to a person",
    "representative",
)

CONFIRMATION_PATTERN = re.compile(
    r"\b(?:yes|confirm|go ahead)\b",
    re.IGNORECASE,
)


def requires_verified_identity(session: Session) -> bool:
    return session.verified_customer_id is not None


def requires_handoff(message: str) -> bool:
    normalized = message.casefold()
    return any(phrase in normalized for phrase in HANDOFF_PHRASES)


def is_confirmation(message: str) -> bool:
    return CONFIRMATION_PATTERN.search(message) is not None


def is_plan_eligible(
    backend: SubscriptionBackend,
    customer_id: str,
    plan_id: str,
) -> bool:
    return backend.is_eligible(customer_id, plan_id)
