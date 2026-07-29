# Developer Guide

## Purpose

This guide is intended for developers who want to contribute to SpecOmega, extend its verification capabilities, or fix issues. It focuses on the project layout, entry points, validation flow, and recommended development patterns.

## 1. Project layout

- [specomega](../specomega): the core Python package, including the CLI, engine, verifiers, and analysis modules.
- [tests](../tests): regression tests and behavior validations.
- [examples](../examples): runnable example scripts and sample inputs.
- [docs](../docs): architecture, usage, and development documentation.
- [.specomega](../.specomega): default configuration, workflow examples, and report output.

## 2. Key modules

- `specomega/cli.py`: command-line entry point for `verify`, `analyze`, `plan`, `risk`, `vibecode`, and `info`.
- `specomega/engine.py`: the unified verification engine that dispatches validators and consolidates output.
- `specomega/verifiers/`: contract, trace, security, and syntax-boundary verification logic.
- `specomega/analysis/`: Vibecode analysis, risk analysis, and framework coordination logic.
- `specomega/agents/orchestrator.py`: orchestration for multi-agent workflows.

## 3. Recommended starting flow

Start with:

```bash
python -m specomega --version
python -m specomega info
python -m unittest discover -s tests -v
```

These commands confirm that the CLI entrypoints and test environment are healthy before you begin implementation work.

## 4. Recommended development loop

1. Understand which subsystem you need to change, such as the CLI, validators, analysis flow, or documentation.
2. Add or update a regression test before changing the implementation.
3. Run the core validation flow:

```bash
python -m unittest discover -s tests -v
python examples/agent_runtime/run_example.py
python -m specomega verify --path .
```

4. If you changed workflow semantics, governance rules, or report formats, update the related docs and examples.

## 5. Notes for contributors

- Keep CLI output stable unless the change intentionally breaks compatibility.
- Prefer tests for new commands or modified report structures.
- For governance and audit behavior, keep the example workflow, docs, and configuration in sync.

## 6. Documentation and examples

When any of the following changes, update the related docs:

- CLI commands or parameters
- Report formats or output names
- Verification rules or governance gates
- Example workflows and inputs

Suggested files to update include:

- [README.md](../README.md)
- [docs/quickstart.en.md](./quickstart.en.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [CHANGELOG.md](../CHANGELOG.md)

## 7. Contribution checklist

Before submitting a PR, confirm that:

- Local tests are passing
- Relevant docs are updated
- Key behavior is covered by regression tests
- The change summary is concise and traceable
