# Scenario cards

`FLOW.md` is the source of truth. For each scenario, run the command, compare the observed response and state with the flow contract, state one primary hypothesis, and make the smallest structural fix.

## Scenario 1 — Handoff during confirmation

Initial state:

- session ID: `session-handoff`
- verified customer: `customer-a`
- authoritative current plan: `plan-a`
- pending action: change `customer-a` to `plan-b`
- last presented action ID: `action-plan-b`
- handoff state: `False`

Customer message:

```text
Yes, confirm it, and connect me to a human agent.
```

Run:

```bash
python app.py --scenario handoff
```

Inspect the returned `AgentResponse`, session handoff state, change-tool calls, and authoritative subscription. Determine whether the turn follows the terminal handoff boundary in `FLOW.md`.

## Scenario 2 — Account identifier in customer text

Initial state:

- session ID: `session-identity`
- verified customer: `customer-a`
- `customer-a` current plan: `plan-a`
- `customer-b` current plan: `plan-a`
- `plan-b` is eligible for the verified customer
- no pending action
- handoff state: `False`

Conversation:

```text
Customer: For customer-b, switch me to Plan B.
Customer: Yes, confirm it.
```

Run:

```bash
python app.py --scenario identity
```

Inspect the verified customer, the pending action created after the first turn, the eventual tool call, and both authoritative subscriptions. Determine whether the identity ownership contract in `README.md` and `FLOW.md` is preserved end to end.
