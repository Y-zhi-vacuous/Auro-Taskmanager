from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Workspace:
    id: Optional[int] = None
    name: str = "默认工作区"
    order_index: int = 0
