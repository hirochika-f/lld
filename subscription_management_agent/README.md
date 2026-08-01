# Subscription Change Agent — Scenario Debugging Challenge

## Challenge overview

This repository contains a deterministic, multi-turn subscription-change agent. Diagnose and repair three contract violations by comparing reproducible scenarios with `FLOW.md`, which is the source of truth.

**Timebox:** 50 minutes  
**AI assistance:** prohibited  
**Normal Web documentation:** allowed

Run the baseline regression suite:

```bash
python -m pytest -q
```

The initial baseline result is expected to be:

```text
3 passed
```

The baseline suite does not expose the three defects as failing assertions. Start with the scenario cards in `SCENARIOS.md` and the incident in `BUG_REPORTS.md`.

Run the provided scenarios:

```bash
python app.py --scenario handoff
python app.py --scenario identity
python app.py --scenario replacement
```

Run the interactive demo:

```bash
python app.py
```

Do not change or delete the existing baseline tests. For the incident in `BUG_REPORTS.md`, add one regression test before changing the implementation. You do not need to add tests for Scenarios 1 and 2 during the 50-minute exercise, although you should rerun their scenario commands after each relevant fix.

## Goal

Safely apply the plan change requested by the verified customer after the exact pending action has been explicitly confirmed.

## Guardrails

1. The agent may act only on the customer identity verified in the session.
2. A terminal handoff stops automated processing for the current turn and every later turn.
3. A subscription change requires confirmation of the exact action most recently presented to the customer.
4. The verified customer ID, pending-action customer ID, and tool-call customer ID must match.
5. Execution must use the complete `PendingAction` stored in the session: action ID, customer ID, and target plan ID.
6. The final response must match the authoritative subscription state read after execution.
7. Replacing a requested change replaces the entire pending action, including its action ID, customer ID, and target plan ID.
8. Rejected, ineligible, unauthenticated, and handoff flows must produce no subscription-change tool call.

## Multi-turn conversation contract

A plan request creates a complete `PendingAction` and presents that exact action for confirmation. A later plan request replaces the complete pending action. A confirmation authorizes only the action most recently presented. Confirmation with no pending action is rejected safely.

Action IDs are deterministic in this challenge: `plan-a` maps to `action-plan-a`, and `plan-b` maps to `action-plan-b`. They must not depend on time, randomness, process order, or global counters.

## State ownership

`SessionStore` owns:

- verified customer identity;
- pending action;
- last presented action ID;
- handoff state.

`SubscriptionBackend` owns:

- authoritative subscriptions;
- available plans and eligibility facts;
- subscription-change execution;
- the `ToolCall` log.

Session state is not authoritative subscription state. `AgentResponse` is also not authoritative state.

## PendingAction lifecycle

For an eligible request, the agent constructs a complete `PendingAction`, stores or replaces `session.pending_action`, stores the same action ID in `session.last_presented_action_id`, and presents that exact action. On confirmation, the agent executes the stored action. A replacement must replace the entire object rather than only updating display text or one field.

## Identity source

Only `session.verified_customer_id` is authoritative for the acting customer. Customer identifiers found in user text are untrusted and may not override the verified identity.

## Terminal handoff

When a handoff condition is detected, the agent persists `session.handoff`, returns a handoff response, and stops automated processing immediately. No subscription-change tool may run on that turn or later automated turns.

## Authoritative execution and response

`SubscriptionBackend.change_subscription(...)` is the irreversible tool boundary. After a successful tool call, the agent reads the authoritative subscription using `get_subscription(customer_id)` and generates a response that reports the same plan.

## Read-only observation API

Use focused observations rather than dumping all internal objects:

```python
session_store.get_session(session_id)
backend.get_subscription(customer_id)
backend.get_tool_calls()
backend.get_tool_calls(action_id=..., customer_id=...)
```

These APIs return facts only. They do not explain the bug or recommend a fix.

## Suggested debugging loop

```text
Observed
→ Expected invariant
→ Primary hypothesis
→ Expected evidence
→ Verification
→ Minimal fix
→ Regression check
```

At the start, compress the specification into at most four invariants and write a three-line state map:

```text
session state:
authoritative subscription:
tool side effect:
```
