from __future__ import annotations

from backend import CURRENT_DAY, InMemoryBackend
from history import is_in_cooldown
from models import (
    AgentResponse,
    Customer,
    Explanation,
    InventoryRecord,
    Product,
    Recommendation,
    RecommendationEvent,
    ScoreBreakdown,
)
from policies import is_hard_eligible
from ranking import apply_diversity, deduplicate_products, score_products, sort_scored_products


class RecommendationAgent:
    def __init__(self, backend: InMemoryBackend, current_day: int = CURRENT_DAY) -> None:
        self.backend = backend
        self.current_day = current_day

    def recommend(self, customer_id: str, limit: int = 3) -> AgentResponse:
        customer = self.backend.get_customer(customer_id)
        catalog = self.backend.get_catalog(customer_id)
        inventory_records = self.backend.get_inventory(customer_id)
        inventory_by_id = {record.product_id: record for record in inventory_records}
        history = self.backend.get_recommendation_history(customer_id)

        unique_catalog = deduplicate_products(catalog)
        scorable_catalog = [
            product for product in unique_catalog if product.product_id in inventory_by_id
        ]
        scored = score_products(customer, scorable_catalog, inventory_by_id)
        ranked = sort_scored_products(scored)
        selected = apply_diversity(ranked)[:limit]
        selected = [
            item
            for item in selected
            if self._is_recommendable(
                customer,
                item.product,
                inventory_by_id.get(item.product.product_id),
                history,
            )
        ]

        source_breakdowns = [item.breakdown for item in scored]
        recommendations: list[Recommendation] = []
        for item, breakdown in zip(selected, source_breakdowns):
            explanation = self._build_explanation(breakdown)
            recommendations.append(
                Recommendation(
                    product_id=item.product.product_id,
                    name=item.product.name,
                    monthly_price_cents=item.product.monthly_price_cents,
                    score=item.breakdown.total_score,
                    explanation=explanation,
                )
            )

        for recommendation in recommendations:
            self.backend.save_recommendation_event(
                customer_id=customer_id,
                product_id=recommendation.product_id,
                day=self.current_day,
            )

        return AgentResponse(customer_id=customer_id, recommendations=tuple(recommendations))

    def _is_recommendable(
        self,
        customer: Customer,
        product: Product,
        inventory: InventoryRecord | None,
        history: list[RecommendationEvent],
    ) -> bool:
        return is_hard_eligible(customer, product, inventory) and not is_in_cooldown(
            product.product_id, history, self.current_day
        )

    @staticmethod
    def _build_explanation(breakdown: ScoreBreakdown) -> Explanation:
        return Explanation(
            product_id=breakdown.product_id,
            total_score=breakdown.total_score,
            summary=(
                f"usage={breakdown.usage_fit}, budget={breakdown.budget_fit}, "
                f"brand={breakdown.brand_fit}, campaign={breakdown.campaign}"
            ),
        )
