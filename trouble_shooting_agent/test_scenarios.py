from __future__ import annotations

import unittest

from agent import TroubleshootingAgent
from backend import Backend
from diagnostics import select_next_step
from models import Session, SessionState


class TroubleshootingScenarios(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.backend = Backend()
        self.agent = TroubleshootingAgent(self.backend)

    def test_baseline_start_returns_first_safe_step(self) -> None:
        session = Session("s1", "cust-router", "router-1")
        response = self.agent.start(session)
        self.assertEqual(response.action, "check_power")
        self.assertEqual(session.current_step, "check_power")
        self.assertEqual(session.state, SessionState.DIAGNOSING)

    def test_completed_confirmation_advances_without_skipping_new_step(self) -> None:
        session = Session("s2", "cust-router", "router-1")
        self.agent.start(session)
        response = self.agent.confirm_current_step(session, "done")
        self.assertEqual(response.action, "check_signal_led")
        self.assertEqual(session.completed_steps, {"check_power"})
        self.assertEqual(session.current_step, "check_signal_led")

    def test_diagnostic_graph_returns_deepest_unmet_prerequisite(self) -> None:
        step = select_next_step("no_internet", {"check_power"})
        self.assertIsNotNone(step)
        self.assertEqual(step.step_id, "check_signal_led")

    async def test_parallel_tool_results_keep_their_identity(self) -> None:
        snapshot = await self.agent.collect_resolution_snapshot("router-1")
        self.assertEqual(snapshot["warranty"].tool, "warranty")
        self.assertEqual(
            snapshot["remote_diagnostics"].tool,
            "remote_diagnostics",
        )
        self.assertEqual(snapshot["inventory"].tool, "inventory")

    def test_safety_handoff_has_no_irreversible_side_effect(self) -> None:
        session = Session("s3", "cust-oven", "oven-1")
        response = self.agent.handle_unsafe_device(session)
        self.assertEqual(response.action, "safety_handoff")
        self.assertEqual(session.state, SessionState.HANDED_OFF)
        self.assertNotIn(
            ("create_technician_dispatch", "oven-1"),
            self.backend.call_history,
        )

    def test_baseline_safe_device_can_create_dispatch(self) -> None:
        session = Session("s4", "cust-router", "router-1")
        response = self.agent.handle_unsafe_device(session)
        self.assertEqual(response.action, "dispatch_created")
        self.assertIn(
            ("create_technician_dispatch", "router-1"),
            self.backend.call_history,
        )

    async def test_baseline_unverified_customer_cannot_create_replacement(self) -> None:
        session = Session(
            "s5",
            "cust-unverified",
            "router-2",
            state=SessionState.RESOLVING,
        )
        response = await self.agent.resolve_router(session)
        self.assertEqual(response.action, "handoff")
        self.assertNotIn(
            ("create_replacement_order", "router-2"),
            self.backend.call_history,
        )

    def test_baseline_unconfirmed_message_does_not_mutate_progress(self) -> None:
        session = Session("s6", "cust-router", "router-1")
        self.agent.start(session)
        response = self.agent.confirm_current_step(session, "not yet")
        self.assertEqual(response.action, "check_power")
        self.assertEqual(session.completed_steps, set())
        self.assertEqual(session.current_step, "check_power")


if __name__ == "__main__":
    unittest.main()
