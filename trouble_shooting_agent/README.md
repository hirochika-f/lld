# Troubleshooting Agent Debugging Round

## Overview

You are debugging a small customer-support agent for routers, modems, and smart appliances. The agent guides customers through safe diagnostic steps, calls remote tools, and may create a replacement or technician dispatch.

Timebox: **50 minutes**.

AI coding assistance is not allowed. Normal web search and Python documentation are allowed.

Do not modify `test_scenarios.py`.

## Run

```bash
python app.py
```

## Test

```bash
python -m unittest -v test_scenarios.py
```

The initial repository contains four intended defects. Some baseline tests already pass.

## Business rules

1. Self-service troubleshooting is allowed only for routers and modems.
2. A customer may confirm only the currently active diagnostic step.
3. A newly selected step must not be recorded as completed until the customer confirms it.
4. Diagnostic prerequisites must be completed in dependency order.
5. A diagnostic dependency cycle is invalid and must fail explicitly.
6. Replacement requires all of the following authoritative results:
   - verified customer;
   - warranty tool returned `OK` and `covered=True`;
   - remote diagnostics returned `OK` and `verdict="hardware_fault"`;
   - inventory tool returned `OK` and `available > 0`.
7. `FAILED` and `UNKNOWN` tool results are not normal negative values. They must not be reinterpreted as another tool's result.

## Safety guardrails

A smart appliance reporting smoke, sparks, or a burning smell requires immediate safety handoff. The agent must instruct the customer to stop using the device and disconnect power only if safe.

Before returning that handoff, the agent must not:

- provide self-repair instructions;
- create a replacement;
- create a technician dispatch;
- perform any other irreversible external action.

Safety guardrails take precedence over goal-oriented resolution logic.

## External tool contracts

- `check_warranty(device_id)` returns a `ToolResult` whose `tool` is `"warranty"`.
- `run_remote_diagnostics(device_id)` returns a `ToolResult` whose `tool` is `"remote_diagnostics"`.
- `check_inventory(part_number)` returns a `ToolResult` whose `tool` is `"inventory"`.
- Tool latency is independent. Completion order is not a stable identifier.
- `create_replacement_order` and `create_technician_dispatch` are irreversible side effects.
- `Backend.call_history` is authoritative for whether a side effect occurred.

## Session state

- `IDENTIFYING`: customer and device are known, but diagnosis has not started.
- `DIAGNOSING`: exactly one current diagnostic step may be active.
- `RESOLVING`: all required diagnostic steps are complete.
- `HANDED_OFF`: the agent has stopped autonomous action.
- `COMPLETE`: an approved resolution was created.

Conversation text is not authoritative. `Session.current_step`, `Session.completed_steps`, tool results, and backend call history are authoritative.

## Recommended loop

For each failure, use this sequence:

**Symptom → Hypothesis → Prediction → Verification → Minimal fix → Regression check**

Before printing values, state what you expect to observe if the hypothesis is correct and what you will investigate next if it is not.
