# Application flow

```text
CLI / scenario
    |
    v
SupportAgent.respond(identifier, message, session)
    |
    +--> Backend.get_customer(identifier)
    |
    +--> Existing conversation state?
    |       |
    |       +--> retention_offer
    |       +--> cancel_confirmation
    |
    +--> classify_intent(message)
            |
            +--> subscription_status
            +--> cancel_subscription
            |       |
            |       +--> retention_eligible(customer)
            |               |
            |               +--> offer 20%
            |               +--> ask for cancellation confirmation
            |
            +--> unknown

Confirmed cancellation
    |
    v
SupportAgent._run_with_retry(...)
    |
    v
Backend.cancel_subscription(customer_id)
```

## Responsibility boundaries

- `models.py`: data structures used across the application
- `backend.py`: mock customer store and external actions
- `policies.py`: deterministic business policy
- `agent.py`: orchestration and conversation state transitions
- `app.py`: interactive CLI only
- `test_scenarios.py`: executable scenarios; do not edit
