## Objective

You are given a small Python CLI application that acts as an e-commerce returns and exchanges customer-support agent. The agent combines deterministic business policies with mock backend tool calls.

The repository contains **four independent defects**. Find and fix them while explaining your investigation clearly.

## Interview conditions

- **Timebox: 50 minutes**
- Python 3.11 or newer
- AI coding assistance is not allowed
- Normal documentation and web search are allowed
- `test_scenarios.py` is the source of truth and **must not be edited**
- Keep fixes minimal; avoid unrelated refactors until correctness is restored

## Run the tests

```bash
python -m pytest -q
```

All four scenario tests initially fail. After the intended four fixes, all tests should pass.

## Business rules

### 1. Return-window guardrail

A return request is eligible when it is made within **30 calendar days, inclusive**, of the delivery date.

- Compare **calendar dates in the customer's configured timezone**.
- Day 0 is the local delivery date.
- A request on local day 30 is eligible.
- A request on local day 31 is not eligible.

This is a deterministic guardrail. The agent must not override it conversationally.

### 2. Existing return or exchange

Only orders whose current status is `delivered` may start a new workflow.

After the agent creates a refund or exchange, subsequent reads must observe the updated status. A repeated customer message must not create a duplicate refund, replacement reservation, or return label.

### 3. Refund calculation

Refunds are calculated in whole Japanese yen.

- `home` and `apparel`: no restocking fee
- `electronics`: 10% restocking fee
- Policy configuration stores the fee in **basis points**
- 100 basis points = 1%; therefore 1,000 basis points = 10%
- Round to the nearest whole yen using conventional half-up rounding

### 4. Exchange inventory guardrail

For an exchange request:

- If replacement stock is available, reserve one unit and create an exchange.
- If stock is confirmed to be zero, fall back to a refund.
- If the inventory tool is unavailable, the agent must **not guess** and must **not perform an irreversible action**.
- On inventory-tool failure, return a `handoff` response and create no refund, reservation, label, or status change.

## Recommended verbal loop

For each symptom, communicate in this order:

1. **Symptom** — what observable behavior is wrong?
2. **Hypothesis** — what class of defect could explain it?
3. **Prediction** — what specific value or control flow should be observed if the hypothesis is correct?
4. **Verification** — which test, log, debugger expression, `repr`, or focused inspection will confirm or reject it?
5. **Fix** — what is the smallest safe code change?
6. **Regression check** — which nearby behavior could the change break, and how will you verify it?

## Evaluation dimensions

- Correctness and number of defects fixed
- Hypothesis-driven investigation
- Logical reproduction and isolation
- Minimal, readable changes
- Regression awareness
- Ability to explain customer and business impact

## Suggested starting point

Read in this order:

1. `README.md`
2. `FLOW.md`
3. `test_scenarios.py`
4. The implementation path implicated by each failing scenario

Do not assume the first suspicious line is the complete cause. Reconcile the tests, the documented policy, and the implementation.
