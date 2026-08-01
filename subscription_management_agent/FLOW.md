# Agent flow

```text
User message
  ↓
Load session from SessionStore
  ↓
If session is already in handoff → return handoff response
  ↓
Parse intent / target plan / confirmation / handoff request
  ↓
Verified identity available?
  ├─ no → safe rejection → return
  └─ yes
       ↓
Handoff required?
  ├─ yes → persist handoff → return (terminal boundary)
  └─ no
       ↓
Requested plan available?
  ├─ yes → check eligibility
  │          ├─ ineligible → safe rejection → return
  │          └─ eligible
  │               ↓
  │          Construct complete PendingAction
  │               ↓
  │          Create or replace session.pending_action
  │               ↓
  │          Store last_presented_action_id
  │               ↓
  │          Generate preview for that exact action
  └─ no
       ↓
Confirmation received?
  ├─ no → return preview or safe guidance
  └─ yes
       ↓
Execute session.pending_action through SubscriptionBackend
       ↓
SubscriptionBackend records ToolCall and updates authoritative subscription
       ↓
Read authoritative subscription
       ↓
Generate matching AgentResponse
```

## Ownership boundary

```text
SessionStore:
  Session, verified_customer_id, pending_action,
  last_presented_action_id, handoff

SubscriptionBackend:
  Subscription, plans, eligibility, ToolCall log
```

The subscription-change tool call occurs only after explicit confirmation. Preview generation occurs after the complete pending action is stored. Handoff is a terminal control-flow boundary. The final response is generated only after reading the backend-owned authoritative subscription.
