import re
from typing import Dict, List, Optional, Tuple

from .base import Verifier
from ..analysis.vibecode import VibecodeAnalyzer


class VibecodeVerifier(Verifier):
    def can_handle(self, verification_tag: str) -> bool:
        return "vibecode_check" in verification_tag

    def verify(self, spec_fragment: str, context: Dict) -> Tuple[bool, List[str], Optional[Dict]]:
        match = re.search(r"vibecode_check\(([^)]+)\)", spec_fragment)
        if not match:
            return False, ["缺少 Vibecode 检查声明"], None

        params = {}
        for item in match.group(1).split(","):
            if "=" in item:
                key, value = item.split("=", 1)
                params[key.strip()] = value.strip()

        threshold = int(params.get("threshold", "0"))
        analyzer = VibecodeAnalyzer()
        analysis = analyzer.analyze(spec_fragment)
        passed = analysis["score"] >= threshold
        failures = [] if passed else [f"Vibecode 信号过弱: score={analysis['score']}, threshold={threshold}"]
        return passed, failures, {"analysis": analysis, "threshold": threshold}
