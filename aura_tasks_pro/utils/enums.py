from enum import Enum


class TaskStatus(str, Enum):
    TODO = "待办"
    IN_PROGRESS = "进行中"
    DONE = "已完成"
    SUSPENDED = "已挂起"

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class Priority(int, Enum):
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5

    @classmethod
    def values(cls):
        return [e.value for e in cls]

    @classmethod
    def labels(cls):
        return ["极低", "低", "中", "高", "紧急"]

    @property
    def label(self) -> str:
        return self.labels()[self.value - 1]

    @property
    def color(self) -> str:
        colors = ["#607D8B", "#4CAF50", "#2196F3", "#FF9800", "#F44336"]
        return colors[self.value - 1]
