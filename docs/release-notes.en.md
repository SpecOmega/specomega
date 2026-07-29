# Release Notes

## SpecOmega 0.1.0

### Release goals

SpecOmega 0.1.0 introduces an engineering-oriented verification layer for specification-driven workflows. It turns specification constraints into machine-checkable signals and gives teams audit-friendly evidence for agent handoffs, governance gates, and AI-assisted risk review.

### Highlights

- Machine-checkable verification of spec fragments
- Multi-agent workflow planning with phases, retries, fallback paths, and handoff validation
- Risk analysis and report export in JSON, Markdown, SARIF, HTML, and CSV
- Example runner and CI workflow for reproducible validation

### Documentation and experience improvements

- Added CLI metadata and an `info` subcommand
- Added a developer guide and contribution workflow
- Improved the README and quickstart onboarding path

### Verification

The following verification command was run successfully:

```bash
python -m unittest discover -s tests -v
```

### Compatibility and migration notes

- This release remains compatible with the existing CLI commands while adding `info`, `--version`, and richer help output
- If existing automation depends on older report formats, prefer the newer JSON / Markdown / SARIF / HTML / CSV outputs

### Release checklist

- [x] Changes have passed the unit test suite
- [x] CLI help and documentation are available
- [x] Example runner and CI workflow have been verified
- [ ] For a formal release, add approval and change-management notes

### Planned follow-up

- Expand the verifier and rule coverage
- Add richer multi-agent workflow examples
- Strengthen integration with CI and audit workflows
