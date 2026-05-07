import sqlite3
from datetime import date, datetime
from typing import Optional, List
from ..models.task import Task
from ..utils.path_utils import get_db_path


class TaskRepository:
    """数据访问层：封装所有 SQLite 数据库操作，使用邻接表模型实现自关联分级。"""

    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER,
        name TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        status TEXT DEFAULT '待办',
        priority INTEGER DEFAULT 3,
        start_date DATE,
        due_date DATE,
        risk TEXT DEFAULT '',
        remarks TEXT DEFAULT '',
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE
    );
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_db_path()
        self._conn: Optional[sqlite3.Connection] = None
        self._ensure_db()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _ensure_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute(self.CREATE_TABLE_SQL)

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            parent_id=row["parent_id"],
            name=row["name"],
            progress=row["progress"] or 0,
            status=row["status"] or "待办",
            priority=row["priority"] or 3,
            start_date=date.fromisoformat(row["start_date"]) if row["start_date"] else None,
            due_date=date.fromisoformat(row["due_date"]) if row["due_date"] else None,
            risk=row["risk"] or "",
            remarks=row["remarks"] or "",
            order_index=row["order_index"] or 0,
        )

    def get_all_tasks(self) -> List[Task]:
        cursor = self.conn.execute("SELECT * FROM tasks ORDER BY order_index, id")
        rows = cursor.fetchall()
        task_map = {}
        roots = []
        for row in rows:
            t = self._row_to_task(row)
            task_map[t.id] = t
        for t in task_map.values():
            if t.parent_id and t.parent_id in task_map:
                task_map[t.parent_id].children.append(t)
            else:
                roots.append(t)
        return roots

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        cursor = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return self._row_to_task(row) if row else None

    def get_children(self, parent_id: int) -> List[Task]:
        cursor = self.conn.execute(
            "SELECT * FROM tasks WHERE parent_id = ? ORDER BY order_index, id",
            (parent_id,),
        )
        return [self._row_to_task(r) for r in cursor.fetchall()]

    def get_max_depth(self, task_id: int) -> int:
        """递归计算指定任务的最大嵌套深度。"""
        children = self.get_children(task_id)
        if not children:
            return 0
        return 1 + max(self.get_max_depth(c.id) for c in children)

    def create_task(self, task: Task) -> int:
        if task.parent_id is not None:
            current_depth = self.get_max_depth(task.parent_id)
            if current_depth >= 2:
                raise ValueError("已达到最大嵌套深度（三级），无法再添加子任务")

        cursor = self.conn.execute(
            """INSERT INTO tasks (parent_id, name, progress, status, priority,
               start_date, due_date, risk, remarks, order_index)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.parent_id,
                task.name,
                task.progress,
                task.status,
                task.priority,
                task.start_date.isoformat() if task.start_date else None,
                task.due_date.isoformat() if task.due_date else None,
                task.risk,
                task.remarks,
                task.order_index,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_task(self, task: Task):
        self.conn.execute(
            """UPDATE tasks SET name=?, progress=?, status=?, priority=?,
               start_date=?, due_date=?, risk=?, remarks=?, order_index=?
               WHERE id=?""",
            (
                task.name,
                task.progress,
                task.status,
                task.priority,
                task.start_date.isoformat() if task.start_date else None,
                task.due_date.isoformat() if task.due_date else None,
                task.risk,
                task.remarks,
                task.order_index,
                task.id,
            ),
        )
        self.conn.commit()

    def delete_task(self, task_id: int):
        self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def update_order(self, task_id: int, order_index: int):
        self.conn.execute(
            "UPDATE tasks SET order_index = ? WHERE id = ?",
            (order_index, task_id),
        )
        self.conn.commit()

    def reorder_siblings(self, parent_id: Optional[int], ordered_ids: List[int]):
        for idx, tid in enumerate(ordered_ids):
            self.update_order(tid, idx)
