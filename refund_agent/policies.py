from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from models import Customer, OrderItem


RETURN_WINDOW_DAYS = 30
RESTOCKING_FEE_BPS_BY_CATEGORY = {
    "electronics": 1_000,  # 10.00%
    "home": 0,
    "apparel": 0,
}


def is_within_return_window(
    *,
    order: OrderItem,
    customer: Customer,
    requested_at: datetime,
) -> bool:
    """Return True when the request is within the allowed local-date window."""

    customer_zone = ZoneInfo(customer.timezone)
    delivered_local_date = order.delivered_at.date()
    requested_local_date = requested_at.astimezone(customer_zone).date()
    elapsed_days = (requested_local_date - delivered_local_date).days
    return elapsed_days < RETURN_WINDOW_DAYS


def calculate_refund_amount_yen(order: OrderItem) -> int:
    """Calculate the deterministic refund amount for an eligible order."""

    fee_bps = RESTOCKING_FEE_BPS_BY_CATEGORY.get(order.category, 0)
    fee_rate = Decimal(fee_bps) / Decimal("100000")
    refund = Decimal(order.unit_price_yen) * (Decimal("1") - fee_rate)
    return int(refund.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
