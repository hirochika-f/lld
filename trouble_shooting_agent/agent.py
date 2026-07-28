from __future__ import annotations

import asyncio

from backend import Backend
from diagnostics import STEPS
from models import AgentResponse, Session, SessionState, ToolResult
from policies import may_create_replacement, may_start_self_service, requires_safety_handoff


class TroubleshootingAgent:
    def __init__(self, backend: Backend) -> None:
        self.backend = backend

    def start(self, session: Session) -> AgentResponse:
        device = self.backend.get_device(session.device_id)
        if not may_start_self_service(device):
            return AgentResponse(
                message="This device requires assisted support.",
                state=session.state,
                action="handoff",
            )

        if device.symptom != "no_internet":
            return AgentResponse("No diagnostic flow is available.", session.state)
        first_step = STEPS["check_power"]
        session.state = SessionState.DIAGNOSING
        session.current_step = first_step.step_id
        return AgentResponse(first_step.prompt, session.state, action=first_step.step_id)

    def confirm_current_step(self, session: Session, user_message: str) -> AgentResponse:
        if session.state is not SessionState.DIAGNOSING or session.current_step is None:
            return AgentResponse("There is no active diagnostic step.", session.state)
        if user_message.strip().casefold() not in {"done", "yes", "completed"}:
            return AgentResponse(
                f"Please complete: {STEPS[session.current_step].prompt}",
                session.state,
                action=session.current_step,
            )

        next_by_step = {
            "check_power": "check_signal_led",
            "check_signal_led": "reboot_device",
            "reboot_device": "remote_line_test",
            "remote_line_test": "replacement_review",
            "replacement_review": None,
        }
        next_step_id = next_by_step[session.current_step]
        if next_step_id is None:
            session.completed_steps.add(session.current_step)
            session.current_step = None
            session.state = SessionState.RESOLVING
            return AgentResponse(
                "Diagnostics complete. Reviewing resolution options.",
                session.state,
                action="review_resolution",
            )

        session.current_step = next_step_id
        session.completed_steps.add(session.current_step)
        next_step = STEPS[next_step_id]
        return AgentResponse(next_step.prompt, session.state, action=next_step.step_id)

    async def collect_resolution_snapshot(self, device_id: str) -> dict[str, ToolResult]:
        tasks = [
            asyncio.create_task(self.backend.check_warranty(device_id)),
            asyncio.create_task(self.backend.run_remote_diagnostics(device_id)),
            asyncio.create_task(self.backend.check_inventory("router-mainboard")),
        ]
        completed_results: list[ToolResult] = []
        for task in asyncio.as_completed(tasks):
            completed_results.append(await task)
        return dict(
            zip(
                ("warranty", "remote_diagnostics", "inventory"),
                completed_results,
                strict=True,
            )
        )

    async def resolve_router(self, session: Session) -> AgentResponse:
        customer = self.backend.get_customer(session.customer_id)
        snapshot = await self.collect_resolution_snapshot(session.device_id)
        if may_create_replacement(
            customer,
            snapshot["warranty"],
            snapshot["remote_diagnostics"],
            snapshot["inventory"],
        ):
            order_id = self.backend.create_replacement_order(session.device_id)
            session.state = SessionState.COMPLETE
            return AgentResponse(
                f"Replacement created: {order_id}",
                session.state,
                action="replacement_created",
            )
        return AgentResponse(
            "Replacement could not be approved. A human specialist will review it.",
            SessionState.HANDED_OFF,
            action="handoff",
        )

    def handle_unsafe_device(self, session: Session) -> AgentResponse:
        device = self.backend.get_device(session.device_id)
        dispatch_id = self.backend.create_technician_dispatch(device.device_id)
        if requires_safety_handoff(device):
            session.state = SessionState.HANDED_OFF
            return AgentResponse(
                "Stop using the device, disconnect power if safe, and contact emergency support.",
                session.state,
                action="safety_handoff",
            )
        session.state = SessionState.COMPLETE
        return AgentResponse(
            f"Technician visit created: {dispatch_id}",
            session.state,
            action="dispatch_created",
        )
