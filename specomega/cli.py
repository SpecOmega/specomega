import argparse
import json
import re
from pathlib import Path
from typing import Optional

from .agents.orchestrator import MultiAgentOrchestrator
from .engine import VerificationEngine


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
