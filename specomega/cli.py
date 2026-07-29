import argparse
import json
import re
from pathlib import Path
from typing import Optional

from .agents.orchestrator import MultiAgentOrchestrator
from .analysis.risk_analyzer import analyze_agent_risks
from .engine import VerificationEngine


def export_sarif(report: dict) -> str:
    findings = []
    for item in report.get("findings", []):
        findings.append({
            "ruleId": item.get("type", "unknown"),
            "level": "warning",
            "message": {"text": item.get("message", "")},
        })
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "SpecOmega", "rules": []}},
            "results": findings,
        }],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def export_html(report: dict) -> str:
    body = "<html><body><h1>SpecOmega Risk Report</h1>"
    body += f"<p>Risk Level: {report.get('risk_level', 'ok')}</p>"
    for item in report.get("findings", []):
        body += f"<p>{item.get('message', '')}</p>"
    body += "</body></html>"
    return body


def main() -> None:
    parser = argparse.ArgumentParser(prog="specomega")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify", help="Verify spec markers against implementation evidence")
    verify.add_argument("--path", default=".", help="Path to a spec file or project root")
    verify.add_argument("--framework", choices=["spec-kit", "openspec", "superpowers", "auto"], default="auto")

    analyze = subparsers.add_parser("analyze", help="Analyze conflicts across spec fragments")
    analyze.add_argument("--path", nargs="+", default=[], help="Path(s) to spec files")

    plan = subparsers.add_parser("plan", help="Plan an SDD-style multi-agent workflow")
    plan.add_argument("--path", default=".", help="Path to a workflow spec file")

    analyze_risk = subparsers.add_parser("risk", help="Analyze Agent risks and produce recommendations")
    analyze_risk.add_argument("--spec", default="", help="Path to a spec file or inline text")
    analyze_risk.add_argument("--trace", default="", help="Path to a JSON trace file")
    analyze_risk.add_argument("--output-dir", default=".specomega/reports", help="Directory for markdown/json report output")
    analyze_risk.add_argument("--format", choices=["json", "markdown", "sarif", "html"], default="json", help="Report format to emit")
    analyze_risk.add_argument("--strict", action="store_true", help="Exit with status 1 when findings are present")

    args = parser.parse_args()
    if args.command == "verify":
        report = verify_path(args.path, framework=args.framework)
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.command == "analyze":
        conflicts = analyze_conflicts(args.path)
        print(json.dumps(conflicts, indent=2, ensure_ascii=False))
    elif args.command == "plan":
        target = Path(args.path)
        if target.is_file():
            spec = target.read_text(encoding="utf-8")
        else:
            spec = ""
        orchestrator = MultiAgentOrchestrator()
        print(json.dumps(orchestrator.execute(spec), indent=2, ensure_ascii=False))
    elif args.command == "risk":
        spec_text = args.spec
        trace_text = args.trace
        if args.spec and Path(args.spec).exists():
            spec_text = Path(args.spec).read_text(encoding="utf-8")
        if args.trace and Path(args.trace).exists():
            trace_text = Path(args.trace).read_text(encoding="utf-8")
            trace_payload = json.loads(trace_text)
        else:
            trace_payload = {}
        report = analyze_agent_risks(spec_text, trace_payload, use_remote=False)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "risk_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (output_dir / "risk_report.md").write_text(report.get("report_markdown", ""), encoding="utf-8")
        if args.format == "sarif":
            (output_dir / "risk_report.sarif").write_text(export_sarif(report), encoding="utf-8")
        elif args.format == "html":
            (output_dir / "risk_report.html").write_text(export_html(report), encoding="utf-8")
        if args.strict and report.get("risk_level") == "warning":
            raise SystemExit(1)
        if args.format == "json":
            print(json.dumps(report, indent=2, ensure_ascii=False))
        elif args.format == "markdown":
            print(report.get("report_markdown", ""))
        elif args.format == "sarif":
            print(export_sarif(report))
        else:
            print(export_html(report))


def verify_path(path: str, framework: str = "auto") -> dict:
    target = Path(path)
    engine = VerificationEngine()

    if target.is_file():
        content = target.read_text(encoding="utf-8")
        report = engine.verify(content, {"framework": framework, "superpowers_session": "demo-session"})
        report["framework"] = framework
        engine.write_report(report, target.parent / ".specomega" / "reports" / "latest.json")
        return report

    spec_files = list(target.rglob("*.spec")) + list(target.rglob("*.md"))
    results = []
    for spec_file in spec_files:
        content = spec_file.read_text(encoding="utf-8")
        results.extend(engine.verify(content, {"framework": framework, "superpowers_session": "demo-session"})["results"])
    report = {"framework": framework, "results": results}
    engine.write_report(report, target / ".specomega" / "reports" / "latest.json")
    return report


def analyze_conflicts(paths: list[str]) -> list[dict]:
    fragments = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.exists():
            fragments.append((path.name, path.read_text(encoding="utf-8")))
    conflicts = []
    for index, (left_name, left_text) in enumerate(fragments):
        for right_name, right_text in fragments[index + 1:]:
            left_matches = re.findall(r"(400|200|500|401|403)", left_text)
            right_matches = re.findall(r"(400|200|500|401|403)", right_text)
            if left_matches and right_matches and set(left_matches) != set(right_matches):
                conflicts.append({
                    "files": [left_name, right_name],
                    "matches": [left_matches, right_matches],
                })
    return conflicts
