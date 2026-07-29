import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from specomega.analysis.risk_analyzer import analyze_agent_risks
from specomega.engine import VerificationEngine


def main() -> None:
    spec_path = Path(__file__).with_name("spec.md")
    trace_path = Path(__file__).with_name("agent_trace.json")
    spec = spec_path.read_text(encoding="utf-8")
    trace = json.loads(trace_path.read_text(encoding="utf-8"))

    engine = VerificationEngine()
    verify_report = engine.verify(spec, {"agent_trace": trace})
    risk_report = analyze_agent_risks(spec, trace, use_remote=False)

    output_dir = ROOT / ".specomega" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "example_verify.json").write_text(json.dumps(verify_report, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "example_risk.json").write_text(json.dumps(risk_report, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "example_risk.md").write_text(risk_report.get("report_markdown", ""), encoding="utf-8")

    print("SpecOmega quickstart example")
    print("=" * 28)
    print("Verification result:")
    print(json.dumps(verify_report, indent=2, ensure_ascii=False))
    print("\nRisk analysis result:")
    print(json.dumps(risk_report, indent=2, ensure_ascii=False))
    print(f"\nReports written to {output_dir}")
    print("\nNext steps:")
    print("  python -m specomega verify --path .")
    print("  python -m specomega risk --spec examples/agent_runtime/spec.md --trace examples/agent_runtime/agent_trace.json --output-dir .specomega/reports --format markdown")


if __name__ == "__main__":
    main()
