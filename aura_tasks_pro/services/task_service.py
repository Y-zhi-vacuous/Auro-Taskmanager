from datetime import date
from typing import Optional, List
from ..models.task import Task
from ..utils.enums import TaskStatus, Priority
from .repository import TaskRepository


class TaskService:
    """业务逻辑层：封装排序算法、递归进度计算和状态管理。"""

    RISK_WEIGHTS = {"高": 5, "严重": 8, "紧急": 10, "critical": 10, "high": 5}

    def __init__(self, repo: Optional[TaskRepository] = None):
        self.repo = repo or TaskRepository()

    def close(self):
        self.repo.close()

    def get_task_tree(self) -> List[Task]:
        return self.repo.get_all_tasks()

    def add_task(self, task: Task) -> int:
        return self.repo.create_task(task)

    def update_task(self, task: Task):
        self.repo.update_task(task)

    def delete_task(self, task_id: int):
        self.repo.delete_task(task_id)

    def reorder_siblings(self, parent_id: Optional[int], ordered_ids: List[int]):
        self.repo.reorder_siblings(parent_id, ordered_ids)

    def calculate_progress(self, task: Task) -> int:
        """递归计算加权平均进度。
        若任务自身设置了 progress 且无子任务，直接返回；
        否则按子任务的 progress 加权平均计算。
        """
        if not task.children:
            return task.progress
        total_weight = 0
        weighted_sum = 0.0
        for child in task.children:
            child_prog = self.calculate_progress(child)
            weight = max(child.priority, 1)
            weighted_sum += child_prog * weight
            total_weight += weight
        if total_weight == 0:
            return 0
        return int(weighted_sum / total_weight)

    def compute_score(self, task: Task) -> float:
        """复合权重排序算法: Score = (Priority × 10) - DaysToDeadline + RiskWeight"""
        days_to_deadline = 0
        if task.due_date:
            delta = (task.due_date - date.today()).days
            days_to_deadline = delta
        risk_weight = 0
        for keyword, weight in self.RISK_WEIGHTS.items():
            if keyword in task.risk.lower():
                risk_weight = max(risk_weight, weight)
        return (task.priority * 10) - days_to_deadline + risk_weight

    def sort_by_score(self, tasks: List[Task]) -> List[Task]:
        """按复合权重分数自动排序（降序，分数越高越靠前）。"""
        return sorted(tasks, key=lambda t: self.compute_score(t), reverse=True)

    def mark_status(self, task_id: int, status: str):
        task = self.repo.get_task_by_id(task_id)
        if task:
            task.status = status
            if status == TaskStatus.DONE.value:
                task.progress = 100
            self.repo.update_task(task)

    def increase_priority(self, task_id: int):
        task = self.repo.get_task_by_id(task_id)
        if task and task.priority < Priority.CRITICAL.value:
            task.priority += 1
            self.repo.update_task(task)

    def decrease_priority(self, task_id: int):
        task = self.repo.get_task_by_id(task_id)
        if task and task.priority > Priority.VERY_LOW.value:
            task.priority -= 1
            self.repo.update_task(task)

    def _flatten_tasks(self, tasks: List['Task'], ancestors: List[str] = None) -> List[dict]:
        if ancestors is None:
            ancestors = []
        result = []
        for task in tasks:
            path = ancestors + [task.name]
            score = self.compute_score(task)
            result.append({
                "task": task,
                "path": " → ".join(path),
                "score": score,
            })
            if task.children:
                result.extend(self._flatten_tasks(task.children, path))
        return result

    def get_top3(self) -> List[dict]:
        tasks = self.repo.get_all_tasks()
        flat = self._flatten_tasks(tasks)
        flat.sort(key=lambda x: x["score"], reverse=True)
        return flat[:3]
