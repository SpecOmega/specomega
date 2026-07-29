import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from specomega.analysis.vibecode import VibecodeAnalyzer


def main() -> None:
    analyzer = VibecodeAnalyzer()
    result = analyzer.analyze("Local git server review should flag vibecode workflow usage. Trace: prompt->model->patch. Intent: deliver release validation.")
    output_dir = ROOT / ".specomega" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "vibecode_git.txt").write_text(
        f"[vibecode] severity={result.get('severity', 'none')} score={result.get('score', 0)} {result.get('summary', '')}",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
