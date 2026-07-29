# Contributing

Contributions are welcome.

## Development workflow

1. Create a feature branch from the latest `main` branch.
2. Add or update tests for the behavior you change.
3. Run the local verification flow below.
4. Update the relevant documentation if the CLI, workflow semantics, handoff rules, or governance outputs change.
5. Submit a pull request with a clear summary and evidence from the verification run.

## First-time setup

```bash
cd /workspaces/specomega
python -m specomega --version
python -m specomega info
python -m unittest discover -s tests -v
```

These commands confirm that the CLI entrypoints and test environment are healthy before you begin implementation work.

## Local verification

```bash
python -m unittest discover -s tests -v
python examples/agent_runtime/run_example.py
python -m specomega verify --path .
python -m specomega plan --path .specomega/agents.md
python -m specomega vibecode --paths docs specomega --output-dir .specomega/reports
```

When you update workflow semantics, handoff rules, or Vibecode behavior, also update the relevant docs under [docs](docs) and the sample workflow in [.specomega/agents.md](.specomega/agents.md).

## Recommended contribution loop

For day-to-day development, follow this loop:

1. Start from the latest `main` branch.
2. Make a small change and add or update a regression test.
3. Run the local verification commands below.
4. Review the CLI output, reports, and docs to ensure the change is discoverable and understandable.
5. Submit a pull request with a concise summary and the verification evidence.

## Pull request checklist

- Tests are passing locally.
- Relevant docs and examples were updated when behavior changed.
- CLI outputs or report formats remain backward-compatible unless intentionally changed.
- The change includes a concise summary of the problem, the fix, and the verification evidence.
- The change is easy to understand from the README, help output, and documentation paths.
