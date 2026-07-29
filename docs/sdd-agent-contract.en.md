# SDD Agent Contract

SpecOmega provides a lightweight contract layer for multi-agent workflows. Roles are declared with `@agent`, and handoffs are declared with `@handoff`.

## Example

```text
@agent: planner
@agent: implementer
@agent: reviewer
@handoff: planner->implementer
@handoff: implementer->reviewer
```

These declarations can be validated by the orchestrator to ensure that the workflow has a coherent role graph and that required handoff targets exist.
