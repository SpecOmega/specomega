# User Guide

## 1. Verify a spec fragment

Use the verification command to run the available checks against a file or directory:

```bash
python -m specomega verify --path .
```

## 2. Analyze conflicts

If multiple spec fragments disagree on the same constraint, run:

```bash
python -m specomega analyze --path .specify/specs/user_management.spec openspec/specs/user_management.md
```

## 3. Plan a multi-agent workflow

Create a workflow spec using `@agent` and `@handoff` declarations, then run:

```bash
python -m specomega plan --path .specomega/agents.md
```

## 4. Run risk analysis

```bash
python -m specomega risk --spec examples/agent_runtime/spec.md --trace examples/agent_runtime/agent_trace.json --output-dir .specomega/reports
```

The output can be exported as Markdown, JSON, SARIF, or HTML.
