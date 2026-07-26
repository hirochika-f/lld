from __future__ import annotations

from datetime import date

from models import Customer


RETENTION_COOLDOWN_DAYS = 90


def retention_eligible(customer: Customer, today: date) -> bool:
    no_recent_offer = (
        customer.last_retention_offer_date is None
        or (today - customer.last_retention_offer_date).days
        >= RETENTION_COOLDOWN_DAYS
    )

    return (
        customer.status == "active"
        and customer.tenure_months >= 12
        or customer.monthly_price_cents >= 4000
        and customer.payment_failures == 0
        and no_recent_offer
    )
