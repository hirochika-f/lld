# Processing Flow

```text
app.py
  -> TroubleshootingAgent.start(session)
       -> Backend.get_device()
       -> policies.may_start_self_service()
       -> loads the first step from diagnostics.STEPS
       -> updates Session.state/current_step

user confirmation
  -> TroubleshootingAgent.confirm_current_step()
       -> validates active session state
       -> advances through the explicit state transition table
       -> updates Session.completed_steps/current_step/state

diagnostic dependency inspection
  -> diagnostics.select_next_step()
       -> diagnostics.first_unmet_requirement() [recursive DFS]
       -> validates prerequisite order and detects cycles

resolution review
  -> TroubleshootingAgent.collect_resolution_snapshot()
       -> check_warranty() ------------------+
       -> run_remote_diagnostics() ----------+--> combine authoritative results
       -> check_inventory() -----------------+
  -> policies.may_create_replacement()
  -> Backend.create_replacement_order() [irreversible]

service visit or unsafe appliance
  -> TroubleshootingAgent.handle_unsafe_device()
       -> policies.requires_safety_handoff()
       -> safety handoff OR dispatch logic
       -> Backend.create_technician_dispatch() [irreversible]
```

## Module responsibilities

- `app.py`: thin CLI only.
- `agent.py`: conversation orchestration, explicit state transitions, policy calls, tool coordination, and resolution decisions.
- `backend.py`: authoritative mock data, asynchronous tools, and irreversible side effects.
- `policies.py`: deterministic safety, identity, warranty, diagnostics, and inventory guardrails.
- `diagnostics.py`: diagnostic dependency graph traversal, prerequisite validation, and next-step selection.
- `models.py`: enums and dataclasses shared by all modules.
- `test_scenarios.py`: executable specification; do not edit.

## State mutation points

- Diagnosis start: `TroubleshootingAgent.start`.
- Step completion and next-step transition: `TroubleshootingAgent.confirm_current_step`.
- Resolution completion or handoff: `resolve_router` and `handle_unsafe_device`.

## Side-effect boundary

Only backend methods whose names start with `create_` are irreversible in this exercise. A correct response message does not undo an earlier backend call.

## Guardrail boundary

Policy checks define whether an action is allowed. Agent orchestration must evaluate mandatory guardrails before entering code paths that can create irreversible effects. Goal-oriented logic may choose among allowed actions only after those checks pass.
