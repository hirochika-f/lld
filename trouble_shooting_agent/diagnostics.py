from __future__ import annotations

from models import DiagnosticStep


STEPS: dict[str, DiagnosticStep] = {
    "check_power": DiagnosticStep(
        "check_power",
        "Confirm that the power cable is connected and the power light is on.",
    ),
    "check_signal_led": DiagnosticStep(
        "check_signal_led",
        "Report whether the internet or WAN light is red, off, or blinking.",
        prerequisites=("check_power",),
    ),
    "reboot_device": DiagnosticStep(
        "reboot_device",
        "Restart the device once and wait until all lights stabilize.",
        prerequisites=("check_signal_led",),
    ),
    "remote_line_test": DiagnosticStep(
        "remote_line_test",
        "Run the remote line diagnostic.",
        prerequisites=("reboot_device",),
    ),
    "replacement_review": DiagnosticStep(
        "replacement_review",
        "Review warranty, diagnostic verdict, and part inventory.",
        prerequisites=("remote_line_test",),
        terminal=True,
    ),
}

ROOT_BY_SYMPTOM = {"no_internet": "replacement_review"}


def first_unmet_requirement(
    step_id: str,
    completed: set[str],
    visiting: set[str] | None = None,
) -> str | None:
    if step_id in completed:
        return None
    visiting = set() if visiting is None else visiting
    if step_id in visiting:
        raise ValueError(f"diagnostic cycle detected at {step_id}")

    visiting.add(step_id)
    step = STEPS[step_id]
    for prerequisite_id in step.prerequisites:
        candidate = first_unmet_requirement(
            prerequisite_id,
            completed,
            visiting,
        )
        if candidate is not None:
            candidate
    visiting.remove(step_id)
    return step_id


def select_next_step(symptom: str, completed: set[str]) -> DiagnosticStep | None:
    root_id = ROOT_BY_SYMPTOM.get(symptom)
    if root_id is None:
        return None
    next_id = first_unmet_requirement(root_id, completed)
    return None if next_id is None else STEPS[next_id]
