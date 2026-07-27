from __future__ import annotations

from dataclasses import replace

from models import Customer, OrderItem, OrderStatus


class CustomerNotFoundError(KeyError):
    pass


class OrderNotFoundError(KeyError):
    pass


class InventoryServiceUnavailable(RuntimeError):
    pass


class InMemoryCommerceBackend:
    """Mock external systems used by the agent.

    The backend deliberately returns copies rather than exposing its internal
    records directly. This makes the mock behave more like a remote API.
    """

    def __init__(
        self,
        *,
        customers: list[Customer],
        orders: list[OrderItem],
        replacement_inventory: dict[str, int] | None = None,
        inventory_failures: set[str] | None = None,
    ) -> None:
        self._customers = {customer.customer_id: customer for customer in customers}
        self._orders = {order.order_id: order for order in orders}
        self._replacement_inventory = dict(replacement_inventory or {})
        self._inventory_failures = set(inventory_failures or set())

        self._order_cache: dict[str, OrderItem] = {}
        self.created_return_labels: list[str] = []
        self.issued_refunds: list[tuple[str, int]] = []
        self.reserved_replacements: list[str] = []

    def get_customer(self, customer_id: str) -> Customer:
        try:
            return self._customers[customer_id]
        except KeyError as exc:
            raise CustomerNotFoundError(customer_id) from exc

    def get_order(self, order_id: str) -> OrderItem:
        if order_id in self._order_cache:
            return self._order_cache[order_id]

        try:
            order = replace(self._orders[order_id])
        except KeyError as exc:
            raise OrderNotFoundError(order_id) from exc

        self._order_cache[order_id] = order
        return order

    def update_order_status(self, order_id: str, status: OrderStatus) -> None:
        try:
            self._orders[order_id] = replace(self._orders[order_id], status=status)
        except KeyError as exc:
            raise OrderNotFoundError(order_id) from exc

        # The remote record is updated here. Callers should observe that new
        # state on their next read.

    def get_replacement_stock(self, sku: str) -> int:
        if sku in self._inventory_failures:
            raise InventoryServiceUnavailable(
                f"replacement inventory temporarily unavailable for {sku}"
            )
        return self._replacement_inventory.get(sku, 0)

    def reserve_replacement(self, sku: str) -> None:
        stock = self._replacement_inventory.get(sku, 0)
        if stock <= 0:
            raise ValueError(f"no replacement stock for {sku}")
        self._replacement_inventory[sku] = stock - 1
        self.reserved_replacements.append(sku)

    def create_return_label(self, order_id: str) -> str:
        label_id = f"RMA-{order_id}-{len(self.created_return_labels) + 1}"
        self.created_return_labels.append(label_id)
        return label_id

    def issue_refund(self, order_id: str, amount_yen: int) -> None:
        self.issued_refunds.append((order_id, amount_yen))
