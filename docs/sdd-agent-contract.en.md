# SDD Agent Contract

SpecOmega provides an engineering-oriented contract layer for multi-agent workflows. Roles are declared with `@agent`, and handoffs are declared with `@handoff`.

## Example

```text
@agent: planner
@agent: implementer
@agent: reviewer
@handoff: planner->implementer
@handoff: implementer->reviewer
@phase: planning
@phase: execution
@retry: implementer:3
@fallback: implementer->reviewer
@join: review_gate
```

These declarations can be validated by the orchestrator to ensure that the workflow has a coherent role graph, that required handoff targets exist, and that phase, retry, fallback, and merge semantics are represented in a machine-readable form.
