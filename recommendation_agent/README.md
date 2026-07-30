# Personalized Product Recommendation Agent — Debugging Exercise

## Overview

You are debugging a small Python CLI used by a telecommunications company to recommend plans and devices. The agent must maximize customer suitability while enforcing non-negotiable eligibility rules.

**Timebox: 50 minutes.**

AI coding assistants are not allowed. Normal web search and language documentation are allowed.

The repository intentionally contains four behavioral defects:

- Two are exposed by existing failing tests.
- Two are described only in `BUG_REPORTS.md` and do not initially have regression tests.

For each incident report, first add a regression test that fails on the current implementation, then apply the smallest correct fix.

## Run the CLI

```bash
python app.py recommend cust-baseline --limit 2
```

## Run the tests

```bash
python -m unittest -v
```

The initial suite is expected to contain exactly two failing tests. Do not delete or weaken existing tests, and do not change their expected behavior.

You may and should add regression tests for the incidents in `BUG_REPORTS.md`.

## Recommendation contract

### Goal

Return up to `limit` of the most suitable eligible products. If at least `limit` eligible, non-cooled-down, unique products exist, return exactly `limit` recommendations.

### Hard constraints

A product must never be recommended when any of the following is true:

- The customer's region is not supported.
- The customer's device lacks the product's required capability.
- The customer is younger than the product's minimum age.
- The monthly price exceeds the customer's explicit budget.
- The customer already has that product as a current subscription.
- Inventory is missing.
- Available inventory is zero or negative.

Hard constraints are guardrails. A high score can never override them.

### Soft preferences and score

Soft preferences affect ranking only. They never make an otherwise eligible product forbidden.

For every eligible product, calculate:

- `usage_fit`: 40 points when included data is at least the customer's monthly usage; otherwise 15.
- `budget_fit`: 20 points when price is at most 70% of budget; otherwise 10 points when it is within budget.
- `brand_fit`: 10 points when the product brand matches a stated preferred brand; otherwise 0.
- `campaign`: the product's campaign points.

`total_score` is the sum of those fields.

### Correct pipeline order

```text
fetch customer, catalog, inventory, and history
→ apply hard constraints
→ apply cooldown
→ deduplicate by product_id
→ calculate score
→ deterministic sort
→ apply the stable diversity hook
→ select top-k
→ generate an explanation from that selected product's score breakdown
→ save recommendation history for the selected product IDs
```

Filtering, cooldown, and deduplication must occur before top-k selection. Ineligible or suppressed products must not consume recommendation slots.

### Deterministic ranking and tie-break

Sort by the following keys, in this exact order:

1. `total_score`, descending
2. `monthly_price_cents`, ascending
3. `available_units`, descending
4. `product_id`, ascending lexicographically

Catalog input order must not affect the final order.

### Top-k

`limit` is the maximum number of returned recommendations, not the number of raw candidates examined. Return fewer only when fewer eligible, non-cooled-down, unique products exist.

### Cooldown

A product is suppressed when the customer was recommended the same `product_id` fewer than 30 days ago. Recommendation history may arrive in any order. The result must not depend on history input order.

### Deduplication

Duplicate catalog records with the same `product_id` represent the same product. Only one recommendation for that product may be returned.

### Explanation contract

Each recommendation explanation must be generated from the `ScoreBreakdown` belonging to that exact selected product.

For every recommendation:

- `recommendation.product_id == recommendation.explanation.product_id`
- `recommendation.score == recommendation.explanation.total_score`

A correct product with another product's explanation is incorrect.

### Missing inventory

Missing inventory is treated as unavailable and is a hard-constraint failure. Do not borrow or infer inventory from another product.

### Determinism and input order

The same logical inputs must produce the same recommendation IDs, order, scores, and explanations regardless of catalog or history ordering.

## Incident investigation workflow

For an incident report:

1. Separate observed facts from assumptions.
2. Define the expected invariant.
3. Create the smallest reproducible fixture.
4. Add a regression test that fails before the fix.
5. Form a root-cause hypothesis.
6. Predict the observable values.
7. Inspect only the necessary state.
8. Apply the smallest fix.
9. Run the new test and the full suite.
10. Check nearby cases and input-order independence.

Keep each spoken investigation update concise:

```text
symptom → hypothesis → prediction → verification → fix → regression check
```
