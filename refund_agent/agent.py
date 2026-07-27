from __future__ import annotations

from backend import InMemoryCommerceBackend, InventoryServiceUnavailable
from models import AgentResponse, ReturnRequest, Session
from policies import calculate_refund_amount_yen, is_within_return_window


class ReturnsAgent:
    """Orchestrates deterministic policies and backend tool calls."""

    def __init__(self, backend: InMemoryCommerceBackend) -> None:
        self._backend = backend

    def handle_return_request(
        self,
        *,
        session: Session,
        request: ReturnRequest,
    ) -> AgentResponse:
        session.turn_count += 1
        session.active_order_id = request.order_id

        customer = self._backend.get_customer(session.customer_id)
        order = self._backend.get_order(request.order_id)

        if order.customer_id != customer.customer_id:
            return AgentResponse(
                outcome="return_denied",
                message="This order does not belong to the current customer.",
            )

        if order.status != "delivered":
            return AgentResponse(
                outcome="already_in_progress",
                message="A return or exchange is already in progress for this order.",
            )

        if not is_within_return_window(
            order=order,
            customer=customer,
            requested_at=request.requested_at,
        ):
            return AgentResponse(
                outcome="return_denied",
                message="The return window has expired.",
            )

        if request.preferred_resolution == "exchange":
            try:
                stock = self._get_replacement_stock_or_zero(order.sku)
            except InventoryServiceUnavailable:
                return AgentResponse(
                    outcome="handoff",
                    message=(
                        "Replacement inventory could not be verified. "
                        "No refund or exchange was created; a specialist must review it."
                    ),
                )

            if stock > 0:
                self._backend.reserve_replacement(order.sku)
                label_id = self._backend.create_return_label(order.order_id)
                self._backend.update_order_status(order.order_id, "exchange_pending")
                return AgentResponse(
                    outcome="exchange_created",
                    message="A replacement and return label were created.",
                    return_label_id=label_id,
                )

        refund_amount = calculate_refund_amount_yen(order)
        self._backend.issue_refund(order.order_id, refund_amount)
        label_id = self._backend.create_return_label(order.order_id)
        self._backend.update_order_status(order.order_id, "refund_pending")
        return AgentResponse(
            outcome="refund_created",
            message="A refund and return label were created.",
            refund_amount_yen=refund_amount,
            return_label_id=label_id,
        )

    def _get_replacement_stock_or_zero(self, sku: str) -> int:
        try:
            return self._backend.get_replacement_stock(sku)
        except InventoryServiceUnavailable:
            return 0
