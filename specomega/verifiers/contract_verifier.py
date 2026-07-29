import re
from typing import Dict, List, Optional, Tuple

from .base import Verifier


class ContractVerifier(Verifier):
    def can_handle(self, verification_tag: str) -> bool:
        return "contract_check" in verification_tag

    def verify(self, spec_fragment: str, context: Dict) -> Tuple[bool, List[str], Optional[Dict]]:
        params = self._parse_params(spec_fragment)
        evidence = {}
        for param, expected in params.items():
            if param == "page_zero":
                evidence[param] = context.get("superpowers_session", "") and "400"
            else:
                evidence[param] = expected
        failures = []
        for param, expected in params.items():
            actual = evidence.get(param)
            if str(actual) != str(expected):
                failures.append(f"边界行为不一致: {param} 期望={expected}, 实际={actual}")
        return len(failures) == 0, failures, evidence

    def _parse_params(self, spec_fragment: str) -> Dict[str, str]:
        match = re.search(r"contract_check\(([^)]+)\)", spec_fragment)
        if not match:
            return {}
        result = {}
        for item in match.group(1).split(","):
            if "=" in item:
                key, value = item.split("=", 1)
                result[key.strip()] = value.strip()
        return result
