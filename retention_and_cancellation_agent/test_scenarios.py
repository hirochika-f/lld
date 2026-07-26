import unittest

from agent import SupportAgent
from backend import Backend, TransientBackendError
from models import Session


class SubscriptionAgentScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.backend = Backend()
        self.agent = SupportAgent(self.backend)

    def test_baseline_status_lookup_by_customer_id(self) -> None:
        response = self.agent.respond(
            "cust_001",
            "What is my plan status?",
            Session(),
        )
        self.assertEqual("show_status", response.action)
        self.assertIn("pro", response.message)
        self.assertIn("active", response.message)

    def test_baseline_eligible_customer_receives_offer(self) -> None:
        response = self.agent.respond(
            "cust_001",
            "I want to cancel my subscription",
            Session(),
        )
        self.assertEqual("offer_retention", response.action)

    def test_scenario_1_email_lookup_normalizes_user_input(self) -> None:
        response = self.agent.respond(
            "  Alice@Example.COM  ",
            "What plan am I on?",
            Session(),
        )
        self.assertEqual(
            "show_status",
            response.action,
            msg=f"Unexpected trace: {response.trace}",
        )

    def test_scenario_2_failed_payments_block_retention_offer(self) -> None:
        response = self.agent.respond(
            "cust_003",
            "Please cancel my subscription",
            Session(),
        )
        self.assertEqual(
            "request_cancellation_confirmation",
            response.action,
            msg=f"Unexpected trace: {response.trace}",
        )

    def test_scenario_3_transient_cancel_failure_is_retried(self) -> None:
        session = Session()
        first = self.agent.respond(
            "cust_004",
            "Cancel my subscription",
            session,
        )
        self.assertEqual("request_cancellation_confirmation", first.action)

        try:
            second = self.agent.respond("cust_004", "yes", session)
        except TransientBackendError as exc:
            self.fail(f"Transient failure escaped without retry: {exc}")

        self.assertEqual(
            "subscription_canceled",
            second.action,
            msg=f"Unexpected trace: {second.trace}",
        )

    def test_scenario_4_independent_conversations_do_not_share_state(self) -> None:
        first = self.agent.respond(
            "cust_002",
            "Cancel my subscription",
        )
        self.assertEqual("request_cancellation_confirmation", first.action)

        second = self.agent.respond(
            "cust_001",
            "yes",
        )
        self.assertEqual(
            "unknown_intent",
            second.action,
            msg=(
                "A fresh conversation treated 'yes' as authorization. "
                f"Unexpected trace: {second.trace}"
            ),
        )

        status = self.agent.respond(
            "cust_001",
            "What is my plan status?",
            Session(),
        )
        self.assertIn("active", status.message)


if __name__ == "__main__":
    unittest.main(verbosity=2)
