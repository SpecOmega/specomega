## SDD Multi-Agent Workflow

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
