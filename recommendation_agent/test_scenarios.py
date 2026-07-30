import unittest

from agent import RecommendationAgent
from backend import CURRENT_DAY, build_backend


class RecommendationScenarioTests(unittest.TestCase):
    def test_returns_three_eligible_recommendations_when_enough_products_exist(self) -> None:
        """Eligible alternatives should fill all available recommendation slots."""
        agent = RecommendationAgent(build_backend())

        response = agent.recommend("cust-fill-slots", limit=3)

        self.assertEqual(
            [rec.product_id for rec in response.recommendations],
            ["fill-a", "fill-b", "fill-c"],
        )

    def test_equal_score_products_follow_the_documented_business_order(self) -> None:
        """Equal-score recommendations must use price, inventory, then product ID."""
        agent = RecommendationAgent(build_backend())

        response = agent.recommend("cust-tie", limit=4)

        self.assertEqual(
            [rec.product_id for rec in response.recommendations],
            [
                "tie-alpha",
                "tie-zeta",
                "tie-cheap-low-stock",
                "tie-expensive",
            ],
        )

    def test_normal_recommendation_succeeds(self) -> None:
        backend = build_backend()
        response = RecommendationAgent(backend).recommend("cust-baseline", limit=2)
        self.assertEqual(
            [rec.product_id for rec in response.recommendations],
            ["plan-max", "plan-flex"],
        )

    def test_hard_constraint_products_are_not_returned(self) -> None:
        backend = build_backend()
        response = RecommendationAgent(backend).recommend("cust-constraints", limit=2)
        ids = [rec.product_id for rec in response.recommendations]
        self.assertEqual(ids, ["constraint-valid"])
        self.assertNotIn("constraint-over-budget", ids)

    def test_fewer_candidates_than_limit_does_not_raise(self) -> None:
        response = RecommendationAgent(build_backend()).recommend("cust-single", limit=3)
        self.assertEqual([rec.product_id for rec in response.recommendations], ["single-plan"])

    def test_empty_catalog_returns_empty_response(self) -> None:
        response = RecommendationAgent(build_backend()).recommend("cust-empty", limit=3)
        self.assertEqual(response.recommendations, ())

    def test_product_ids_are_unique(self) -> None:
        response = RecommendationAgent(build_backend()).recommend("cust-duplicates", limit=3)
        ids = [rec.product_id for rec in response.recommendations]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {"duplicate-plan", "duplicate-other"})

    def test_history_is_saved_for_returned_product_ids(self) -> None:
        backend = build_backend()
        response = RecommendationAgent(backend).recommend("cust-history-write", limit=2)
        returned_ids = [rec.product_id for rec in response.recommendations]
        saved_ids = [
            event.product_id
            for event in backend.history_by_customer["cust-history-write"]
            if event.day == CURRENT_DAY
        ]
        self.assertEqual(saved_ids, returned_ids)


if __name__ == "__main__":
    unittest.main()
