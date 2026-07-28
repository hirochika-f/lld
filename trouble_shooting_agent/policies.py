from __future__ import annotations

from models import Customer, Device, DeviceKind, ToolResult, ToolStatus


SAFE_SELF_SERVICE_KINDS = {DeviceKind.ROUTER, DeviceKind.MODEM}


def requires_safety_handoff(device: Device) -> bool:
    return device.kind == DeviceKind.SMART_OVEN and device.symptom in {
        "smoke",
        "sparks",
        "burning_smell",
    }


def may_start_self_service(device: Device) -> bool:
    return device.kind in SAFE_SELF_SERVICE_KINDS


def may_create_replacement(
    customer: Customer,
    warranty: ToolResult,
    remote: ToolResult,
    inventory: ToolResult,
) -> bool:
    if not customer.verified:
        return False
    if warranty.status is not ToolStatus.OK:
        return False
    if remote.status is not ToolStatus.OK:
        return False
    if inventory.status is not ToolStatus.OK:
        return False
    return (
        warranty.payload.get("covered") is True
        and remote.payload.get("verdict") == "hardware_fault"
        and inventory.payload.get("available", 0) > 0
    )
