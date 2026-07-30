from models import Customer, InventoryRecord, Product


def is_hard_eligible(
    customer: Customer,
    product: Product,
    inventory: InventoryRecord | None,
) -> bool:
    if customer.region not in product.supported_regions:
        return False
    if product.required_capability not in customer.device_capabilities:
        return False
    if customer.age < product.minimum_age:
        return False
    if product.monthly_price_cents > customer.budget_cents:
        return False
    if product.product_id in customer.current_product_ids:
        return False
    if inventory is None or inventory.available_units <= 0:
        return False
    return True
