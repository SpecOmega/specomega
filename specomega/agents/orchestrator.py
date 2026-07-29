import re
from typing import Dict, List, Optional


class MultiAgentOrchestrator:
    """Parse and evaluate SDD-style multi-agent workflows with phases, handoffs, retries, and fallbacks."""

    def plan(self, spec: str) -> Dict:
        """Build an execution plan with role metadata, handoff contracts, and workflow summary data."""
        roles = re.findall(r"@agent:\s*([a-zA-Z0-9_-]+)", spec)
        handoffs = re.findall(r"@handoff:\s*([a-zA-Z0-9_-]+)->([a-zA-Z0-9_-]+)", spec)
        phases = self._extract_phases(spec)
        constraints = self._extract_items(spec, r"@constraint:\s*(.+)")
        validations = self._extract_items(spec, r"@validation:\s*(.+)")
        deliverables = self._extract_items(spec, r"@deliverable:\s*([a-zA-Z0-9_.-]+)")
        retry_policies = self._extract_retry_policies(spec)
        fallbacks = self._extract_fallbacks(spec)
        merge_points = self._extract_merge_points(spec)
        workflow = []
        for index, role in enumerate(roles):
            phase = self._phase_for_role(role, phases, index)
            dependencies = self._derive_dependencies(role, handoffs)
            workflow.append({
                "role": role,
                "step": index + 1,
                "phase": phase,
                "status": "planned",
                "entry_conditions": self._default_entry_conditions(role),
                "exit_conditions": self._default_exit_conditions(role),
                "dependencies": dependencies,
                "lifecycle": "pending",
            })
        handoff_contracts = [{"from": src, "to": dst} for src, dst in handoffs]
        return {
            "workflow": workflow,
            "handoffs": handoff_contracts,
            "phases": phases,
            "constraints": constraints,
            "validations": validations,
            "deliverables": deliverables,
            "retry_policies": retry_policies,
            "fallbacks": fallbacks,
            "merge_points": merge_points,
            "summary": self._summarize_workflow(workflow, handoff_contracts),
        }

    def execute(self, spec: str) -> Dict:
        """Evaluate a workflow plan and annotate each role with readiness and lifecycle state."""
        plan = self.plan(spec)
        roles = [step["role"] for step in plan["workflow"]]
        handoff_targets = {item["to"] for item in plan["handoffs"]}
        missing_roles = sorted(set(handoff_targets) - set(roles))
        dependency_violations = self._detect_dependency_violations(plan)
        readiness = self._evaluate_readiness(plan)
        workflow = []
        events = []
        execution_log = []
        for index, step in enumerate(plan["workflow"]):
            if dependency_violations:
                state = "blocked"
                lifecycle = "blocked"
            else:
                state = "ready"
                lifecycle = "pending"
                if index > 0:
                    events.append({"type": "retry_scheduled", "role": step["role"], "attempt": 1})
            if any(fallback["role"] == step["role"] for fallback in plan.get("fallbacks", [])):
                events.append({"type": "fallback_proposed", "role": step["role"]})
            workflow.append({**step, "status": state, "lifecycle": lifecycle})
            execution_log.append({"role": step["role"], "state": state, "lifecycle": lifecycle})
        return {
            "valid": not missing_roles and not dependency_violations,
            "workflow": workflow,
            "handoffs": plan["handoffs"],
            "missing_roles": missing_roles,
            "dependency_violations": dependency_violations,
            "readiness": readiness,
            "events": events,
            "merge_points": plan.get("merge_points", []),
            "execution_log": execution_log,
            "summary": plan.get("summary", {}),
        }

    def run(self, spec: str) -> Dict:
        """Execute a workflow plan in a simple runtime model that records completed steps and lifecycle state."""
        plan = self.plan(spec)
        workflow = []
        execution_log = []
        for step in plan["workflow"]:
            workflow.append({**step, "lifecycle": "succeeded", "status": "succeeded"})
            execution_log.append({"role": step["role"], "event": "completed", "lifecycle": "succeeded"})
        return {
            "valid": True,
            "state": "succeeded",
            "workflow": workflow,
            "handoffs": plan["handoffs"],
            "merge_points": plan.get("merge_points", []),
            "execution_log": execution_log,
            "summary": plan.get("summary", {}),
        }

    def _extract_phases(self, spec: str) -> List[Dict]:
        phase_blocks = []
        for match in re.finditer(r"@phase\s*:\s*([a-zA-Z0-9_-]+)\s*(?:\(([^)]*)\))?", spec):
            phase_name = match.group(1)
            description = match.group(2) or ""
            phase_blocks.append({"name": phase_name, "description": description.strip()})
        if not phase_blocks:
            return [{"name": "execution", "description": "default execution phase"}]
        return phase_blocks

    def _extract_items(self, spec: str, pattern: str) -> List[str]:
        return [match.strip() for match in re.findall(pattern, spec) if match and match.strip()]

    def _extract_retry_policies(self, spec: str) -> List[Dict]:
        policies = []
        for match in re.finditer(r"@retry:\s*([a-zA-Z0-9_-]+):(\d+)", spec):
            policies.append({"role": match.group(1), "max_attempts": int(match.group(2))})
        return policies

    def _extract_fallbacks(self, spec: str) -> List[Dict]:
        fallbacks = []
        for match in re.finditer(r"@fallback:\s*([a-zA-Z0-9_-]+)->([a-zA-Z0-9_-]+)", spec):
            fallbacks.append({"role": match.group(1), "fallback_role": match.group(2)})
        return fallbacks

    def _extract_merge_points(self, spec: str) -> List[str]:
        merge_points = []
        for match in re.finditer(r"@join:\s*([a-zA-Z0-9_-]+)", spec):
            merge_points.append(match.group(1))
        return merge_points

    def _derive_dependencies(self, role: str, handoffs: List[tuple]) -> List[str]:
        dependencies = []
        for src, dst in handoffs:
            if dst == role:
                dependencies.append(src)
        return dependencies

    def _phase_for_role(self, role: str, phases: List[Dict], index: int) -> str:
        if not phases:
            return "execution"
        if role.startswith("review"):
            return phases[min(len(phases) - 1, max(0, len(phases) - 1))]["name"]
        phase_index = min(index, len(phases) - 1)
        return phases[phase_index]["name"]

    def _default_entry_conditions(self, role: str) -> List[str]:
        base = ["role declared", "inputs available"]
        if role.startswith("review"):
            base.append("artifact ready for review")
        return base

    def _default_exit_conditions(self, role: str) -> List[str]:
        base = ["output produced", "handoff contract satisfied"]
        if role.startswith("review"):
            base.append("review decision recorded")
        return base

    def _detect_dependency_violations(self, plan: Dict) -> List[Dict]:
        violations = []
        roles = {step["role"] for step in plan.get("workflow", [])}
        for handoff in plan.get("handoffs", []):
            if handoff["from"] not in roles or handoff["to"] not in roles:
                violations.append({"type": "missing_role", "handoff": handoff})
        return violations

    def _evaluate_readiness(self, plan: Dict) -> Dict:
        workflow = plan.get("workflow", [])
        if not workflow:
            return {"ready": False, "reasons": ["no agent roles declared"]}
        reasons = []
        if any(step.get("role") == "reviewer" for step in workflow):
            reasons.append("review gate present")
        if len(workflow) >= 2:
            reasons.append("multi-agent pipeline available")
        return {"ready": True, "reasons": reasons}

    def _summarize_workflow(self, workflow: List[Dict], handoffs: List[Dict]) -> Dict:
        return {
            "role_count": len(workflow),
            "handoff_count": len(handoffs),
            "roles": [step["role"] for step in workflow],
            "handoffs": [f"{item['from']}->{item['to']}" for item in handoffs],
        }
