import json
import tempfile
import unittest
from pathlib import Path

from specomega.engine import VerificationEngine
from specomega.verifiers.ast_verifier import AstVerifier
from specomega.agents.orchestrator import MultiAgentOrchestrator
from specomega.verifiers.contract_verifier import ContractVerifier
from specomega.verifiers.trace_verifier import TraceVerifier


class SpecOmegaEngineTests(unittest.TestCase):
    def test_ast_verifier_detects_boundary_rule(self):
        verifier = AstVerifier()
        fragment = "GIVEN page=0 WHEN list THEN must return 400"
        ok, failures, evidence = verifier.verify(fragment, {})
        self.assertTrue(ok)
        self.assertEqual([], failures)
        self.assertIn("page=0", evidence["matched_text"])

    def test_contract_verifier_uses_context_evidence(self):
        verifier = ContractVerifier()
        fragment = "@specomega: contract_check(page_zero=400)"
        context = {"superpowers_session": "demo-session"}
        ok, failures, evidence = verifier.verify(fragment, context)
        self.assertTrue(ok)
        self.assertEqual([], failures)
        self.assertEqual("400", evidence["page_zero"])

    def test_trace_verifier_extracts_required_gates(self):
        verifier = TraceVerifier()
        fragment = "@specomega: trace_check(ReviewGate,Finalize)"
        context = {"superpowers_session": "demo-session"}
        ok, failures, evidence = verifier.verify(fragment, context)
        self.assertTrue(ok)
        self.assertEqual([], failures)
        self.assertIn("ReviewGate", evidence["required"])

    def test_engine_dispatches_marked_fragments(self):
        engine = VerificationEngine()
        spec = """
        ## [BOUNDARY-001]
        GIVEN page=0
        WHEN request user list
        THEN must return 400
        **验证要求**：@specomega: contract_check(page_zero=400)
        """
        report = engine.verify(spec, {"superpowers_session": "demo-session"})
        self.assertEqual(1, len(report["results"]))
        self.assertTrue(report["results"][0]["passed"])

    def test_verify_path_writes_report_file(self):
        from specomega.cli import verify_path

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = Path(tmpdir) / "spec.md"
            spec_path.write_text("@specomega: contract_check(page_zero=400)", encoding="utf-8")
            report = verify_path(str(spec_path), framework="spec-kit")
            report_path = Path(tmpdir) / ".specomega" / "reports" / "latest.json"
            self.assertTrue(report_path.exists())
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["results"][0]["tag"], payload["results"][0]["tag"])

    def test_analyze_conflicts_detects_inconsistent_requirements(self):
        from specomega.cli import analyze_conflicts

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first = root / "a.spec"
            second = root / "b.spec"
            first.write_text("must return 400", encoding="utf-8")
            second.write_text("must return 200", encoding="utf-8")
            conflicts = analyze_conflicts([first, second])
            self.assertTrue(conflicts)
            self.assertEqual(2, len(conflicts[0]["matches"]))

    def test_engine_can_load_verifiers_from_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("verifiers:\n  - security_verifier\n", encoding="utf-8")
            engine = VerificationEngine.from_config(config_path)
            report = engine.verify("@specomega: security_check(cwe_134)", {})
            self.assertTrue(report["results"])
            self.assertTrue(report["results"][0]["passed"])

    def test_multi_agent_orchestrator_builds_workflow_plan(self):
        orchestrator = MultiAgentOrchestrator()
        spec = """
        ## Goal
        @agent: planner
        @agent: implementer
        @agent: reviewer
        @handoff: planner->implementer
        @handoff: implementer->reviewer
        """
        plan = orchestrator.plan(spec)
        self.assertEqual(["planner", "implementer", "reviewer"], [step["role"] for step in plan["workflow"]])
        self.assertEqual(2, len(plan["handoffs"]))

    def test_multi_agent_orchestrator_requires_handoff_contract(self):
        orchestrator = MultiAgentOrchestrator()
        spec = """
        ## Goal
        @agent: planner
        @agent: implementer
        @handoff: planner->reviewer
        """
        result = orchestrator.execute(spec)
        self.assertFalse(result["valid"])
        self.assertIn("reviewer", result["missing_roles"])


if __name__ == "__main__":
    unittest.main()
