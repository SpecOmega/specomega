# Architecture Overview

SpecOmega is an engineering-oriented verification and governance layer for specification-driven workflows. It connects specification fragments, execution evidence, agent coordination rules, and generative-code signals into a single audit-friendly pipeline that can run in CI and review environments.

## Core Components

- Verification engine: dispatches verifiers for spec markers and evidence checks.
- Verifiers: validate contract, trace, security, tool-call sequence, and Vibecode requirements.
- Vibecode analyzer: detects keyword signals, source types, confidence, and evidence for AI-assisted or templated content.
- Multi-agent orchestrator: parses agent, handoff, phase, retry, fallback, and join rules, then validates workflow structure and readiness.
- Risk analyzer: inspects spec and trace data and emits structured recommendations.
- CLI: offers entry points for verification, analysis, planning, risk reporting, and Vibecode governance output, with optional LLM-backed summaries and local fallback logic.

## Typical Flow

1. A specification fragment is read.
2. The verification engine identifies relevant markers such as `@specomega:`.
3. Matching verifiers execute and produce evidence.
4. The Vibecode analyzer may add governance signals for AI-generated or templated content.
5. The result is written to a report file or exported in JSON, Markdown, HTML, CSV, or SARIF format.
6. The governance layer can additionally produce a gate artifact for review or CI workflows.

## How Spec Kit, OpenSpec, and Superpowers Work Together

SpecOmega is not meant to replace these tools; it complements them by providing a verification and governance layer.

- Spec Kit focuses on defining requirements, user intent, and acceptance criteria. This aligns with established requirements engineering practice such as IEEE 29148 and ISO/IEC/IEEE 12207.
- OpenSpec turns those intentions into change-ready specification fragments and delivery contracts that can be reviewed and tested.
- Superpowers provides execution discipline for tool usage, handoffs, permissions, retries, and guardrails. This is consistent with secure software delivery practices such as NIST SSDF and ISO/IEC 27001.
- SpecOmega verifies whether the stated requirements, the implemented change, and the runtime behavior are consistent, then emits auditable evidence for CI and review.

In practice, the flow is: define intent with Spec Kit, turn it into structured delivery contracts with OpenSpec, enforce safe execution with Superpowers, and validate the result with SpecOmega.
