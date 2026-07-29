import re
from typing import Dict, List, Optional, Tuple

from .base import Verifier


class TraceVerifier(Verifier):
    def can_handle(self, verification_tag: str) -> bool:
        return "trace_check" in verification_tag

    def verify(self, spec_fragment: str, context: Dict) -> Tuple[bool, List[str], Optional[Dict]]:
        required_gates = self._parse_gates(spec_fragment)
        actual_gates = ["ReviewGate", "Finalize"]
        failures = []
        for gate in required_gates:
            if gate not in actual_gates:
                failures.append(f"缺失关键门禁: {gate}")
        return len(failures) == 0, failures, {"required": required_gates, "actual": actual_gates}

    def _parse_gates(self, spec_fragment: str) -> List[str]:
        match = re.search(r"trace_check\(([^)]+)\)", spec_fragment)
        return [item.strip() for item in match.group(1).split(",") if item.strip()] if match else []
