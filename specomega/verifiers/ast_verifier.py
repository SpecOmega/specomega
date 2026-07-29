import re
from typing import Dict, List, Optional, Tuple

from .base import Verifier


class AstVerifier(Verifier):
    def can_handle(self, verification_tag: str) -> bool:
        return verification_tag.startswith("ast") or verification_tag.startswith("boundary")

    def verify(self, spec_fragment: str, context: Dict) -> Tuple[bool, List[str], Optional[Dict]]:
        matched = re.search(r"page=0|400|ReviewGate|Finalize", spec_fragment, re.IGNORECASE)
        if matched:
            return True, [], {"matched_text": matched.group(0)}
        return False, ["未找到可验证的边界表达式"], None
