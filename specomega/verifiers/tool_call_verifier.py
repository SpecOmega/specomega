import re
from typing import Dict, List, Optional, Tuple

from .base import Verifier


class ToolCallVerifier(Verifier):
    def can_handle(self, verification_tag: str) -> bool:
        return "tool_call_sequence" in verification_tag

    def verify(self, spec_fragment: str, context: Dict) -> Tuple[bool, List[str], Optional[Dict]]:
        match = re.search(r"tool_call_sequence\(([^)]+)\)", spec_fragment)
        if not match:
            return False, ["缺少工具调用序列声明"], None

        expected = [item.strip() for item in match.group(1).split("→") if item.strip()]
        actual = context.get("agent_trace", {}).get("tool_calls", [])
        if not actual:
            return False, ["缺少 Agent 运行日志中的工具调用记录"], None

        if expected and actual[:len(expected)] == expected:
            return True, [], {"expected": expected, "actual": actual}

        return False, [f"工具调用序列不匹配: expected={expected}, actual={actual}"], {"expected": expected, "actual": actual}
