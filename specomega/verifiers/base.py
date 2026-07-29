from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class Verifier(ABC):
    """所有验证器必须实现的接口。"""

    @abstractmethod
    def can_handle(self, verification_tag: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def verify(
        self,
        spec_fragment: str,
        context: Dict,
    ) -> Tuple[bool, List[str], Optional[Dict]]:
        raise NotImplementedError
