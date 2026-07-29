# Quickstart

## 1. Requirements

- Python 3.11+
- A terminal environment with Python available
- The repository root as the working directory

## 2. Install and initialize

Run from the repository root:

```bash
cd /workspaces/specomega
python -m unittest discover -s tests -v
```

This confirms the current implementation is runnable.

## 3. Run the first example

### 3.1 Validate agent tool-call compliance

The repository includes a minimal runnable Agent example:

```bash
python examples/agent_runtime/run_example.py
```

This reads:

- [examples/agent_runtime/spec.md](../examples/agent_runtime/spec.md)
- [examples/agent_runtime/agent_trace.json](../examples/agent_runtime/agent_trace.json)

It validates whether a payment scenario follows the expected tool-call sequence:

- run `risk_check`
- then run `pay`

If the order is correct, the output will show `passed: true`.

## 4. Run specification verification

### 4.1 Verify spec markers in the whole project

```bash
python -m specomega verify --path .
```

### 4.2 Verify a single spec file

```bash
python -m specomega verify --path .specify/specs/user_management.spec
```

## 5. Analyze spec conflicts

```bash
python -m specomega analyze --path .specify/specs/user_management.spec openspec/specs/user_management.md
```

## 6. Plan a multi-agent workflow

```bash
python -m specomega plan --path .specomega/agents.md
```

## 7. Risk analysis and reporting

```bash
python -m specomega risk --spec examples/agent_runtime/spec.md --trace examples/agent_runtime/agent_trace.json --output-dir .specomega/reports --format markdown
```

This produces Markdown, JSON, SARIF, and HTML risk reports.

To fail CI when findings are present, use:

```bash
python -m specomega risk --spec examples/agent_runtime/spec.md --trace examples/agent_runtime/agent_trace.json --output-dir .specomega/reports --format sarif --strict
```
