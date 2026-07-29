# Agent Runtime Example

The example under [examples/agent_runtime](../examples/agent_runtime) demonstrates how SpecOmega validates a payment-flow agent trace.

## What it checks

- The tool-call sequence includes `risk_check` before `pay`
- The resulting verification report is emitted as structured JSON
- The risk analysis layer produces a recommendation summary

## Run it

```bash
python examples/agent_runtime/run_example.py
```
