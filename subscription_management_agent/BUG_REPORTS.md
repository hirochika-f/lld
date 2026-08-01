# Incident — A replacement request activates the earlier plan

Scenario builder: `scenarios.build_plan_replacement_incident`  
Session ID: `session-replace`  
Verified customer: `customer-a`  
Initial authoritative plan: `plan-a`

Conversation:

```text
Customer: I want to switch to Plan A.
Agent: Plan A is ready. Please confirm the change.

Customer: Actually, switch me to Plan B instead.
Agent: Plan B is ready. Please confirm the change.

Customer: Yes, confirm it.
Agent: Your subscription is now Plan A.
```

The customer was most recently shown Plan B, but confirmation activated Plan A. The final response accurately reported the authoritative backend result.

Run the incident:

```bash
python app.py --scenario replacement
```

Before changing the implementation, add a regression test that reproduces the replacement conversation and fails on the violated contract. Then apply a minimal fix and rerun the full baseline suite plus your new test.
