# Processing Flow

## Call graph

```text
app.py
  └─ RecommendationAgent.recommend()                 agent.py
       ├─ backend.get_customer()                     backend.py
       ├─ backend.get_catalog()                      backend.py
       ├─ backend.get_inventory()                    backend.py
       ├─ backend.get_recommendation_history()       backend.py
       ├─ is_hard_eligible()                         policies.py
       ├─ is_in_cooldown()                           history.py
       ├─ deduplicate_products()                     ranking.py
       ├─ score_products()                           ranking.py
       ├─ sort_scored_products()                     ranking.py
       ├─ apply_diversity()                          ranking.py
       ├─ build_explanation()                        agent.py
       └─ backend.save_recommendation_event()        backend.py
```

## Intended data flow

```text
Customer + Catalog + Inventory + Recommendation History
  → hard-constraint filter
  → cooldown filter
  → product_id deduplication
  → score calculation
  → deterministic multi-key sort
  → stable diversity hook
  → top-k selection
  → product-bound explanation generation
  → recommendation-history writes
```

## Module responsibilities

- `app.py`: thin CLI and JSON output.
- `agent.py`: orchestration and final response assembly.
- `backend.py`: deterministic in-memory representations of external systems.
- `policies.py`: non-negotiable eligibility guardrails only.
- `history.py`: cooldown evaluation over recommendation events.
- `ranking.py`: deduplication, scoring, sorting, and diversity.
- `models.py`: data contracts shared across modules.
- `test_scenarios.py`: baseline behavior plus two initially exposed failures.

## Hard constraints versus soft preferences

`policies.py` decides whether a product may be recommended. `ranking.py` decides how eligible products are ordered. Ranking must never restore a product rejected by policy.

## State and side effects

Explanations are generated only after final selection. Recommendation events are saved only for returned product IDs, after response assembly.
