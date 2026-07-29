from __future__ import annotations

from typing import Dict


def describe_framework_stack() -> Dict[str, object]:
    """Describe how Spec Kit, OpenSpec, and Superpowers cooperate with SpecOmega.

    This model follows established software engineering and requirements engineering
    practice: Spec Kit captures requirements and acceptance criteria, OpenSpec
    organizes change specifications and versioned deliverables, and Superpowers
    provides execution discipline and operational guardrails. SpecOmega acts as
    the verification and governance layer that turns these artifacts into auditable
    evidence and policy-enforced controls.
    """

    return {
        "mode": "spec-driven-engineering",
        "frameworks": {
            "spec_kit": {
                "name": "Spec Kit",
                "primary_role": "requirements and acceptance criteria",
                "focus": "capture user needs, functional intent, and validation expectations in a structured form",
                "typical_artifacts": ["requirements", "acceptance criteria", "feature briefs"],
                "standards_alignment": ["ISO/IEC/IEEE 12207", "IEEE 29148"],
            },
            "openspec": {
                "name": "OpenSpec",
                "primary_role": "change specification and delivery contracts",
                "focus": "describe change sets, interfaces, and implementation expectations as versioned, testable spec fragments",
                "typical_artifacts": ["spec fragments", "change contracts", "release notes"],
                "standards_alignment": ["OpenAPI", "IEEE 29148", "ISO/IEC/IEEE 12207"],
            },
            "superpowers": {
                "name": "Superpowers",
                "primary_role": "execution and governance",
                "focus": "enforce execution discipline, tool usage, handoffs, and operational safeguards during implementation",
                "typical_artifacts": ["runtime policies", "workflow constraints", "guardrails"],
                "standards_alignment": ["ISO/IEC 27001", "NIST SSDF", "IEEE 7000"],
            },
        },
        "coordination": {
            "governance_layer": "SpecOmega (specomega)",
            "how_they_work_together": [
                "Spec Kit defines what must be true.",
                "OpenSpec turns those intentions into change-ready contracts and testable specifications.",
                "Superpowers governs how execution should happen safely and consistently.",
                "SpecOmega verifies whether requirements, implementation, and runtime behavior actually align.",
            ],
            "reference_standards": ["IEEE 29148", "ISO/IEC/IEEE 12207", "NIST SSDF", "ISO/IEC 27001"],
            "delivery_flow": [
                "1. Capture intent and acceptance criteria.",
                "2. Decompose the change into spec fragments and contracts.",
                "3. Enforce operational rules and tool sequencing.",
                "4. Verify the implementation and generate audit evidence.",
            ],
        },
    }
