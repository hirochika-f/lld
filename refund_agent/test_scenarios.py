from __future__ import annotations

from datetime import datetime, timezone

from agent import ReturnsAgent
from backend import InMemoryCommerceBackend
from models import Customer, OrderItem, ReturnRequest, Session


def make_agent(
    order: OrderItem,
    *,
    replacement_inventory: dict[str, int] | None = None,
    inventory_failures: set[str] | None = None,
) -> tuple[ReturnsAgent, InMemoryCommerceBackend, Session]:
    customer = Customer(customer_id=order.customer_id, timezone="Asia/Tokyo")
    backend = InMemoryCommerceBackend(
        customers=[customer],
        orders=[order],
        replacement_inventory=replacement_inventory,
        inventory_failures=inventory_failures,
    )
    return ReturnsAgent(backend), backend, Session(customer_id=customer.customer_id)


def test_return_window_uses_customer_local_date_and_is_inclusive() -> None:
    """A request on local calendar day 30 is still eligible."""

    order = OrderItem(
        order_id="order-boundary",
        customer_id="cust-1",
        sku="LAMP-01",
        category="home",
        unit_price_yen=12_000,
        delivered_at=datetime(2026, 6, 1, 23, 30, tzinfo=timezone.utc),
    )
    agent, _, session = make_agent(order)

    response = agent.handle_return_request(
        session=session,
        request=ReturnRequest(
            order_id=order.order_id,
            reason="changed my mind",
            preferred_resolution="refund",
            requested_at=datetime(2026, 7, 1, 15, 15, tzinfo=timezone.utc),
        ),
    )

    assert response.outcome == "refund_created"
    assert response.refund_amount_yen == 12_000


def test_second_request_observes_updated_order_status() -> None:
    """A second request must not create a duplicate refund or return label."""

    order = OrderItem(
        order_id="order-duplicate",
        customer_id="cust-2",
        sku="CHAIR-01",
        category="home",
        unit_price_yen=18_000,
        delivered_at=datetime(2026, 7, 10, 2, 0, tzinfo=timezone.utc),
    )
    agent, backend, session = make_agent(order)
    request = ReturnRequest(
        order_id=order.order_id,
        reason="does not fit",
        preferred_resolution="refund",
        requested_at=datetime(2026, 7, 15, 2, 0, tzinfo=timezone.utc),
    )

    first = agent.handle_return_request(session=session, request=request)
    second = agent.handle_return_request(session=session, request=request)

    assert first.outcome == "refund_created"
    assert second.outcome == "already_in_progress"
    assert backend.issued_refunds == [(order.order_id, 18_000)]
    assert len(backend.created_return_labels) == 1


def test_electronics_restocking_fee_uses_basis_points() -> None:
    """A 1,000-basis-point fee means 10%, not 1%."""

    order = OrderItem(
        order_id="order-fee",
        customer_id="cust-3",
        sku="TABLET-01",
        category="electronics",
        unit_price_yen=50_000,
        delivered_at=datetime(2026, 7, 1, 1, 0, tzinfo=timezone.utc),
    )
    agent, backend, session = make_agent(order)

    response = agent.handle_return_request(
        session=session,
        request=ReturnRequest(
            order_id=order.order_id,
            reason="no longer needed",
            preferred_resolution="refund",
            requested_at=datetime(2026, 7, 5, 1, 0, tzinfo=timezone.utc),
        ),
    )

    assert response.outcome == "refund_created"
    assert response.refund_amount_yen == 45_000
    assert backend.issued_refunds == [(order.order_id, 45_000)]


def test_inventory_outage_causes_safe_handoff_without_side_effects() -> None:
    """The agent must not guess when exchange inventory cannot be verified."""

    order = OrderItem(
        order_id="order-outage",
        customer_id="cust-4",
        sku="JACKET-01",
        category="apparel",
        unit_price_yen=15_000,
        delivered_at=datetime(2026, 7, 20, 3, 0, tzinfo=timezone.utc),
    )
    agent, backend, session = make_agent(
        order,
        replacement_inventory={order.sku: 3},
        inventory_failures={order.sku},
    )

    response = agent.handle_return_request(
        session=session,
        request=ReturnRequest(
            order_id=order.order_id,
            reason="wrong size",
            preferred_resolution="exchange",
            requested_at=datetime(2026, 7, 22, 3, 0, tzinfo=timezone.utc),
        ),
    )

    assert response.outcome == "handoff"
    assert backend.issued_refunds == []
    assert backend.reserved_replacements == []
    assert backend.created_return_labels == []
