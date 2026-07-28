from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DeviceKind(str, Enum):
    ROUTER = "router"
    MODEM = "modem"
    SMART_OVEN = "smart_oven"


class SessionState(str, Enum):
    IDENTIFYING = "identifying"
    DIAGNOSING = "diagnosing"
    RESOLVING = "resolving"
    HANDED_OFF = "handed_off"
    COMPLETE = "complete"


class ToolStatus(str, Enum):
    OK = "ok"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Customer:
    customer_id: str
    verified: bool


@dataclass(frozen=True)
class Device:
    device_id: str
    customer_id: str
    kind: DeviceKind
    symptom: str


@dataclass(frozen=True)
class DiagnosticStep:
    step_id: str
    prompt: str
    prerequisites: tuple[str, ...] = ()
    terminal: bool = False


@dataclass(frozen=True)
class ToolResult:
    tool: str
    status: ToolStatus
    payload: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class Session:
    session_id: str
    customer_id: str
    device_id: str
    state: SessionState = SessionState.IDENTIFYING
    current_step: str | None = None
    completed_steps: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AgentResponse:
    message: str
    state: SessionState
    action: str | None = None
