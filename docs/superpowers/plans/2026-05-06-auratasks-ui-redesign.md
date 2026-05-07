# AuraTasks Pro UI 重构 + 功能增强 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 AuraTasks Pro 重构为 Glassmorphism + Bento Grid 风格，增加树内直接编辑、拖拽排序、TOP3 关键任务面板。

**Architecture:** 保留 MVC 分层，主要改动集中在 `views/main_window.py`（新布局 + 内联编辑 + 拖拽 + TOP3）、`apple_theme.py`（新 Glass/Bento 样式常量）、`task_service.py`（新增 `get_top3()` 方法）、`task_delegates.py`（点击式进度条）。

**Tech Stack:** PyQt6 + PyQt6-Fluent-Widgets, SQLite3

**测试说明:** 本项目无自动化测试框架，验证步骤通过启动应用手动检查。

---

### Task 1: 更新 AppleTheme 样式常量

**Files:**
- Modify: `aura_tasks_pro/utils/apple_theme.py`

- [ ] **Step 1: 添加 Glass/Bento/TOP3 卡片样式常量**

在 `AppleTheme` 类末尾（最后一个赋值之后）追加以下内容：

```python
    # ─── Glassmorphism 卡片 ────────────────────────────
    GLASS_BG = "rgba(35, 33, 36, 180)"
    GLASS_BG_LIGHT = "rgba(45, 42, 46, 160)"
    GLASS_BG_DARK = "rgba(25, 23, 26, 200)"
    GLASS_BORDER = "rgba(166, 226, 42, 30)"
    GLASS_BORDER_SUBTLE = "rgba(255, 255, 255, 8)"
    GLASS_BLUR = 20  # backdrop-filter blur px
    GLASS_SHADOW = "0 8px 32px rgba(0, 0, 0, 100)"

    # ─── Bento Grid 卡片 ───────────────────────────────
    RADIUS_BENTO = 12
    RADIUS_BENTO_INNER = 8
    BENTO_PADDING = 16
    BENTO_GAP = 12

    # ─── TOP3 面板 ─────────────────────────────────────
    TOP1_BG = "rgba(166, 226, 42, 15)"
    TOP1_BORDER = "rgba(166, 226, 42, 50)"
    TOP2_BG = "rgba(120, 220, 232, 10)"
    TOP2_BORDER = "rgba(120, 220, 232, 35)"
    TOP3_BG = "rgba(252, 152, 103, 8)"
    TOP3_BORDER = "rgba(252, 152, 103, 25)"
    DANGER_BG = "rgba(255, 97, 136, 15)"
    DANGER_BORDER = "rgba(255, 97, 136, 40)"
```

- [ ] **Step 2: 验证文件语法**

```bash
python -c "from aura_tasks_pro.utils.apple_theme import AppleTheme; print(AppleTheme.GLASS_BG)"
```

预期输出: `rgba(35, 33, 36, 180)`

---

### Task 2: TaskService 新增 get_top3() 方法

**Files:**
- Modify: `aura_tasks_pro/services/task_service.py`

- [ ] **Step 1: 在 TaskService 类中添加 get_top3() 方法**

在 `decrease_priority` 方法之后（类闭合 `# END class` 之前）插入：

```python
    def _flatten_tasks(self, tasks: List['Task'], ancestors: List[str] = None) -> List[dict]:
        """将树形任务展平为带祖先路径的列表。"""
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
        """获取综合得分最高的 3 个任务（含完整路径）。"""
        tasks = self.repo.get_all_tasks()
        flat = self._flatten_tasks(tasks)
        flat.sort(key=lambda x: x["score"], reverse=True)
        return flat[:3]
```

在文件顶部 import 区域，`from typing import Optional, List` 保持不变（`List` 已在用）。

- [ ] **Step 2: 添加类型引用**

确认 `get_top3` 方法中 `'Task'` 的前向引用字符串形式可用，因为 `from ..models.task import Task` 已在文件顶部。

- [ ] **Step 3: 验证导入和语法**

```bash
python -c "from aura_tasks_pro.services.task_service import TaskService; s = TaskService(); print(s.get_top3())"
```

预期输出: `[]`（空数据库，返回空列表）

---

### Task 3: 增强 ProgressBarDelegate 支持点击设置进度

**Files:**
- Modify: `aura_tasks_pro/delegates/task_delegates.py`

- [ ] **Step 1: 重写 ProgressBarDelegate 添加鼠标点击处理**

用以下完整代码替换 `ProgressBarDelegate` 类：

```python
class ProgressBarDelegate(QStyledItemDelegate):
    """可点击设置进度的 Monokai Pro 风格进度条委托。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tree: Optional['QTreeWidget'] = None

    def set_tree(self, tree: 'QTreeWidget'):
        self._tree = tree

    def paint(self, painter: QPainter, option, index: QModelIndex):
        value = index.data(Qt.ItemDataRole.DisplayRole)
        if value is None:
            super().paint(painter, option, index)
            return
        try:
            progress = int(value)
        except (TypeError, ValueError):
            super().paint(painter, option, index)
            return
        progress = max(0, min(100, progress))

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = option.rect
        bar_height = 18
        bar_y = rect.y() + (rect.height() - bar_height) // 2
        bar_rect = rect.adjusted(6, bar_y - rect.y(), -6, rect.bottom() - bar_y - bar_height)

        # 轨道
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(64, 62, 65, 200))
        painter.drawRoundedRect(bar_rect, 4, 4)

        if progress > 0:
            fill_width = int(bar_rect.width() * progress / 100)
            fill_rect = bar_rect.adjusted(0, 0, -(bar_rect.width() - fill_width), 0)
            if progress < 30:
                color = QColor(AppleTheme.CYAN)
            elif progress < 70:
                color = QColor(AppleTheme.ACCENT)
            else:
                color = QColor(AppleTheme.ORANGE)
            painter.setBrush(color)
            painter.drawRoundedRect(fill_rect, 4, 4)
            if fill_width > 4:
                shine_rect = fill_rect.adjusted(0, 0, 0, -(fill_rect.height() // 2))
                painter.setBrush(QColor(255, 255, 255, 20))
                painter.drawRoundedRect(shine_rect, 4, 2)

        font = painter.font()
        font.setPixelSize(10)
        font.setWeight(600)
        painter.setFont(font)
        painter.setPen(QColor(AppleTheme.TEXT_PRIMARY))
        painter.drawText(bar_rect, Qt.AlignmentFlag.AlignCenter, f"{progress}%")

        painter.restore()

    def editorEvent(self, event, model, option, index):
        """点击进度条直接设置进度百分比。"""
        if event.type() == event.Type.MouseButtonPress:
            rect = option.rect
            bar_height = 18
            bar_y = rect.y() + (rect.height() - bar_height) // 2
            bar_rect = rect.adjusted(6, bar_y - rect.y(), -6, rect.bottom() - bar_y - bar_height)
            if bar_rect.contains(event.pos()):
                click_x = event.pos().x() - bar_rect.x()
                new_progress = int(click_x / bar_rect.width() * 100)
                new_progress = max(0, min(100, new_progress))
                model.setData(index, new_progress, Qt.ItemDataRole.DisplayRole)
                if self._tree:
                    self._tree.itemDelegateProgressChanged.emit(index, new_progress)
                return True
        return super().editorEvent(event, model, option, index)
```

同时在文件顶部的 import 添加：
```python
from typing import Optional
```
（在现有 `from PyQt6.QtCore import QModelIndex, Qt` 之后追加 `, pyqtSignal`）

- [ ] **Step 2: 验证语法**

```bash
python -c "from aura_tasks_pro.delegates.task_delegates import ProgressBarDelegate; print('OK')"
```

---

### Task 4: 创建自定义 DragDropTreeWidget

**Files:**
- Create: `aura_tasks_pro/views/drag_tree.py`

- [ ] **Step 1: 创建支持限层级拖拽的树组件**

```python
"""限同层级拖拽排序的 QTreeWidget 子类。"""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt, pyqtSignal, QModelIndex
from PyQt6.QtGui import QDrag, QPainter, QColor, QPen
from typing import Optional


class DragDropTreeWidget(QTreeWidget):
    """QTreeWidget 子类：仅允许同层级拖拽排序。"""

    itemDelegateProgressChanged = pyqtSignal(QModelIndex, int)
    orderChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropOverwriteMode(False)
        self._drag_item_parent_id: Optional[int] = None

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            # 记录被拖拽项的 parent_id
            self._drag_item_parent_id = item.data(0, Qt.ItemDataRole.UserRole + 100)
        super().startDrag(supportedActions)

    def dropEvent(self, event):
        dragged = self.currentItem()
        if not dragged:
            event.ignore()
            return
        target = self.itemAt(event.position().toPoint())
        if not target:
            # 拖到空白区域 = 移动到末尾
            dragged_parent = dragged.data(0, Qt.ItemDataRole.UserRole + 100)
            # 验证 target 区域是否属于同一父级
            super().dropEvent(event)
            self._emit_order_changed()
            return

        target_parent = target.data(0, Qt.ItemDataRole.UserRole + 100)
        # 记录目标 item 的父级
        dragged_parent = dragged.data(0, Qt.ItemDataRole.UserRole + 100)

        # 只允许同父级间拖拽
        if dragged_parent != target_parent:
            event.ignore()
            return

        # 不允许拖到子项上（会破坏结构）
        if self._is_descendant(dragged, target):
            event.ignore()
            return

        super().dropEvent(event)
        self._emit_order_changed()

    def _is_descendant(self, ancestor: QTreeWidgetItem, target: QTreeWidgetItem) -> bool:
        """检查 target 是否是 ancestor 的后代。"""
        item = target
        while item:
            if item == ancestor:
                return True
            item = item.parent()
        return False

    def _emit_order_changed(self):
        """拖拽完成后触发信号。"""
        self.orderChanged.emit()
```

将 `parent_id` 存入 UserRole+100：在 `MainWindow._create_item()` 中设置：
```python
item.setData(0, Qt.ItemDataRole.UserRole + 100, task.parent_id)
```

- [ ] **Step 2: 验证语法**

```bash
python -c "from aura_tasks_pro.views.drag_tree import DragDropTreeWidget; print('OK')"
```

---

### Task 5: 创建 TOP3 面板组件

**Files:**
- Create: `aura_tasks_pro/views/top3_panel.py`

- [ ] **Step 1: 创建 TOP3 面板类**

```python
"""TOP3 关键任务高亮面板。"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont
from ..utils.apple_theme import AppleTheme
from typing import List


class Top3Panel(QWidget):
    """Glass Card 风格 TOP3 面板。"""

    taskClicked = pyqtSignal(int)  # 发射 task_id，用于定位到树中

    RANK_ICONS = {0: "🥇", 1: "🥈", 2: "🥉"}
    RANK_COLORS = {
        0: (AppleTheme.TOP1_BG, AppleTheme.TOP1_BORDER, AppleTheme.ACCENT),
        1: (AppleTheme.TOP2_BG, AppleTheme.TOP2_BORDER, AppleTheme.CYAN),
        2: (AppleTheme.TOP3_BG, AppleTheme.TOP3_BORDER, AppleTheme.ORANGE),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("top3Panel")
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(8)

        # 标题
        title = QLabel("🔴 关键任务 TOP3")
        title.setStyleSheet(f"""
            font-size: {AppleTheme.FONT_SIZE_SUBTITLE}px;
            font-weight: 700;
            color: {AppleTheme.ACCENT};
            padding: 0 4px;
        """)
        self.main_layout.addWidget(title)

        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(12)
        self.main_layout.addLayout(self.cards_layout)

        self.cards = []
        for i in range(3):
            card = self._create_card(i)
            self.cards.append(card)
            self.cards_layout.addWidget(card, 1)

    def _create_card(self, rank: int) -> QWidget:
        bg, border, accent = self.RANK_COLORS[rank]
        card = QWidget()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QWidget {{
                background: {bg};
                border: 1px solid {border};
                border-radius: {AppleTheme.RADIUS_BENTO_INNER}px;
                padding: 10px 14px;
            }}
            QWidget:hover {{
                background: rgba(166, 226, 42, 8);
                border-color: rgba(166, 226, 42, 45);
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        icon_label = QLabel(self.RANK_ICONS[rank])
        icon_label.setStyleSheet(f"font-size: 16px; background: transparent; border: none;")
        layout.addWidget(icon_label)

        path_label = QLabel("—")
        path_label.setObjectName(f"path_{rank}")
        path_label.setWordWrap(True)
        path_label.setStyleSheet(f"""
            font-size: {AppleTheme.FONT_SIZE_SMALL}px;
            font-weight: 600;
            color: {AppleTheme.TEXT_PRIMARY};
            background: transparent;
            border: none;
        """)
        layout.addWidget(path_label)

        meta_label = QLabel("")
        meta_label.setObjectName(f"meta_{rank}")
        meta_label.setStyleSheet(f"""
            font-size: {AppleTheme.FONT_SIZE_SMALL - 1}px;
            color: {AppleTheme.TEXT_SECONDARY};
            background: transparent;
            border: none;
        """)
        layout.addWidget(meta_label)

        return card

    def update_top3(self, top_data: List[dict]):
        """top_data: TaskService.get_top3() 返回的列表，每项 {task, path, score}"""
        from datetime import date

        for i, card in enumerate(self.cards):
            path_label = card.findChild(QLabel, f"path_{i}")
            meta_label = card.findChild(QLabel, f"meta_{i}")
            icon_label = card.layout().itemAt(0).widget()

            if i < len(top_data):
                item = top_data[i]
                t = item["task"]
                path_label.setText(item["path"])
                days = (t.due_date - date.today()).days if t.due_date else None
                risk_text = f"风险:{t.risk}" if t.risk else "无风险标记"
                if days is not None:
                    if days < 0:
                        deadline_text = f" | ⚠已逾期{-days}天"
                    elif days == 0:
                        deadline_text = " | ⚠今日截止"
                    else:
                        deadline_text = f" | 剩余{days}天"
                else:
                    deadline_text = " | 无截止"
                meta_label.setText(f"{risk_text}{deadline_text}")

                # 存储 task_id 用于点击
                card.setProperty("task_id", t.id)
                card.mousePressEvent = lambda e, tid=t.id: self.taskClicked.emit(tid)
                card.setVisible(True)
                icon_label.setVisible(True)
            else:
                card.setVisible(False)
                icon_label.setVisible(False)

    def clear(self):
        for card in self.cards:
            card.setVisible(False)
```

- [ ] **Step 2: 验证语法**

```bash
python -c "from aura_tasks_pro.views.top3_panel import Top3Panel; print('OK')"
```

---

### Task 6: 重写 MainWindow — 新布局 + 内联编辑 + 拖拽 + TOP3 集成

这是核心任务。由于 `main_window.py` 需要大幅重写，以下步骤逐步构建新的 MainWindow。

**Files:**
- Modify: `aura_tasks_pro/views/main_window.py`

- [ ] **Step 1: 更新 import 区域**

将文件顶部现有 import 替换为：

```python
import traceback
from datetime import date
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QHeaderView,
    QFileDialog, QMenu, QMessageBox, QLabel,
    QComboBox, QLineEdit, QFrame, QApplication,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon,
    PushButton, PrimaryPushButton, SearchLineEdit,
    ComboBox, InfoBar, InfoBarPosition, TitleLabel, BodyLabel,
    CaptionLabel, setTheme, Theme,
)

from ..models.task import Task
from ..services.task_service import TaskService
from ..services.repository import TaskRepository
from ..services.export_import import export_xlsx, import_xlsx, export_pdf
from ..delegates.task_delegates import ProgressBarDelegate, RiskIconDelegate
from ..utils.enums import TaskStatus, Priority
from ..utils.apple_theme import AppleTheme
from ..utils.blur_effect import enable_acrylic
from .edit_dialog import TaskEditDialog
from .drag_tree import DragDropTreeWidget
from .top3_panel import Top3Panel
```

- [ ] **Step 2: 更新 QSS 样式常量**

将现有的 `COLUMNS` 和 `DARK_QSS` 替换为增强版：

```python
COLUMNS = ["任务名称", "进度", "状态", "优先级", "开始日期", "截止日期", "风险", "备注"]

GLASS_CARD_QSS = f"""
    background: {AppleTheme.GLASS_BG};
    border: 1px solid {AppleTheme.GLASS_BORDER_SUBTLE};
    border-radius: {AppleTheme.RADIUS_BENTO}px;
"""

GLASS_CARD_ACCENT_QSS = f"""
    background: {AppleTheme.GLASS_BG};
    border: 1px solid {AppleTheme.GLASS_BORDER};
    border-radius: {AppleTheme.RADIUS_BENTO}px;
"""

DARK_QSS = f"""
QWidget {{
    font-family: {AppleTheme.FONT_FAMILY};
    font-size: {AppleTheme.FONT_SIZE_BODY}px;
    color: {AppleTheme.TEXT_PRIMARY};
}}

QMainWindow, FluentWindow {{
    background: {AppleTheme.WINDOW_BG};
}}

NavigationPanel {{
    background: rgba(30, 30, 30, 240);
    border-right: 1px solid rgba(255,255,255,6);
}}
NavigationTreeWidget {{
    background: transparent;
}}
NavigationTreeWidget::item {{
    border-radius: 4px;
    padding: 4px 8px;
    color: {AppleTheme.TEXT_SECONDARY};
}}
NavigationTreeWidget::item:selected {{
    background: rgba(166, 226, 42, 20);
    color: {AppleTheme.ACCENT};
}}
NavigationTreeWidget::item:hover {{
    background: rgba(255,255,255,8);
}}

QPushButton {{
    background: rgba(255,255,255,18);
    border: 1px solid rgba(255,255,255,12);
    border-radius: {AppleTheme.RADIUS_BUTTON}px;
    padding: 6px 14px;
    font-size: {AppleTheme.FONT_SIZE_BODY}px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QPushButton:hover {{
    background: rgba(255,255,255,28);
    border-color: rgba(166,226,42,80);
}}
QPushButton:pressed {{
    background: rgba(166,226,42,30);
}}

PrimaryPushButton {{
    background: {AppleTheme.ACCENT};
    border: none;
    border-radius: {AppleTheme.RADIUS_BUTTON}px;
    padding: 6px 14px;
    color: #2D2A2E;
    font-weight: 700;
}}
PrimaryPushButton:hover {{
    background: {AppleTheme.ACCENT_HOVER};
}}
PrimaryPushButton:pressed {{
    background: #8FD41E;
}}

SearchLineEdit {{
    background: rgba(64,62,65,180);
    border: 1px solid rgba(255,255,255,12);
    border-radius: {AppleTheme.RADIUS_INPUT}px;
    padding: 6px 12px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
SearchLineEdit:focus {{
    border-color: {AppleTheme.ACCENT};
    background: rgba(64,62,65,240);
}}

ComboBox {{
    background: rgba(64,62,65,180);
    border: 1px solid rgba(255,255,255,12);
    border-radius: {AppleTheme.RADIUS_INPUT}px;
    padding: 4px 10px;
    color: {AppleTheme.TEXT_PRIMARY};
    min-width: 100px;
}}
ComboBox:hover {{
    border-color: rgba(166,226,42,80);
}}
QComboBox QAbstractItemView {{
    background: #2D2A2E;
    border: 1px solid rgba(255,255,255,12);
    selection-background-color: rgba(166,226,42,30);
    color: {AppleTheme.TEXT_PRIMARY};
}}

QTreeWidget {{
    background: rgba(45, 42, 46, 220);
    alternate-background-color: rgba(50, 47, 51, 160);
    border: 1px solid rgba(255,255,255,8);
    border-radius: {AppleTheme.RADIUS_CARD}px;
    outline: none;
    font-size: {AppleTheme.FONT_SIZE_BODY}px;
    padding: 2px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QTreeWidget::item {{
    padding: 5px 4px;
    border-radius: 3px;
    border-bottom: 1px solid rgba(255,255,255,4);
}}
QTreeWidget::item:selected {{
    background: rgba(166,226,42,25);
    color: {AppleTheme.ACCENT};
}}
QTreeWidget::item:hover:!selected {{
    background: rgba(255,255,255,10);
}}
QTreeWidget::branch {{
    background: transparent;
}}

QHeaderView::section {{
    background: rgba(35,33,36,240);
    border: none;
    border-bottom: 2px solid {AppleTheme.ACCENT};
    padding: 8px 6px;
    font-weight: 700;
    font-size: {AppleTheme.FONT_SIZE_SMALL}px;
    color: {AppleTheme.ACCENT};
    letter-spacing: 0.8px;
}}

QMenu {{
    background: rgba(45,42,46,245);
    border: 1px solid rgba(166,226,42,30);
    border-radius: {AppleTheme.RADIUS_INPUT}px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 24px;
    border-radius: 3px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QMenu::item:selected {{
    background: rgba(166,226,42,25);
    color: {AppleTheme.ACCENT};
}}
QMenu::separator {{
    height: 1px;
    background: rgba(166,226,42,30);
    margin: 4px 8px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: rgba(166,226,42,60);
    border-radius: 2px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(166,226,42,120);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 5px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: rgba(166,226,42,60);
    border-radius: 2px;
    min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QMessageBox {{
    background: {AppleTheme.EDITOR_BG};
}}
QMessageBox QLabel {{
    color: {AppleTheme.TEXT_PRIMARY};
}}

/* 内联编辑控件 */
QComboBox {{
    background: rgba(64,62,65,200);
    border: 1px solid rgba(255,255,255,10);
    border-radius: 3px;
    padding: 2px 6px;
    font-size: {AppleTheme.FONT_SIZE_SMALL}px;
    color: {AppleTheme.TEXT_PRIMARY};
    min-width: 60px;
}}
QComboBox:hover {{
    border-color: {AppleTheme.ACCENT};
}}
QComboBox QAbstractItemView {{
    background: #2D2A2E;
    border: 1px solid {AppleTheme.ACCENT};
    selection-background-color: rgba(166,226,42,30);
    color: {AppleTheme.TEXT_PRIMARY};
}}
QComboBox::drop-down {{
    border: none;
    width: 16px;
}}

QLineEdit {{
    background: rgba(64,62,65,200);
    border: 1px solid rgba(255,255,255,10);
    border-radius: 3px;
    padding: 2px 6px;
    font-size: {AppleTheme.FONT_SIZE_SMALL}px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QLineEdit:hover {{
    border-color: {AppleTheme.ACCENT};
}}
QLineEdit:focus {{
    border-color: {AppleTheme.ACCENT};
    background: rgba(64,62,65,250);
}}
"""
```

- [ ] **Step 3: 完全重写 MainWindow 类的 `__init__` 和 `_setup_ui`**

删除现有的 `MainWindow` 类（保留文件头部 import 和常量），然后用以下代码替换：

```python
class MainWindow(FluentWindow):
    """AuraTasks Pro — Glassmorphism + Bento Grid 重构版。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AuraTasks Pro")
        self.setMinimumSize(QSize(1100, 720))
        self.resize(1350, 800)

        setTheme(Theme.DARK)
        self.setStyleSheet(DARK_QSS)

        self.service = TaskService()
        self.task_item_map: Dict[int, QTreeWidgetItem] = {}
        self.item_task_map: Dict[int, Task] = {}
        self._sort_mode = "auto"
        self._risk_timers: Dict[int, QTimer] = {}

        self._setup_ui()
        self._setup_delegates()
        self.refresh_tree()

    def showEvent(self, event):
        super().showEvent(event)
        enable_acrylic(self, gradient_color=0xCC1E1E1E)

    def _setup_ui(self):
        """构建 Glassmorphism + Bento 卡片布局。"""
        # ─── 主容器 ──────────────────────────────────────
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainInterface")
        self.main_widget.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 12, 16, 12)

        # ─── Glass 顶栏 ────────────────────────────────
        top_bar = self._make_glass_card()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)
        top_layout.setSpacing(12)

        app_icon = QLabel("✦")
        app_icon.setStyleSheet(f"font-size: 22px; color: {AppleTheme.ACCENT}; font-weight: bold; background: transparent; border: none;")
        top_layout.addWidget(app_icon)

        app_title = TitleLabel("AuraTasks Pro")
        app_title.setStyleSheet(f"font-size: {AppleTheme.FONT_SIZE_TITLE}px; font-weight: 700; color: {AppleTheme.TEXT_PRIMARY}; background: transparent; border: none;")
        top_layout.addWidget(app_title)
        top_layout.addStretch()

        self.search_edit = SearchLineEdit()
        self.search_edit.setPlaceholderText("搜索任务...")
        self.search_edit.setFixedWidth(260)
        self.search_edit.textChanged.connect(self._on_search)
        top_layout.addWidget(self.search_edit)

        sort_label = CaptionLabel("排序:")
        sort_label.setStyleSheet(f"color: {AppleTheme.TEXT_SECONDARY}; background: transparent; border: none;")
        top_layout.addWidget(sort_label)
        self.sort_combo = ComboBox()
        self.sort_combo.addItems(["自动排序", "按优先级", "按截止日期", "手动排序"])
        self.sort_combo.setCurrentIndex(0)
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        top_layout.addWidget(self.sort_combo)

        main_layout.addWidget(top_bar)

        # ─── 中部：左侧工具栏 + 树区域 ──────────────────
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(12)

        # 左侧 Bento 工具栏卡片
        sidebar = self._make_glass_card_accent()
        sidebar.setFixedWidth(130)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(8)

        self.add_btn = PrimaryPushButton("  新建任务")
        self.add_btn.setIcon(FluentIcon.ADD.icon())
        self.add_btn.clicked.connect(self._add_task)
        sidebar_layout.addWidget(self.add_btn)

        self.child_btn = PushButton("  子任务")
        self.child_btn.setIcon(FluentIcon.FOLDER_ADD.icon())
        self.child_btn.clicked.connect(self._add_child_task)
        sidebar_layout.addWidget(self.child_btn)

        self.edit_btn = PushButton("  编辑")
        self.edit_btn.setIcon(FluentIcon.EDIT.icon())
        self.edit_btn.clicked.connect(self._edit_selected)
        sidebar_layout.addWidget(self.edit_btn)

        self.del_btn = PushButton("  删除")
        self.del_btn.setIcon(FluentIcon.DELETE.icon())
        self.del_btn.clicked.connect(self._delete_selected)
        sidebar_layout.addWidget(self.del_btn)

        sidebar_layout.addSpacing(4)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {AppleTheme.GLASS_BORDER}; max-height: 1px; border: none;")
        sidebar_layout.addWidget(sep)
        sidebar_layout.addSpacing(4)

        self.export_xlsx_btn = PushButton("  导出 Excel")
        self.export_xlsx_btn.setIcon(FluentIcon.SHARE.icon())
        self.export_xlsx_btn.clicked.connect(self._export_xlsx)
        sidebar_layout.addWidget(self.export_xlsx_btn)

        self.export_pdf_btn = PushButton("  导出 PDF")
        self.export_pdf_btn.setIcon(FluentIcon.DOCUMENT.icon())
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        sidebar_layout.addWidget(self.export_pdf_btn)

        self.import_btn = PushButton("  导入 Excel")
        self.import_btn.setIcon(FluentIcon.DOWNLOAD.icon())
        self.import_btn.clicked.connect(self._import_xlsx)
        sidebar_layout.addWidget(self.import_btn)

        sidebar_layout.addStretch()
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color: {AppleTheme.ACCENT}; font-size: {AppleTheme.FONT_SIZE_SMALL}px; font-weight: 500; background: transparent; border: none;")
        sidebar_layout.addWidget(self.status_label)

        mid_layout.addWidget(sidebar)

        # 主区域：树卡片
        tree_card = self._make_glass_card()
        tree_card_layout = QVBoxLayout(tree_card)
        tree_card_layout.setContentsMargins(4, 4, 4, 4)

        self.tree = DragDropTreeWidget()
        self.tree.setHeaderLabels(COLUMNS)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(28)
        self.tree.setRootIsDecorated(True)
        self.tree.setAllColumnsShowFocus(False)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.itemDoubleClicked.connect(self._edit_selected)
        self.tree.orderChanged.connect(self._on_drag_finished)

        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 100)
        for col in range(2, len(COLUMNS)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        tree_card_layout.addWidget(self.tree)
        mid_layout.addWidget(tree_card, 1)

        main_layout.addLayout(mid_layout, 1)

        # ─── 底部：TOP3 面板 ────────────────────────────
        self.top3_panel = Top3Panel()
        top3_wrapper = self._make_glass_card_accent()
        top3_wrapper_layout = QVBoxLayout(top3_wrapper)
        top3_wrapper_layout.setContentsMargins(12, 12, 12, 12)
        top3_wrapper_layout.addWidget(self.top3_panel)
        self.top3_panel.taskClicked.connect(self._navigate_to_task)
        main_layout.addWidget(top3_wrapper)

        # FluentWindow 集成
        self.addSubInterface(
            self.main_widget, FluentIcon.HOME, "任务列表",
            NavigationItemPosition.TOP
        )

    def _make_glass_card(self) -> QWidget:
        """创建标准玻璃卡片容器。"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                {GLASS_CARD_QSS}
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 100))
        card.setGraphicsEffect(shadow)
        return card

    def _make_glass_card_accent(self) -> QWidget:
        """创建带强调边框的玻璃卡片容器。"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                {GLASS_CARD_ACCENT_QSS}
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 100))
        card.setGraphicsEffect(shadow)
        return card
```

- [ ] **Step 4: 重写 `_setup_delegates` 和 `refresh_tree`**

在 `_setup_ui` 之后添加（替换旧的对应方法）：

```python
    def _setup_delegates(self):
        self.progress_delegate = ProgressBarDelegate(self.tree)
        self.progress_delegate.set_tree(self.tree)
        self.risk_delegate = RiskIconDelegate(self.tree)
        self.tree.setItemDelegateForColumn(1, self.progress_delegate)
        self.tree.setItemDelegateForColumn(6, self.risk_delegate)
        # 进度条编辑信号连接
        self.tree.itemDelegateProgressChanged.connect(self._on_progress_edited)

    def refresh_tree(self, filter_text: str = ""):
        try:
            self.tree.clear()
            self.task_item_map.clear()
            self.item_task_map.clear()
            for tid, timer in self._risk_timers.items():
                timer.stop()
            self._risk_timers.clear()

            tasks = self.service.get_task_tree()

            if self._sort_mode == "auto" and not filter_text:
                tasks = self.service.sort_by_score(tasks)
            elif self._sort_mode == "priority":
                tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
            elif self._sort_mode == "due_date":
                far_future = date(2099, 12, 31)
                tasks = sorted(tasks, key=lambda t: t.due_date or far_future)

            for task in tasks:
                if filter_text and not self._match_filter(task, filter_text):
                    continue
                item = self._create_item(task, filter_text)
                self.tree.addTopLevelItem(item)
                self._add_children(item, task, filter_text)

            self._update_status()
            self._refresh_top3()
        except Exception as e:
            QMessageBox.critical(self, "刷新错误", f"刷新任务列表失败：\n{e}")
```

- [ ] **Step 5: 重写 `_create_item` — 嵌入内联编辑控件**

```python
    def _create_item(self, task: Task, filter_text: str = "") -> QTreeWidgetItem:
        item = QTreeWidgetItem()
        item.setText(0, task.name)
        item.setData(0, Qt.ItemDataRole.UserRole + 100, task.parent_id)

        # 列 1: 进度 (由 Delegate 渲染，纯数据存储)
        progress_val = task.progress
        if task.children:
            progress_val = self.service.calculate_progress(task)
        item.setData(1, Qt.ItemDataRole.DisplayRole, progress_val)

        # 列 2: 状态 — 嵌入 QComboBox
        status_combo = QComboBox()
        status_combo.addItems(TaskStatus.values())
        current_status_idx = TaskStatus.values().index(task.status) if task.status in TaskStatus.values() else 0
        status_combo.setCurrentIndex(current_status_idx)
        status_combo.currentIndexChanged.connect(
            lambda idx, t=task: self._on_status_changed(t.id, TaskStatus.values()[idx])
        )
        self.tree.setItemWidget(item, 2, status_combo)

        # 列 3: 优先级 — 嵌入 QComboBox（带颜色）
        prio_combo = QComboBox()
        for i, label in enumerate(Priority.labels()):
            prio_combo.addItem(label)
            prio_combo.setItemData(i, QColor(Priority(i+1).color), Qt.ItemDataRole.ForegroundRole)
        prio_combo.setCurrentIndex(task.priority - 1 if 1 <= task.priority <= 5 else 2)
        prio_combo.currentIndexChanged.connect(
            lambda idx, t=task: self._on_priority_changed(t.id, idx + 1)
        )
        self.tree.setItemWidget(item, 3, prio_combo)

        # 列 4: 开始日期 (文本)
        item.setText(4, task.start_date.isoformat() if task.start_date else "")

        # 列 5: 截止日期 (文本)
        item.setText(5, task.due_date.isoformat() if task.due_date else "")

        # 列 6: 风险 — 嵌入 QLineEdit（防抖保存）
        risk_edit = QLineEdit()
        risk_edit.setText(task.risk)
        risk_edit.setPlaceholderText("风险...")
        timer = QTimer()
        timer.setSingleShot(True)
        timer.setInterval(500)
        timer.timeout.connect(lambda t=task, e=risk_edit: self._on_risk_changed(t.id, e.text()))
        risk_edit.textChanged.connect(lambda: timer.start())
        risk_edit.editingFinished.connect(lambda t=task, e=risk_edit: self._on_risk_changed(t.id, e.text()))
        self._risk_timers[task.id] = timer
        self.tree.setItemWidget(item, 6, risk_edit)

        # 高风险样式
        if task.is_high_risk:
            risk_edit.setStyleSheet(f"""
                QLineEdit {{
                    background: rgba(255, 97, 136, 20);
                    border: 1px solid rgba(255, 97, 136, 60);
                    border-radius: 3px;
                    padding: 2px 6px;
                    font-size: {AppleTheme.FONT_SIZE_SMALL}px;
                    color: {AppleTheme.DANGER};
                }}
            """)

        # 列 7: 备注 (文本片段)
        item.setText(7, task.remarks[:60] + "..." if len(task.remarks) > 60 else task.remarks)

        # 已完成样式
        if task.status == TaskStatus.DONE.value:
            done_font = item.font(0)
            done_font.setStrikeOut(True)
            item.setFont(0, done_font)
            item.setForeground(0, QColor(AppleTheme.TEXT_DISABLED))

        if task.id is not None:
            self.task_item_map[task.id] = item
            self.item_task_map[id(item)] = task

        return item
```

- [ ] **Step 6: 添加内联编辑回调方法**

```python
    def _on_status_changed(self, task_id: int, status: str):
        self.service.mark_status(task_id, status)
        self.refresh_tree()

    def _on_priority_changed(self, task_id: int, priority: int):
        task = self.service.repo.get_task_by_id(task_id)
        if task:
            task.priority = priority
            self.service.repo.update_task(task)
            self.refresh_tree()

    def _on_risk_changed(self, task_id: int, risk_text: str):
        task = self.service.repo.get_task_by_id(task_id)
        if task and task.risk != risk_text.strip():
            task.risk = risk_text.strip()
            self.service.repo.update_task(task)
            self.refresh_tree()

    def _on_progress_edited(self, index, new_progress: int):
        task = self.item_task_map.get(id(self.tree.itemFromIndex(index)))
        if task:
            task.progress = new_progress
            self.service.repo.update_task(task)
            self.refresh_tree()
```

- [ ] **Step 7: 添加拖拽完成回调**

```python
    def _on_drag_finished(self):
        """拖拽完成后持久化新顺序。"""
        # 收集所有顶层项的顺序
        root_ids = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            task = self.item_task_map.get(id(item))
            if task:
                root_ids.append(task.id)
        if root_ids:
            self.service.reorder_siblings(None, root_ids)

        # 同时也处理每个根的子项
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            task = self.item_task_map.get(id(item))
            if task and item.childCount() > 0:
                child_ids = []
                for j in range(item.childCount()):
                    child = item.child(j)
                    ct = self.item_task_map.get(id(child))
                    if ct:
                        child_ids.append(ct.id)
                if child_ids:
                    self.service.reorder_siblings(task.id, child_ids)
```

- [ ] **Step 8: 添加 TOP3 刷新与导航**

```python
    def _refresh_top3(self):
        top_data = self.service.get_top3()
        self.top3_panel.update_top3(top_data)

    def _navigate_to_task(self, task_id: int):
        """点击 TOP3 项 → 定位到树中对应任务。"""
        item = self.task_item_map.get(task_id)
        if item:
            self.tree.setCurrentItem(item)
            self.tree.scrollToItem(item)
```

- [ ] **Step 9: 保留其余方法**

以下方法保持不变（直接从现有文件中保留）：
- `_safe_exec`, `_match_filter`, `_add_children`, `_update_status`, `_count_all`, `_count_by_status`
- `_get_selected_task`, `_add_task`, `_do_add_task`, `_add_child_task`, `_do_add_child_task`
- `_edit_selected`, `_do_edit_selected`, `_delete_selected`, `_do_delete_selected`
- `_mark_status`, `_increase_priority`, `_decrease_priority`
- `_show_context_menu`, `_on_search`, `_on_sort_changed`
- `_export_xlsx`, `_do_export_xlsx`, `_export_pdf`, `_do_export_pdf`
- `_import_xlsx`, `_do_import_xlsx`, `_import_task_recursive`
- `closeEvent`

**注意：** `_do_mark_status` 中的状态变更会触发 `refresh_tree()`，而现在状态列是 ComboBox，所以不会有冲突。右键菜单的"标记状态"会直接调用 `_mark_status` → `_do_mark_status`，其中会 update 数据库并 refresh_tree。

- [ ] **Step 10: 验证语法**

```bash
python -c "from aura_tasks_pro.views.main_window import MainWindow; print('OK')"
```

---

### Task 7: 最终集成测试与验证

- [ ] **Step 1: 确认应用可启动**

```bash
python run.py
```

检查项：
- 应用窗口正常显示，Glass 卡片样式可见
- 顶栏、左侧工具栏、任务树、底部 TOP3 四个区域渲染正常
- 毛玻璃效果正常（如 Windows 11）

- [ ] **Step 2: 测试内联编辑**

- 任务树中状态列为下拉框，切换状态后自动刷新
- 优先级列下拉框可切换，颜色即时更新
- 进度列可点击进度条直接修改
- 风险列可输入文字，500ms 后自动保存

- [ ] **Step 3: 测试拖拽排序**

- 同层级任务可拖拽交换顺序
- 跨层级拖拽被拒绝（不执行动作）
- 拖拽后刷新保持新顺序

- [ ] **Step 4: 测试 TOP3 面板**

- 添加若干带风险、截止日期的任务
- 底部 TOP3 面板显示得分最高的 3 个任务
- 点击 TOP3 项可定位到树中对应任务

- [ ] **Step 5: 测试回归功能**

- 新建任务 / 子任务
- 编辑任务（双击名称/备注 → 弹窗）
- 删除任务
- 搜索过滤
- 排序切换
- 导出 Excel / PDF
- 导入 Excel

---

### Task 8: 清理与收尾

- [ ] **Step 1: 移除未使用的 import**

确认 `main_window.py` 中没有未使用的导入。运行：
```bash
python -c "import py_compile; py_compile.compile('aura_tasks_pro/views/main_window.py', doraise=True)"
```

- [ ] **Step 2: 确认所有文件导入正常**

```bash
python -c "from aura_tasks_pro.views.main_window import MainWindow; from aura_tasks_pro.views.top3_panel import Top3Panel; from aura_tasks_pro.views.drag_tree import DragDropTreeWidget; from aura_tasks_pro.delegates.task_delegates import ProgressBarDelegate; print('All imports OK')"
```
