from models import Customer, InventoryRecord, Product, ScoreBreakdown, ScoredProduct


def deduplicate_products(products: list[Product]) -> list[Product]:
    seen: set[str] = set()
    unique: list[Product] = []
    for product in products:
        if product.product_id in seen:
            continue
        seen.add(product.product_id)
        unique.append(product)
    return unique


def score_products(
    customer: Customer,
    products: list[Product],
    inventory_by_id: dict[str, InventoryRecord],
) -> list[ScoredProduct]:
    scored: list[ScoredProduct] = []
    for product in products:
        usage_fit = 40 if product.data_gb >= customer.monthly_data_gb else 15
        if product.monthly_price_cents * 10 <= customer.budget_cents * 7:
            budget_fit = 20
        else:
            budget_fit = 10
        brand_fit = 10 if customer.preferred_brand == product.brand else 0
        breakdown = ScoreBreakdown(
            product_id=product.product_id,
            usage_fit=usage_fit,
            budget_fit=budget_fit,
            brand_fit=brand_fit,
            campaign=product.campaign_points,
        )
        scored.append(
            ScoredProduct(
                product=product,
                available_units=inventory_by_id[product.product_id].available_units,
                breakdown=breakdown,
            )
        )
    return scored


def sort_scored_products(products: list[ScoredProduct]) -> list[ScoredProduct]:
    return sorted(
        products,
        key=lambda item: (
            item.breakdown.total_score,
            item.product.monthly_price_cents,
            item.available_units,
            item.product.product_id,
        ),
        reverse=True,
    )


def apply_diversity(products: list[ScoredProduct]) -> list[ScoredProduct]:
    """Stable hook for future category quotas; currently preserves ranking."""
    return list(products)
