# Processing Flow and Responsibility Boundaries

## End-to-end flow

```text
Customer input
    |
    v
app.py
  - Parses CLI input
  - Creates ReturnRequest
  - Prints AgentResponse
    |
    v
agent.py  (orchestrator)
  - Loads customer and order
  - Checks current workflow state
  - Calls deterministic policy functions
  - Calls inventory/refund/label/status backend tools
  - Chooses refund, exchange, denial, or safe handoff
    |                    |
    |                    +-------------------+
    v                                        v
policies.py                             backend.py
  - Return-window rule                   - Customer/order reads
  - Refund amount calculation            - Order-state writes
                                         - Inventory lookup/reservation
                                         - Refund and label side effects
    ^                                        ^
    |                                        |
    +---------------- models.py -------------+
                       - Customer
                       - OrderItem
                       - ReturnRequest
                       - Session
                       - AgentResponse

pytest
    |
    v
test_scenarios.py
  - Executable acceptance criteria
  - Correct and not editable
```

## File responsibilities

### `models.py`

Defines the data contract shared by all modules. It should contain structure, not business decisions or backend side effects.

### `backend.py`

Mocks external commerce systems. It owns persisted customer/order state, replacement inventory, refunds, and return labels. Treat reads and writes as remote API operations even though the implementation is in memory.

### `policies.py`

Contains deterministic business rules. These functions should be pure: the same inputs should produce the same outputs without mutating backend state.

### `agent.py`

Coordinates the workflow. It decides which policy and tool to call, handles tool failure safely, and controls irreversible side effects.

### `app.py`

A thin CLI adapter. It should not duplicate business rules.

### `test_scenarios.py`

Executable business acceptance criteria. This file is correct and must not be modified.
