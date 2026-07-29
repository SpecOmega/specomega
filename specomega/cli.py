import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .agents.orchestrator import MultiAgentOrchestrator
from .analysis.risk_analyzer import analyze_agent_risks
from .analysis.vibecode import VibecodeAnalyzer
from .engine import VerificationEngine


def export_vibecode_report(result: dict, output_dir: Path, format_name: str = "json", config: Optional[dict] = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "vibecode_report.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown_lines = [
        "# Vibecode Report",
        "",
        f"- Severity: **{result.get('severity', 'none')}**",
        f"- Score: {result.get('score', 0)}",
        f"- Source Type: **{result.get('source_type', 'unknown')}**",
        f"- Source Confidence: **{result.get('source_confidence', 0.0):.2f}**",
        f"- Source Evidence: **{', '.join(result.get('source_evidence', [])) or 'n/a'}**",
    ]
    if result.get("source_summary"):
        markdown_lines.append("")
        markdown_lines.append("## Source Summary")
        for source_type, count in sorted(result.get("source_summary", {}).items()):
            markdown_lines.append(f"- {source_type}: {count}")
    if result.get("language_summary"):
        markdown_lines.append("")
        markdown_lines.append("## Language Summary")
        for language, count in sorted(result.get("language_summary", {}).items()):
            markdown_lines.append(f"- {language}: {count}")
    if result.get("summary_label"):
        markdown_lines.append("")
        markdown_lines.append(f"**{result.get('summary_label')}**")
    if result.get("risk_level"):
        markdown_lines.append("")
        markdown_lines.append("## Governance Risk")
        markdown_lines.append(f"- Risk Level: **{result.get('risk_level')}**")
        if result.get("recommended_actions"):
            markdown_lines.append("- Recommended Actions:")
            for action in result.get("recommended_actions", []):
                markdown_lines.append(f"  - {action}")
    if result.get("behavior"):
        markdown_lines.append("")
        markdown_lines.append("## Behavior Analysis")
        behavior = result.get("behavior", {})
        for key, value in sorted(behavior.items()):
            if key == "evidence":
                continue
            markdown_lines.append(f"- {key}: {value}")
        if behavior.get("evidence"):
            markdown_lines.append(f"- evidence: {', '.join(behavior.get('evidence', []))}")
    if result.get("trace_analysis"):
        markdown_lines.append("")
        markdown_lines.append("## Trace Analysis")
        trace = result.get("trace_analysis", {})
        markdown_lines.append(f"- detected: {trace.get('detected')}")
        if trace.get("evidence"):
            markdown_lines.append(f"- evidence: {', '.join(trace.get('evidence', []))}")
    if result.get("intent_analysis"):
        markdown_lines.append("")
        markdown_lines.append("## Intent & Goal Analysis")
        intent = result.get("intent_analysis", {})
        markdown_lines.append(f"- has_intent: {intent.get('has_intent')}")
        markdown_lines.append(f"- has_goal: {intent.get('has_goal')}")
        if intent.get("intent_text"):
            markdown_lines.append(f"- intent: {intent.get('intent_text')}")
        if intent.get("goal_text"):
            markdown_lines.append(f"- goal: {intent.get('goal_text')}")
    if result.get("dynamic_rules"):
        markdown_lines.append("")
        markdown_lines.append("## Dynamic Rules")
        dynamic = result.get("dynamic_rules", {})
        markdown_lines.append(f"- matched: {dynamic.get('matched')}")
        if dynamic.get("matches"):
            markdown_lines.append(f"- matches: {', '.join(dynamic.get('matches', []))}")
    if result.get("classification"):
        markdown_lines.append("")
        markdown_lines.append("## Classification")
        classification = result.get("classification", {})
        for key, value in sorted(classification.items()):
            markdown_lines.append(f"- {key}: {value}")
    profile_name = result.get("profile") or result.get("profile_name")
    if profile_name or result.get("threshold") is not None or result.get("policy"):
        markdown_lines.append("")
        markdown_lines.append("## Governance Profile")
        markdown_lines.append(f"- Profile: **{profile_name or 'default'}**")
        markdown_lines.append(f"- Threshold: **{result.get('threshold', 'n/a')}**")
        policy = result.get("policy") or {}
        if policy:
            markdown_lines.append("- Policy:")
            for key, value in sorted(policy.items()):
                markdown_lines.append(f"  - {key}: {value}")
    if result.get("audit_summary"):
        markdown_lines.append("")
        markdown_lines.append("## Audit Summary")
        for key, value in result.get("audit_summary", {}).items():
            if isinstance(value, list):
                markdown_lines.append(f"- {key}: {', '.join(str(item) for item in value)}")
            else:
                markdown_lines.append(f"- {key}: {value}")
    if result.get("file_summary"):
        markdown_lines.append("")
        markdown_lines.append("## File Summary")
        for entry in result.get("file_summary", []):
            markdown_lines.append(f"- {entry.get('name')}: {entry.get('source_type')} ({entry.get('language')}, confidence={entry.get('confidence', 0.0):.2f})")
    markdown_lines.extend(["", result.get("summary", ""), ""])
    (output_dir / "vibecode_report.md").write_text("\n".join(markdown_lines), encoding="utf-8")
    if format_name == "sarif":
        sarif_payload = {
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {"driver": {"name": "SpecOmega Vibecode", "rules": []}},
                "results": [{
                    "ruleId": "vibecode-signal",
                    "level": "warning" if result.get("is_vibecode") else "none",
                    "message": {"text": f"{result.get('summary', '')} [severity={result.get('severity', 'none')}]"},
                }],
            }],
        }
        (output_dir / "vibecode_report.sarif").write_text(json.dumps(sarif_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    if format_name == "html":
        html_lines = [
            "<html><body>",
            "<h1>Vibecode Audit Report</h1>",
            f"<p><strong>Severity:</strong> {result.get('severity', 'none')}</p>",
            f"<p><strong>Score:</strong> {result.get('score', 0)}</p>",
            f"<p><strong>Source Type:</strong> {result.get('source_type', 'unknown')}</p>",
            f"<p><strong>Source Confidence:</strong> {result.get('source_confidence', 0.0):.2f}</p>",
            f"<p><strong>Risk Level:</strong> {result.get('risk_level', 'low')}</p>",
            "<h2>Summary</h2>",
            f"<p>{result.get('summary', '')}</p>",
        ]
        profile_name = result.get("profile") or result.get("profile_name")
        if profile_name or result.get("threshold") is not None or result.get("policy"):
            html_lines.append("<h2>Governance Profile</h2>")
            html_lines.append("<ul>")
            html_lines.append(f"<li><strong>Profile:</strong> {profile_name or 'default'}</li>")
            html_lines.append(f"<li><strong>Threshold:</strong> {result.get('threshold', 'n/a')}</li>")
            policy = result.get("policy") or {}
            if policy:
                html_lines.append("<li><strong>Policy:</strong></li>")
                html_lines.append("<ul>")
                for key, value in sorted(policy.items()):
                    html_lines.append(f"<li>{key}: {value}</li>")
                html_lines.append("</ul>")
            html_lines.append("</ul>")
        if result.get("audit_summary"):
            html_lines.append("<h2>Audit Summary</h2>")
            html_lines.append("<ul>")
            for key, value in result.get("audit_summary", {}).items():
                html_lines.append(f"<li><strong>{key}:</strong> {value}</li>")
            html_lines.append("</ul>")
        if result.get("behavior"):
            html_lines.append("<h2>Behavior Analysis</h2>")
            html_lines.append("<ul>")
            for key, value in sorted(result.get("behavior", {}).items()):
                if key == "evidence":
                    continue
                html_lines.append(f"<li><strong>{key}:</strong> {value}</li>")
            if result.get("behavior", {}).get("evidence"):
                html_lines.append(f"<li><strong>evidence:</strong> {', '.join(result.get('behavior', {}).get('evidence', []))}</li>")
            html_lines.append("</ul>")
        if result.get("trace_analysis"):
            html_lines.append("<h2>Trace Analysis</h2>")
            html_lines.append("<ul>")
            html_lines.append(f"<li><strong>detected:</strong> {result.get('trace_analysis', {}).get('detected')}</li>")
            if result.get("trace_analysis", {}).get("evidence"):
                html_lines.append(f"<li><strong>evidence:</strong> {', '.join(result.get('trace_analysis', {}).get('evidence', []))}</li>")
            html_lines.append("</ul>")
        if result.get("intent_analysis"):
            html_lines.append("<h2>Intent & Goal Analysis</h2>")
            html_lines.append("<ul>")
            html_lines.append(f"<li><strong>has_intent:</strong> {result.get('intent_analysis', {}).get('has_intent')}</li>")
            html_lines.append(f"<li><strong>has_goal:</strong> {result.get('intent_analysis', {}).get('has_goal')}</li>")
            if result.get("intent_analysis", {}).get("intent_text"):
                html_lines.append(f"<li><strong>intent:</strong> {result.get('intent_analysis', {}).get('intent_text')}</li>")
            if result.get("intent_analysis", {}).get("goal_text"):
                html_lines.append(f"<li><strong>goal:</strong> {result.get('intent_analysis', {}).get('goal_text')}</li>")
            html_lines.append("</ul>")
        if result.get("dynamic_rules"):
            html_lines.append("<h2>Dynamic Rules</h2>")
            html_lines.append("<ul>")
            html_lines.append(f"<li><strong>matched:</strong> {result.get('dynamic_rules', {}).get('matched')}</li>")
            if result.get("dynamic_rules", {}).get("matches"):
                html_lines.append(f"<li><strong>matches:</strong> {', '.join(result.get('dynamic_rules', {}).get('matches', []))}</li>")
            html_lines.append("</ul>")
        if result.get("classification"):
            html_lines.append("<h2>Classification</h2>")
            html_lines.append("<ul>")
            for key, value in sorted(result.get("classification", {}).items()):
                html_lines.append(f"<li><strong>{key}:</strong> {value}</li>")
            html_lines.append("</ul>")
        if result.get("file_summary"):
            html_lines.append("<h2>File Summary</h2>")
            html_lines.append("<ul>")
            for entry in result.get("file_summary", []):
                html_lines.append(f"<li>{entry.get('name')}: {entry.get('source_type')} ({entry.get('language')}, confidence={entry.get('confidence', 0.0):.2f})</li>")
            html_lines.append("</ul>")
        html_lines.extend(["</body></html>"])
        (output_dir / "vibecode_report.html").write_text("\n".join(html_lines), encoding="utf-8")

    if format_name == "csv":
        rows = []
        if result.get("file_summary"):
            rows = [
                ["name", "language", "source_type", "confidence", "evidence"],
            ]
            for entry in result.get("file_summary", []):
                rows.append([
                    entry.get("name", ""),
                    entry.get("language", "unknown"),
                    entry.get("source_type", "unknown"),
                    f"{entry.get('confidence', 0.0):.2f}",
                    ";".join(str(item) for item in entry.get("evidence", [])),
                ])
        else:
            rows = [["name", "language", "source_type", "confidence", "evidence"], ["", "", "", "", ""]]
        csv_content = "\n".join(",".join(str(cell).replace(",", " ") for cell in row) for row in rows)
        (output_dir / "vibecode_report.csv").write_text(csv_content, encoding="utf-8")

    annotation_lines = [
        f"::warning title=Vibecode::{result.get('summary', '')} [severity={result.get('severity', 'none')}] [source={result.get('source_type', 'unknown')}] [confidence={result.get('source_confidence', 0.0):.2f}]"
    ] if result.get("is_vibecode") else []
    (output_dir / "vibecode_annotations.txt").write_text("\n".join(annotation_lines), encoding="utf-8")

    git_lines = [
        f"[vibecode] severity={result.get('severity', 'none')} score={result.get('score', 0)} source={result.get('source_type', 'unknown')} confidence={result.get('source_confidence', 0.0):.2f} {result.get('summary', '')}"
    ] if result.get("is_vibecode") else []
    (output_dir / "vibecode_git.txt").write_text("\n".join(git_lines), encoding="utf-8")

    gate_blocked, gate_status = "", "pass"
    if config is not None:
        gate_blocked, gate_status = VibecodeAnalyzer().evaluate_policy_gate(result, config)
    else:
        gate_blocked = result.get("is_vibecode")
        gate_status = "blocked" if gate_blocked else "pass"
    gate_lines = [
        f"status={'blocked' if gate_blocked else gate_status}",
        f"risk_level={result.get('risk_level', 'low')}",
        f"severity={result.get('severity', 'none')}",
        f"source={result.get('source_type', 'unknown')}",
        f"confidence={result.get('source_confidence', 0.0):.2f}",
        f"actions={';'.join(result.get('recommended_actions', []))}",
    ]
    (output_dir / "vibecode_gate.txt").write_text("\n".join(gate_lines), encoding="utf-8")

    summary_lines = [
        "Vibecode Summary",
        f"severity={result.get('severity', 'none')}",
        f"risk_level={result.get('risk_level', 'low')}",
        f"source={result.get('source_type', 'unknown')}",
        f"confidence={result.get('source_confidence', 0.0):.2f}",
        f"profile={result.get('profile') or 'default'}",
        f"threshold={result.get('threshold', 'n/a')}",
        f"summary={result.get('summary', '')}",
    ]
    (output_dir / "vibecode_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")


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
    analyze_risk.add_argument("--llm-threshold", default=None, help="Override the minimum risk level that can trigger remote LLM usage")
    analyze_risk.add_argument("--config", default=".specomega/llm_config.json", help="Path to runtime config file")

    vibecode = subparsers.add_parser("vibecode", help="Analyze text or files for Vibecode-related signals")
    vibecode.add_argument("text", nargs="?", default="", help="Text to analyze")
    vibecode.add_argument("--paths", nargs="*", default=[], help="Optional file or directory paths to scan")
    vibecode.add_argument("--output-dir", default=".specomega/reports", help="Directory for Vibecode report output")
    vibecode.add_argument("--format", choices=["json", "markdown", "sarif", "html", "csv"], default="json", help="Report format to emit")
    vibecode.add_argument("--strict", action="store_true", help="Exit with status 1 when Vibecode signals are detected")
    vibecode.add_argument("--config", default=".specomega/vibecode_config.json", help="Path to Vibecode config file")
    vibecode.add_argument("--profile", default=None, help="Optional profile name to use from the config file")

    bootstrap = subparsers.add_parser("bootstrap", help="Run the default smoke-test workflow")

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
        report = analyze_agent_risks(
            spec_text,
            trace_payload,
            use_remote=False,
            config_path=Path(args.config),
            llm_threshold=args.llm_threshold,
        )
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
    elif args.command == "vibecode":
        analyzer = VibecodeAnalyzer()
        config = analyzer.load_config(Path(args.config))
        selected_profile = args.profile or os.getenv("VIBECODE_PROFILE") or (config.get("profile") if isinstance(config, dict) else None)
        effective_config = analyzer._get_profile_config(config, selected_profile)
        if args.profile or os.getenv("VIBECODE_PROFILE"):
            effective_config = dict(effective_config)
            effective_config["profile"] = selected_profile
        threshold = int(effective_config.get("threshold", config.get("threshold", 2)))
        if args.paths:
            expanded_paths = []
            for raw_path in args.paths:
                path = Path(raw_path)
                if path.is_dir():
                    expanded_paths.extend(str(item) for item in path.rglob("*") if item.is_file())
                else:
                    expanded_paths.append(str(path))
            result = analyzer.scan_paths(expanded_paths, config_path=Path(args.config), config=effective_config)
        else:
            result = analyzer.analyze(args.text, config_path=Path(args.config), config=effective_config)
        result["threshold"] = threshold
        result["profile"] = selected_profile
        result["policy"] = effective_config.get("policy", {})
        result["is_vibecode"] = result.get("score", 0) >= threshold
        output_dir = Path(args.output_dir)
        export_vibecode_report(result, output_dir, format_name=args.format, config=config)
        if args.strict and result.get("is_vibecode"):
            raise SystemExit(1)
        if args.format == "sarif":
            print((output_dir / "vibecode_report.sarif").read_text(encoding="utf-8"))
        elif args.format == "markdown":
            print((output_dir / "vibecode_report.md").read_text(encoding="utf-8"))
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "bootstrap":
        commands = [
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            [sys.executable, "examples/agent_runtime/run_example.py"],
            [sys.executable, "-m", "specomega", "verify", "--path", "."],
        ]
        results = []
        for command in commands:
            print(f"> {' '.join(command)}")
            completed = subprocess.run(command, check=False)
            results.append((command, completed.returncode))
            if completed.returncode != 0:
                print(f"[FAIL] {' '.join(command)}")
                raise SystemExit(completed.returncode)
            print(f"[OK] {' '.join(command)}")
        summary = {
            "command": "bootstrap",
            "results": [
                {"command": " ".join(command), "status": "ok" if returncode == 0 else "fail"}
                for command, returncode in results
            ],
        }
        output_dir = Path(".specomega/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "bootstrap_report.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        print("\nBootstrap summary:")
        for command, returncode in results:
            status = "OK" if returncode == 0 else "FAIL"
            print(f"- {status}: {' '.join(command)}")
        print(f"\nBootstrap report written to {output_dir / 'bootstrap_report.json'}")


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
