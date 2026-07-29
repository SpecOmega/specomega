import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from specomega.analysis.vibecode import VibecodeAnalyzer


def main() -> None:
    config_path = ROOT / ".specomega" / "vibecode_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    if not config.get("repository_sources"):
        config["repository_sources"] = ["local-git-server", "internal-git"]
    analyzer = VibecodeAnalyzer()
    result = analyzer.analyze(
        "Local git server review should flag vibecode workflow usage. Trace: prompt->model->patch. Intent: deliver release validation. Source: local-git-server. Workflow: planner->implementer->reviewer",
        config=config,
    )
    output_dir = ROOT / ".specomega" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "vibecode_git.txt").write_text(
        f"[vibecode] severity={result.get('severity', 'none')} score={result.get('score', 0)} {result.get('summary', '')}",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
