import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from specomega.engine import VerificationEngine


def main() -> None:
    spec_path = Path(__file__).with_name("spec.md")
    trace_path = Path(__file__).with_name("agent_trace.json")
    spec = spec_path.read_text(encoding="utf-8")
    trace = json.loads(trace_path.read_text(encoding="utf-8"))

    engine = VerificationEngine()
    report = engine.verify(spec, {"agent_trace": trace})
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
