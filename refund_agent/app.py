from __future__ import annotations

from datetime import datetime, timezone

from agent import ReturnsAgent
from backend import InMemoryCommerceBackend
from models import Customer, OrderItem, ReturnRequest, Session


def build_demo_agent() -> ReturnsAgent:
    backend = InMemoryCommerceBackend(
        customers=[Customer(customer_id="cust-demo", timezone="Asia/Tokyo")],
        orders=[
            OrderItem(
                order_id="order-demo",
                customer_id="cust-demo",
                sku="HEADPHONES-01",
                category="electronics",
                unit_price_yen=20_000,
                delivered_at=datetime(2026, 7, 20, 1, 0, tzinfo=timezone.utc),
            )
        ],
        replacement_inventory={"HEADPHONES-01": 1},
    )
    return ReturnsAgent(backend)


def main() -> None:
    agent = build_demo_agent()
    session = Session(customer_id="cust-demo")

    print("Returns Agent demo. Type 'quit' to exit.")
    while True:
        resolution = input("Preferred resolution [refund/exchange]: ").strip()
        if resolution == "quit":
            return
        if resolution not in {"refund", "exchange"}:
            print("Please enter 'refund' or 'exchange'.")
            continue

        reason = input("Reason: ").strip()
        request = ReturnRequest(
            order_id="order-demo",
            reason=reason,
            preferred_resolution=resolution,
            requested_at=datetime.now(timezone.utc),
        )
        response = agent.handle_return_request(session=session, request=request)
        print(f"[{response.outcome}] {response.message}")
        if response.refund_amount_yen is not None:
            print(f"Refund: ¥{response.refund_amount_yen:,}")
        if response.return_label_id is not None:
            print(f"Return label: {response.return_label_id}")


if __name__ == "__main__":
    main()
