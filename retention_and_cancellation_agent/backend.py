from __future__ import annotations

from copy import deepcopy
from datetime import date

from models import Customer


class CustomerNotFoundError(Exception):
    pass


class TransientBackendError(Exception):
    pass


class PermanentBackendError(Exception):
    pass


_CUSTOMERS = {
    "cust_001": Customer(
        customer_id="cust_001",
        email="alice@example.com",
        status="active",
        plan="pro",
        monthly_price_cents=3000,
        tenure_months=18,
        payment_failures=0,
        last_retention_offer_date=None,
    ),
    "cust_002": Customer(
        customer_id="cust_002",
        email="bob@example.com",
        status="active",
        plan="basic",
        monthly_price_cents=1000,
        tenure_months=4,
        payment_failures=0,
        last_retention_offer_date=None,
    ),
    "cust_003": Customer(
        customer_id="cust_003",
        email="carol@example.com",
        status="active",
        plan="premium",
        monthly_price_cents=5000,
        tenure_months=30,
        payment_failures=2,
        last_retention_offer_date=None,
    ),
    "cust_004": Customer(
        customer_id="cust_004",
        email="dana@example.com",
        status="active",
        plan="basic",
        monthly_price_cents=1500,
        tenure_months=6,
        payment_failures=0,
        last_retention_offer_date=None,
    ),
}


class Backend:
    def __init__(self) -> None:
        self._customers = deepcopy(_CUSTOMERS)
        self._transient_cancel_failures_remaining = {"cust_004": 1}

    def get_customer(self, identifier: str) -> Customer:
        if identifier in self._customers:
            return self._customers[identifier]

        email_index = {
            customer.email.lower(): customer
            for customer in self._customers.values()
        }
        customer = email_index.get(identifier.lower())
        if customer is None:
            raise CustomerNotFoundError(identifier)
        return customer

    def cancel_subscription(self, customer_id: str) -> Customer:
        failures_remaining = self._transient_cancel_failures_remaining.get(
            customer_id,
            0,
        )
        if failures_remaining > 0:
            self._transient_cancel_failures_remaining[customer_id] = (
                failures_remaining - 1
            )
            raise TransientBackendError(
                f"temporary write failure for {customer_id}"
            )

        customer = self._customers.get(customer_id)
        if customer is None:
            raise PermanentBackendError(f"unknown customer: {customer_id}")
        if customer.status != "active":
            raise PermanentBackendError(
                f"subscription is not active: {customer_id}"
            )

        customer.status = "canceled"
        return customer

    def apply_retention_offer(self, customer_id: str) -> Customer:
        customer = self._customers.get(customer_id)
        if customer is None:
            raise PermanentBackendError(f"unknown customer: {customer_id}")
        customer.last_retention_offer_date = date.today()
        return customer
