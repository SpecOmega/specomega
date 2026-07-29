# AI Risk Analysis

SpecOmega includes a lightweight risk-analysis module that inspects spec content and execution traces to identify potential issues such as missing pre-checks, insecure state transitions, and risky write operations.

## Output

The analyzer emits:

- risk level
- findings
- recommendations
- structured LLM summary data

## Example

```bash
python -m specomega risk --spec examples/agent_runtime/spec.md --trace examples/agent_runtime/agent_trace.json --output-dir .specomega/reports
```
