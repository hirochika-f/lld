from typing import Any
import json


class InvalidProductResponseError(Exception):
    pass


def parse_product_response(
    payload: dict[str, Any],
    ) -> dict[str, Any]:
    data = payload.get("data", {})
    catalog = data.get("catalog", {})
    product = catalog.get("product", {})

    identity = product.get("identity", {})
    product_id = identity.get("product_id")

    details = product.get("details", {})
    display_name = details.get("display_name")
    status = details.get("status", "unknown")
    
    if product_id is None:
        raise InvalidProductResponseError(
            "Missing required field: "
            "data.catalog.product.identity.product_id"
        )
    if display_name is None:
        raise InvalidProductResponseError(
            "Missing required field: "
            "data.catalog.product.details.display_name"
        )

    commerce = product.get("commerce", {})
    price = commerce.get("price", {})
    price_amount = price.get("amount")
    currency = price.get("currency")
    inventory = commerce.get("inventory", {})
    available_quantity = inventory.get("available_quantity", 0)

    associations = product.get("associations", {})
    related_products = associations.get("related_products", [])
    normalized_related_products = []
    for raw_related_product in related_products:
        related_product_id = raw_related_product.get("target", {}).get("product_id")
        if related_product_id is None:
            continue
        relation_type = raw_related_product.get("relation_type", "unknown")
        normalized_related = {
            "product_id": related_product_id,
            "relation_type": relation_type
        }
        normalized_related_products.append(normalized_related)

    return {
        "id": product_id,
        "name": display_name,
        "status": status,
        "available_quantity": available_quantity,
        "price_amount": price_amount,
        "currency": currency,
        "related": normalized_related_products
    }


if __name__ == "__main__":
    expected = {
        "id": "p100",
        "name": "Home Hub",
        "status": "active",
        "available_quantity": 25,
        "price_amount": 12980,
        "currency": "JPY",
        "related": [
            {
                "product_id": "p200",
                "relation_type": "accessory",
            },
            {
                "product_id": "p300",
                "relation_type": "alternative",
            }
        ]
    }

    with open("./get_product_response.json", "r") as f:
        response = json.load(f)
        actual = parse_product_response(response)
        assert actual == expected
