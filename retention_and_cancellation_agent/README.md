# Subscription Retention Agent

This is a **synthetic practice problem**.

It is designed to reproduce the format described in the provided research:
a small multi-file CLI application, scenario-driven debugging, several independent
bugs, and an expectation that you explain hypotheses and customer impact while working.

## Timebox

- Recommended: **50 minutes**
- Language: Python 3.10+
- External packages: none
- AI assistance: do not use it during the mock round
- You may use normal language documentation or web search, as in the stated interview rules

## Your task

The application simulates a customer-support agent for a subscription service.
Several customer scenarios are producing incorrect behavior.

1. Read this README and `FLOW.md`.
2. Before editing code, explain aloud:
   - how you will reproduce the failures;
   - which boundaries you will inspect first;
   - which edge cases matter.
3. Run the scenario suite:

```bash
python test_scenarios.py
```

4. Fix the production code. **Do not modify the tests.**
5. After each fix, rerun the relevant scenario and then the full suite.
6. Be prepared to explain:
   - the root cause;
   - why your fix is minimal and safe;
   - the customer or business impact;
   - what regression test protects the behavior.

## Business rules

### Customer lookup

A customer can be identified by customer ID or email address.
Email lookup is case-insensitive and ignores leading/trailing whitespace.

### Retention offers

A 20% retention offer may be shown only when all of the following are true:

- the subscription is active;
- tenure is at least 12 months;
- the customer has no failed payments;
- no retention offer has been shown in the last 90 days.

An ineligible customer asking to cancel must proceed directly to cancellation confirmation.

### Cancellation

Cancellation is a sensitive action.
It must happen only after an explicit confirmation in the **same conversation**.
Separate customer conversations must never share confirmation state.

### Backend reliability

The backend may fail transiently.
Cancellation should make at most **two total attempts** and should succeed if the first
attempt fails transiently but the second succeeds. Non-transient errors must not be retried.

## Running the CLI manually

```bash
python app.py
```

Example identifiers:

- `cust_001`
- `alice@example.com`
- `cust_002`
- `cust_003`
- `cust_004`

Type `quit` to exit.

## Suggested verbal structure

Use this loop throughout the exercise:

1. Observed symptom
2. Current hypothesis
3. Evidence you expect if the hypothesis is true
4. Smallest experiment
5. Result
6. Fix
7. Regression check

Avoid narrating every line of code. Narrate decisions and evidence.
