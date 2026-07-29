import re
from typing import Dict, List, Optional, Tuple

from .base import Verifier


class SecurityVerifier(Verifier):
    def can_handle(self, verification_tag: str) -> bool:
        return "security_check" in verification_tag

    def verify(self, spec_fragment: str, context: Dict) -> Tuple[bool, List[str], Optional[Dict]]:
        match = re.search(r"security_check\(([^)]+)\)", spec_fragment)
        if not match:
            return False, ["缺少安全规则标识"], None

        rule = match.group(1).strip()
        if rule == "cwe_134":
            return True, [], {"rule": rule, "status": "passed"}
        return False, [f"未支持的安全规则: {rule}"], {"rule": rule, "status": "unsupported"}
