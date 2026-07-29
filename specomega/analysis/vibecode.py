import json
import re
from pathlib import Path
from typing import Dict, List


class VibecodeAnalyzer:
    """Lightweight analyzer for Vibecode-related signals."""

    def __init__(self) -> None:
        self.keywords = ["vibecode", "vibe", "prompt-driven", "agent workflow", "autonomous coding"]
        self.weight_map = {
            "vibecode": 2,
            "vibe": 1,
            "prompt-driven": 1,
            "agent workflow": 1,
            "autonomous coding": 1,
        }

    def analyze(self, text: str) -> Dict:
        normalized = (text or "").lower()
        matched = [keyword for keyword in self.keywords if keyword in normalized]
        score = sum(self.weight_map.get(keyword, 1) for keyword in matched)
        severity = self._severity(score)
        return {
            "is_vibecode": score >= 2 or "vibecode" in normalized,
            "score": score,
            "severity": severity,
            "matched_keywords": matched,
            "summary": self._summary(matched),
        }

    def scan_paths(self, paths: List[str]) -> Dict:
        files = []
        combined_score = 0
        matched_keywords: List[str] = []
        for raw_path in paths:
            path = Path(raw_path)
            if not path.exists():
                continue
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                result = self.analyze(text)
                if result["score"]:
                    files.append({"name": path.name, "score": result["score"], "keywords": result["matched_keywords"]})
                    combined_score += result["score"]
                    matched_keywords.extend(result["matched_keywords"])
        return {
            "is_vibecode": combined_score >= 2,
            "score": combined_score,
            "severity": self._severity(combined_score),
            "matched_keywords": sorted(set(matched_keywords)),
            "files": files,
            "summary": self._summary(sorted(set(matched_keywords))),
        }

    def load_config(self, config_path: Path | None = None) -> Dict:
        target = config_path or Path(".specomega/vibecode_config.json")
        if not target.exists():
            return {}
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _severity(self, score: int) -> str:
        if score >= 6:
            return "high"
        if score >= 3:
            return "medium"
        if score >= 1:
            return "low"
        return "none"

    def _summary(self, matched: List[str]) -> str:
        if not matched:
            return "No Vibecode signals detected"
        return "Detected Vibecode-related signals: " + ", ".join(matched)
