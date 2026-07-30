from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    customer_id: str
    region: str
    budget_cents: int
    device_capabilities: frozenset[str]
    age: int
    monthly_data_gb: int
    preferred_brand: str | None
    current_product_ids: frozenset[str]


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    category: str
    monthly_price_cents: int
    data_gb: int
    supported_regions: frozenset[str]
    required_capability: str
    minimum_age: int
    brand: str
    campaign_points: int


@dataclass(frozen=True)
class InventoryRecord:
    product_id: str
    available_units: int


@dataclass(frozen=True)
class RecommendationEvent:
    customer_id: str
    product_id: str
    day: int


@dataclass(frozen=True)
class ScoreBreakdown:
    product_id: str
    usage_fit: int
    budget_fit: int
    brand_fit: int
    campaign: int

    @property
    def total_score(self) -> int:
        return self.usage_fit + self.budget_fit + self.brand_fit + self.campaign


@dataclass(frozen=True)
class ScoredProduct:
    product: Product
    available_units: int
    breakdown: ScoreBreakdown


@dataclass(frozen=True)
class Explanation:
    product_id: str
    total_score: int
    summary: str


@dataclass(frozen=True)
class Recommendation:
    product_id: str
    name: str
    monthly_price_cents: int
    score: int
    explanation: Explanation


@dataclass(frozen=True)
class AgentResponse:
    customer_id: str
    recommendations: tuple[Recommendation, ...]
