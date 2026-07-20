
from typing import Any


def make_product_payload(
    product_id: str,
    name: str,
    *,
    status: str = "active",
    available_quantity: int = 1,
    price_amount: int | None = None,
    currency: str | None = "JPY",
    related: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    related = related or []

    return {
        "data": {
            "catalog": {
                "product": {
                    "identity": {
                        "product_id": product_id,
                    },
                    "details": {
                        "display_name": name,
                        "status": status,
                    },
                    "commerce": {
                        "price": {
                            "amount": price_amount,
                            "currency": currency,
                        },
                        "inventory": {
                            "available_quantity": available_quantity,
                        },
                    },
                    "associations": {
                        "related_products": [
                            {
                                "target": {
                                    "product_id": related_product_id,
                                },
                                "relation_type": relation_type,
                            }
                            for related_product_id, relation_type in related
                        ],
                    },
                },
            },
        },
    }


PRODUCT_RESPONSES = {
    "p100": make_product_payload(
        "p100",
        "Home Hub",
        available_quantity=25,
        price_amount=12980,
        related=[
            ("p200", "accessory"),
            ("p300", "alternative"),
            ("p404", "accessory"),
        ],
    ),
    "p200": make_product_payload(
        "p200",
        "Charging Dock",
        available_quantity=12,
        price_amount=4980,
        related=[
            ("p400", "accessory"),
            ("p500", "replacement"),
        ],
    ),
    "p300": make_product_payload(
        "p300",
        "Home Hub Pro",
        available_quantity=0,
        price_amount=24980,
        related=[
            ("p400", "accessory"),
            ("p100", "alternative"),
        ],
    ),
    "p400": make_product_payload(
        "p400",
        "Ethernet Adapter",
        available_quantity=8,
        price_amount=2980,
        related=[
            ("p100", "accessory"),
        ],
    ),
    "p500": make_product_payload(
        "p500",
        "Legacy Power Adapter",
        status="inactive",
        available_quantity=4,
        price_amount=1980,
        related=[
            ("p600", "accessory"),
        ],
    ),
    "p600": make_product_payload(
        "p600",
        "USB-C Power Adapter",
        available_quantity=2,
        price_amount=3980,
    ),
}
