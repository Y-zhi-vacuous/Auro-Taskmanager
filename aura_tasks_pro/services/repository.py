import sqlite3
from datetime import date, datetime
from typing import Optional, List
from ..models.task import Task
from ..models.workspace import Workspace
from ..utils.path_utils import get_db_path


class TaskRepository:
    """数据访问层：SQLite 任务 + 工作区 CRUD。"""

    CREATE_TASKS_TABLE = """
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
        workspace_id INTEGER DEFAULT NULL,
        FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE
    );
    """

    CREATE_WORKSPACES_TABLE = """
    CREATE TABLE IF NOT EXISTS workspaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL DEFAULT '默认工作区',
        order_index INTEGER DEFAULT 0
    );
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_db_path()
        self._conn: Optional[sqlite3.Connection] = None
        self._ensure_db()
        self._migrate()
        self._ensure_default_workspace()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _ensure_db(self):
        with sqlite3.connect(self.db_path) as c:
            c.execute("PRAGMA foreign_keys = ON")
            c.execute(self.CREATE_WORKSPACES_TABLE)
            c.execute(self.CREATE_TASKS_TABLE)

    def _migrate(self):
        """向后兼容：为旧数据库添加 workspaces 表和 workspace_id 列。"""
        cursor = self.conn.execute("PRAGMA table_info(tasks)")
        cols = {r["name"] for r in cursor.fetchall()}
        if "workspace_id" not in cols:
            self.conn.execute("ALTER TABLE tasks ADD COLUMN workspace_id INTEGER DEFAULT NULL")
            self.conn.commit()

    def _ensure_default_workspace(self):
        count = self.conn.execute("SELECT COUNT(*) FROM workspaces").fetchone()[0]
        if count == 0:
            self.conn.execute(
                "INSERT INTO workspaces (name, order_index) VALUES (?, ?)",
                ("默认工作区", 0),
            )
            self.conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    # ─── Task <-> Row ────────────────────────────────────

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
            workspace_id=row["workspace_id"],
        )

    # ─── Workspace CRUD ─────────────────────────────────

    def get_all_workspaces(self) -> List[Workspace]:
        rows = self.conn.execute("SELECT * FROM workspaces ORDER BY order_index, id").fetchall()
        return [Workspace(id=r["id"], name=r["name"], order_index=r["order_index"]) for r in rows]

    def create_workspace(self, name: str) -> int:
        max_order = self.conn.execute(
            "SELECT COALESCE(MAX(order_index), -1) FROM workspaces"
        ).fetchone()[0]
        cursor = self.conn.execute(
            "INSERT INTO workspaces (name, order_index) VALUES (?, ?)",
            (name, max_order + 1),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_workspace(self, ws: Workspace):
        self.conn.execute(
            "UPDATE workspaces SET name=?, order_index=? WHERE id=?",
            (ws.name, ws.order_index, ws.id),
        )
        self.conn.commit()

    def delete_workspace(self, ws_id: int):
        self.conn.execute("DELETE FROM tasks WHERE workspace_id=?", (ws_id,))
        self.conn.execute("DELETE FROM workspaces WHERE id=?", (ws_id,))
        self.conn.commit()

    def reorder_workspaces(self, ordered_ids: List[int]):
        for idx, wid in enumerate(ordered_ids):
            self.conn.execute(
                "UPDATE workspaces SET order_index=? WHERE id=?", (idx, wid)
            )
        self.conn.commit()

    # ─── Task CRUD (workspace-aware) ────────────────────

    def get_all_tasks(self, workspace_id: Optional[int] = None) -> List[Task]:
        if workspace_id is not None:
            cursor = self.conn.execute(
                "SELECT * FROM tasks WHERE workspace_id=? ORDER BY order_index, id",
                (workspace_id,),
            )
        else:
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
               start_date, due_date, risk, remarks, order_index, workspace_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.parent_id, task.name, task.progress, task.status,
                task.priority,
                task.start_date.isoformat() if task.start_date else None,
                task.due_date.isoformat() if task.due_date else None,
                task.risk, task.remarks, task.order_index, task.workspace_id,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_task(self, task: Task):
        self.conn.execute(
            """UPDATE tasks SET name=?, progress=?, status=?, priority=?,
               start_date=?, due_date=?, risk=?, remarks=?, order_index=?,
               workspace_id=?
               WHERE id=?""",
            (
                task.name, task.progress, task.status, task.priority,
                task.start_date.isoformat() if task.start_date else None,
                task.due_date.isoformat() if task.due_date else None,
                task.risk, task.remarks, task.order_index, task.workspace_id,
                task.id,
            ),
        )
        self.conn.commit()

    def delete_task(self, task_id: int):
        self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def update_order(self, task_id: int, order_index: int):
        self.conn.execute(
            "UPDATE tasks SET order_index = ? WHERE id = ?", (order_index, task_id)
        )
        self.conn.commit()

    def reorder_siblings(self, parent_id: Optional[int], ordered_ids: List[int]):
        for idx, tid in enumerate(ordered_ids):
            self.update_order(tid, idx)
