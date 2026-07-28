from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from models import Customer, Device, DeviceKind, ToolResult, ToolStatus


@dataclass
class Backend:
    customers: dict[str, Customer] = field(default_factory=dict)
    devices: dict[str, Device] = field(default_factory=dict)
    call_history: list[tuple[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.customers:
            self.customers = {
                "cust-router": Customer("cust-router", verified=True),
                "cust-unverified": Customer("cust-unverified", verified=False),
                "cust-oven": Customer("cust-oven", verified=True),
            }
        if not self.devices:
            self.devices = {
                "router-1": Device(
                    "router-1", "cust-router", DeviceKind.ROUTER, "no_internet"
                ),
                "router-2": Device(
                    "router-2", "cust-unverified", DeviceKind.ROUTER, "no_internet"
                ),
                "oven-1": Device(
                    "oven-1", "cust-oven", DeviceKind.SMART_OVEN, "smoke"
                ),
            }

    def get_customer(self, customer_id: str) -> Customer:
        return self.customers[customer_id]

    def get_device(self, device_id: str) -> Device:
        return self.devices[device_id]

    async def check_warranty(self, device_id: str) -> ToolResult:
        await asyncio.sleep(0.03)
        self.call_history.append(("check_warranty", device_id))
        return ToolResult(
            tool="warranty",
            status=ToolStatus.OK,
            payload={"covered": device_id in {"router-1", "oven-1"}},
        )

    async def run_remote_diagnostics(self, device_id: str) -> ToolResult:
        await asyncio.sleep(0.01)
        self.call_history.append(("run_remote_diagnostics", device_id))
        if device_id == "router-1":
            return ToolResult(
                tool="remote_diagnostics",
                status=ToolStatus.OK,
                payload={"verdict": "hardware_fault"},
            )
        return ToolResult(
            tool="remote_diagnostics",
            status=ToolStatus.UNKNOWN,
            payload={"verdict": "inconclusive"},
        )

    async def check_inventory(self, part_number: str) -> ToolResult:
        await asyncio.sleep(0.02)
        self.call_history.append(("check_inventory", part_number))
        return ToolResult(
            tool="inventory",
            status=ToolStatus.OK,
            payload={"part_number": part_number, "available": 2},
        )

    def create_replacement_order(self, device_id: str) -> str:
        self.call_history.append(("create_replacement_order", device_id))
        return f"replacement:{device_id}"

    def create_technician_dispatch(self, device_id: str) -> str:
        self.call_history.append(("create_technician_dispatch", device_id))
        return f"dispatch:{device_id}"
