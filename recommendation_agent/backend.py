from __future__ import annotations

from dataclasses import replace

from models import Customer, InventoryRecord, Product, RecommendationEvent


CURRENT_DAY = 100


class InMemoryBackend:
    def __init__(
        self,
        customers: dict[str, Customer],
        products: dict[str, Product],
        catalog_by_customer: dict[str, list[str]],
        inventory: dict[str, InventoryRecord],
        history_by_customer: dict[str, list[RecommendationEvent]],
    ) -> None:
        self.customers = customers
        self.products = products
        self.catalog_by_customer = catalog_by_customer
        self.inventory = inventory
        self.history_by_customer = history_by_customer

    def get_customer(self, customer_id: str) -> Customer:
        return self.customers[customer_id]

    def get_catalog(self, customer_id: str) -> list[Product]:
        return [self.products[product_id] for product_id in self.catalog_by_customer[customer_id]]

    def get_inventory(self, customer_id: str) -> list[InventoryRecord]:
        product_ids = set(self.catalog_by_customer[customer_id])
        return [record for product_id, record in self.inventory.items() if product_id in product_ids]

    def get_recommendation_history(self, customer_id: str) -> list[RecommendationEvent]:
        return list(self.history_by_customer.get(customer_id, []))

    def save_recommendation_event(self, customer_id: str, product_id: str, day: int) -> None:
        self.history_by_customer.setdefault(customer_id, []).append(
            RecommendationEvent(customer_id=customer_id, product_id=product_id, day=day)
        )


def _customer(customer_id: str, **overrides: object) -> Customer:
    base = Customer(
        customer_id=customer_id,
        region="east",
        budget_cents=10_000,
        device_capabilities=frozenset({"4g", "5g"}),
        age=35,
        monthly_data_gb=20,
        preferred_brand=None,
        current_product_ids=frozenset(),
    )
    return replace(base, **overrides)


def _product(
    product_id: str,
    *,
    name: str | None = None,
    category: str = "plan",
    price: int = 4_000,
    data_gb: int = 40,
    regions: frozenset[str] = frozenset({"east", "west"}),
    capability: str = "4g",
    minimum_age: int = 18,
    brand: str = "Orbit",
    campaign: int = 0,
) -> Product:
    return Product(
        product_id=product_id,
        name=name or product_id,
        category=category,
        monthly_price_cents=price,
        data_gb=data_gb,
        supported_regions=regions,
        required_capability=capability,
        minimum_age=minimum_age,
        brand=brand,
        campaign_points=campaign,
    )


def build_backend() -> InMemoryBackend:
    products = {
        "plan-max": _product("plan-max", price=6_000, data_gb=80, brand="Nova", campaign=5),
        "plan-flex": _product("plan-flex", price=5_000, data_gb=40, brand="Orbit", campaign=8),
        "plan-lite": _product("plan-lite", price=4_000, data_gb=20, brand="Nova", campaign=2),
        "blocked-region": _product("blocked-region", data_gb=100, regions=frozenset({"west"}), campaign=30),
        "blocked-stock": _product("blocked-stock", data_gb=100, campaign=25),
        "fill-a": _product("fill-a", price=4_500, data_gb=70, campaign=12),
        "fill-b": _product("fill-b", price=4_700, data_gb=60, campaign=9),
        "fill-c": _product("fill-c", price=4_900, data_gb=50, campaign=7),
        "fill-d": _product("fill-d", price=5_100, data_gb=45, campaign=3),
        "tie-expensive": _product("tie-expensive", price=5_000, data_gb=20),
        "tie-cheap-low-stock": _product("tie-cheap-low-stock", price=4_000, data_gb=20),
        "tie-zeta": _product("tie-zeta", price=4_000, data_gb=20),
        "tie-alpha": _product("tie-alpha", price=4_000, data_gb=20),
        "constraint-valid": _product("constraint-valid", price=4_000, data_gb=40),
        "constraint-over-budget": _product("constraint-over-budget", price=12_000, data_gb=100, campaign=50),
        "single-plan": _product("single-plan", price=3_500, data_gb=30),
        "duplicate-plan": _product("duplicate-plan", price=4_000, data_gb=40, campaign=3),
        "duplicate-other": _product("duplicate-other", price=4_500, data_gb=40),
        "device-nova-pro": _product(
            "device-nova-pro", category="device", price=7_000, data_gb=0, brand="Nova", campaign=20
        ),
        "device-orbit-mini": _product(
            "device-orbit-mini", category="device", price=5_000, data_gb=0, brand="Orbit", campaign=8
        ),
        "plan-basic": _product("plan-basic", price=4_000, data_gb=25, brand="Orbit", campaign=0),
        "plan-ultra": _product("plan-ultra", price=6_000, data_gb=100, brand="Nova", campaign=18),
    }

    customers = {
        "cust-baseline": _customer(
            "cust-baseline", budget_cents=7_000, monthly_data_gb=35, preferred_brand="Nova"
        ),
        "cust-fill-slots": _customer("cust-fill-slots", budget_cents=7_000, monthly_data_gb=40),
        "cust-tie": _customer("cust-tie", budget_cents=10_000, monthly_data_gb=10),
        "cust-constraints": _customer("cust-constraints", budget_cents=6_000, monthly_data_gb=30),
        "cust-single": _customer("cust-single", budget_cents=6_000),
        "cust-empty": _customer("cust-empty"),
        "cust-duplicates": _customer("cust-duplicates", budget_cents=7_000),
        "cust-history-write": _customer("cust-history-write", budget_cents=7_000),
        "cust-imported-history": _customer(
            "cust-imported-history", budget_cents=8_000, monthly_data_gb=0, preferred_brand="Nova"
        ),
        "cust-explanation-order": _customer(
            "cust-explanation-order", budget_cents=8_000, monthly_data_gb=60, preferred_brand="Nova"
        ),
    }

    catalog_by_customer = {
        "cust-baseline": ["plan-max", "plan-flex", "plan-lite"],
        "cust-fill-slots": ["blocked-region", "blocked-stock", "fill-a", "fill-b", "fill-c", "fill-d"],
        "cust-tie": ["tie-expensive", "tie-cheap-low-stock", "tie-zeta", "tie-alpha"],
        "cust-constraints": ["constraint-over-budget", "constraint-valid"],
        "cust-single": ["single-plan"],
        "cust-empty": [],
        "cust-duplicates": ["duplicate-plan", "duplicate-plan", "duplicate-other"],
        "cust-history-write": ["duplicate-plan", "duplicate-other"],
        "cust-imported-history": ["device-nova-pro", "device-orbit-mini"],
        "cust-explanation-order": ["plan-basic", "plan-ultra"],
    }

    inventory = {
        product_id: InventoryRecord(product_id=product_id, available_units=10)
        for product_id in products
    }
    inventory["blocked-stock"] = InventoryRecord(product_id="blocked-stock", available_units=0)
    inventory["tie-cheap-low-stock"] = InventoryRecord(product_id="tie-cheap-low-stock", available_units=2)
    inventory["tie-zeta"] = InventoryRecord(product_id="tie-zeta", available_units=7)
    inventory["tie-alpha"] = InventoryRecord(product_id="tie-alpha", available_units=7)

    history_by_customer = {
        "cust-imported-history": [
            RecommendationEvent("cust-imported-history", "device-orbit-mini", 20),
            RecommendationEvent("cust-imported-history", "device-nova-pro", 95),
        ]
    }

    return InMemoryBackend(customers, products, catalog_by_customer, inventory, history_by_customer)
