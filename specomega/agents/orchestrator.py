import re
from typing import Dict, List, Optional


class MultiAgentOrchestrator:
    """A lightweight orchestrator for SDD-style multi-agent workflows."""

    def plan(self, spec: str) -> Dict:
        roles = re.findall(r"@agent:\s*([a-zA-Z0-9_-]+)", spec)
        handoffs = re.findall(r"@handoff:\s*([a-zA-Z0-9_-]+)->([a-zA-Z0-9_-]+)", spec)
        workflow = [{"role": role, "step": index + 1} for index, role in enumerate(roles)]
        return {"workflow": workflow, "handoffs": [{"from": src, "to": dst} for src, dst in handoffs]}

    def execute(self, spec: str) -> Dict:
        plan = self.plan(spec)
        roles = [step["role"] for step in plan["workflow"]]
        handoff_targets = {item["to"] for item in plan["handoffs"]}
        missing_roles = sorted(set(handoff_targets) - set(roles))
        return {
            "valid": not missing_roles,
            "workflow": plan["workflow"],
            "handoffs": plan["handoffs"],
            "missing_roles": missing_roles,
        }
