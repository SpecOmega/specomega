import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from specomega.engine import VerificationEngine
from specomega.verifiers.ast_verifier import AstVerifier
from specomega.agents.orchestrator import MultiAgentOrchestrator
from specomega.analysis.llm_adapter import LLMAdapter
from specomega.analysis.risk_analyzer import RiskAnalyzer, analyze_agent_risks
from specomega.config import RuntimeConfig
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

    def test_risk_analyzer_reports_security_and_state_risks(self):
        analyzer = RiskAnalyzer()
        spec = """
        ## [SEC-202]
        Must call risk_check before pay.
        """
        trace = {
            "tool_calls": ["pay"],
            "risk_level": "medium",
            "state": "running",
            "repo": "user-service",
            "action": "write",
        }
        report = analyzer.analyze(spec, trace, use_remote=False)
        self.assertEqual("warning", report["risk_level"])
        self.assertTrue(any(item["type"] == "tool_sequence" for item in report["findings"]))
        self.assertTrue(report["recommendations"])

    def test_analyze_agent_risks_cli_helper(self):
        report = analyze_agent_risks(
            "Must call risk_check before pay.",
            {"tool_calls": ["risk_check", "pay"], "risk_level": "safe", "state": "idle"},
            use_remote=False,
        )
        self.assertEqual("ok", report["risk_level"])

    def test_llm_adapter_builds_structured_risk_summary(self):
        adapter = LLMAdapter(provider="deepseek")
        report = adapter.summarize_risk(
            spec="Must call risk_check before pay.",
            trace={"tool_calls": ["pay"], "risk_level": "medium", "state": "running"},
            findings=[{"type": "tool_sequence", "message": "缺少风险检查前置步骤"}],
        )
        self.assertIn("risk_check", report["summary"].lower())
        self.assertTrue(report["entities"])
        self.assertTrue(report["relationships"])

    def test_engine_mode_uses_local_risk_logic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "llm_config.json"
            config_path.write_text(json.dumps({"mode": "engine", "enable_llm": False, "api_key": "dummy"}), encoding="utf-8")
            adapter = LLMAdapter(provider="deepseek", config_path=config_path)
            report = adapter.summarize_risk(
                spec="Must call risk_check before pay.",
                trace={"tool_calls": ["pay"], "risk_level": "medium", "state": "running"},
                findings=[{"type": "tool_sequence", "message": "缺少风险检查前置步骤"}],
            )
            self.assertEqual("engine", adapter.mode)
            self.assertFalse(report["remote"])
            self.assertIn("工程模式", report["summary"])
            self.assertEqual("engine_fallback", report["status"])

    def test_runtime_config_reads_mode_from_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "llm_config.json"
            config_path.write_text(json.dumps({"mode": "llm", "enable_llm": True, "api_key": "x"}), encoding="utf-8")
            config = RuntimeConfig.from_file(config_path)
            self.assertEqual("llm", config.mode)
            self.assertTrue(config.enable_llm)

    def test_runtime_config_refreshes_when_file_changes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "llm_config.json"
            config_path.write_text(json.dumps({"mode": "engine", "enable_llm": False}), encoding="utf-8")
            config = RuntimeConfig.from_file(config_path)
            self.assertEqual("engine", config.mode)
            config_path.write_text(json.dumps({"mode": "llm", "enable_llm": True, "api_key": "x"}), encoding="utf-8")
            refreshed = config.refresh()
            self.assertEqual("llm", refreshed.mode)
            self.assertTrue(refreshed.enable_llm)

    def test_runtime_config_applies_llm_threshold_policy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "llm_config.json"
            config_path.write_text(json.dumps({"mode": "llm", "enable_llm": True, "api_key": "x", "llm_threshold": "warning"}), encoding="utf-8")
            config = RuntimeConfig.from_file(config_path)
            self.assertTrue(config.should_use_llm("warning"))
            self.assertFalse(config.should_use_llm("ok"))

    def test_risk_analyzer_respects_explicit_llm_threshold(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "llm_config.json"
            config_path.write_text(json.dumps({"mode": "llm", "enable_llm": True, "api_key": "x", "llm_threshold": "warning"}), encoding="utf-8")
            report = analyze_agent_risks(
                "Must call risk_check before pay.",
                {"risk_level": "ok", "tool_calls": ["pay"]},
                use_remote=False,
                config_path=config_path,
                llm_threshold="critical",
            )
            self.assertIn("工程规则", report["llm_summary"]["summary"])

    def test_bootstrap_command_runs_smoke_sequence(self):
        from specomega.cli import main

        with patch("specomega.cli.subprocess.run") as run_mock:
            run_mock.return_value = type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()
            with patch.object(sys, "argv", ["specomega", "bootstrap"]):
                main()

        commands = [call.args[0] for call in run_mock.call_args_list]
        self.assertTrue(any(cmd[:3] == [sys.executable, "-m", "unittest"] for cmd in commands))
        self.assertTrue(any(cmd[-1] == "examples/agent_runtime/run_example.py" for cmd in commands))
        self.assertTrue(any(cmd[:3] == [sys.executable, "-m", "specomega"] and cmd[3:5] == ["verify", "--path"] for cmd in commands))

    def test_cli_can_export_sarif_and_fail_on_warning(self):
        from specomega.cli import main

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = Path(tmpdir) / "spec.md"
            trace_path = Path(tmpdir) / "trace.json"
            spec_path.write_text("Must call risk_check before pay.", encoding="utf-8")
            trace_path.write_text(json.dumps({"tool_calls": ["pay"], "risk_level": "medium"}), encoding="utf-8")

            with patch.object(sys, "argv", [
                "specomega",
                "risk",
                "--spec",
                str(spec_path),
                "--trace",
                str(trace_path),
                "--output-dir",
                tmpdir,
                "--format",
                "sarif",
                "--strict",
            ]):
                with self.assertRaises(SystemExit) as cm:
                    main()

            self.assertEqual(1, cm.exception.code)
            self.assertTrue(Path(tmpdir, "risk_report.sarif").exists())

    def test_ci_workflow_exists_with_test_and_risk_steps(self):
        workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
        self.assertTrue(workflow_path.exists())
        content = workflow_path.read_text(encoding="utf-8")
        self.assertIn("python -m unittest", content)
        self.assertIn("python -m specomega risk", content)


if __name__ == "__main__":
    unittest.main()
