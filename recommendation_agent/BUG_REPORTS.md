# Production Incident Reports

These incidents do not have tests in the initial suite. Reproduce each incident with a failing regression test before changing implementation code.

## Incident A — recently recommended product appeared again

Customer support reported that `cust-imported-history` received `device-nova-pro` again even though that device had been recommended five days earlier. The customer has imported recommendation history from a legacy service.

Reproduction command:

```bash
python app.py recommend cust-imported-history --limit 2
```

Observed output includes:

```text
product_id: device-nova-pro
```

The backend data contains a recent recommendation event for that customer and product. Existing baseline tests still pass.

## Incident B — recommendation and explanation disagree

Operations reported that `cust-explanation-order` received `plan-ultra` as the first recommendation, but the attached explanation identifies a different product and describes the other product's score.

Reproduction command:

```bash
python app.py recommend cust-explanation-order --limit 2
```

The recommendation IDs themselves look plausible. The inconsistency appears only for some catalog response orders; no exception is raised.
