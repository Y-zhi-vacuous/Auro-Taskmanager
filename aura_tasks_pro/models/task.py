from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List
from ..utils.enums import TaskStatus, Priority


@dataclass
class Task:
    id: Optional[int] = None
    parent_id: Optional[int] = None
    name: str = ""
    progress: int = 0
    status: str = TaskStatus.TODO.value
    priority: int = Priority.MEDIUM.value
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    risk: str = ""
    remarks: str = ""
    order_index: int = 0
    workspace_id: Optional[int] = None
    children: List['Task'] = field(default_factory=list)

    @property
    def depth(self) -> int:
        if self.parent_id is None:
            return 0
        return 1

    @property
    def is_high_risk(self) -> bool:
        keywords = ["高", "严重", "紧急", "critical", "high"]
        return any(kw in self.risk.lower() for kw in keywords)

    @property
    def priority_color(self) -> str:
        try:
            return Priority(self.priority).color
        except ValueError:
            return "#2196F3"

    @property
    def priority_label(self) -> str:
        try:
            return Priority(self.priority).label
        except ValueError:
            return "中"
