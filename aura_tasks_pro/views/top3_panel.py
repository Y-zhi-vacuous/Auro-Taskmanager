"""TOP3 关键任务高亮面板。"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from ..utils.apple_theme import AppleTheme
from typing import List


class Top3Card(QWidget):
    """单个 TOP 排名卡片。"""

    clicked = pyqtSignal(int)
    rightClicked = pyqtSignal(int)

    RANK_ICONS = {0: "\U0001F947", 1: "\U0001F948", 2: "\U0001F949"}
    RANK_STYLES = {
        0: (AppleTheme.TOP1_BG, AppleTheme.TOP1_BORDER, AppleTheme.ACCENT),
        1: (AppleTheme.TOP2_BG, AppleTheme.TOP2_BORDER, AppleTheme.CYAN),
        2: (AppleTheme.TOP3_BG, AppleTheme.TOP3_BORDER, AppleTheme.ORANGE),
    }

    def __init__(self, rank: int, parent=None):
        super().__init__(parent)
        self._rank = rank
        self._task_id = None
        bg, border, accent = self.RANK_STYLES[rank]
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        self.setStyleSheet(f"""
            Top3Card {{
                background: {bg};
                border: 1px solid {border};
                border-radius: {AppleTheme.RADIUS_BENTO_INNER}px;
            }}
            Top3Card:hover {{
                background: {AppleTheme.ACCENT_LIGHT};
                border-color: {AppleTheme.ACCENT};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self.icon_label = QLabel(self.RANK_ICONS[rank])
        self.icon_label.setStyleSheet("font-size: 18px; background: transparent; border: none;")
        layout.addWidget(self.icon_label)

        self.path_label = QLabel("—")
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet(f"""
            font-size: {AppleTheme.FONT_SIZE_SMALL}px;
            font-weight: 600;
            color: {AppleTheme.TEXT_PRIMARY};
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.path_label)

        self.meta_label = QLabel("")
        self.meta_label.setStyleSheet(f"""
            font-size: {AppleTheme.FONT_SIZE_SMALL - 1}px;
            color: {AppleTheme.TEXT_SECONDARY};
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.meta_label)

    def set_data(self, item: dict):
        from datetime import date
        t = item["task"]
        self._task_id = t.id
        self.path_label.setText(item["path"])
        days = (t.due_date - date.today()).days if t.due_date else None
        risk_text = f"风险:{t.risk}" if t.risk else "无风险标记"
        if days is not None:
            if days < 0:
                deadline_text = f" | 已逾期{-days}天"
            elif days == 0:
                deadline_text = " | 今日截止"
            else:
                deadline_text = f" | 剩余{days}天"
        else:
            deadline_text = " | 无截止"
        self.meta_label.setText(f"{risk_text}{deadline_text}")
        self.setVisible(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._task_id is not None:
            self.clicked.emit(self._task_id)
        super().mousePressEvent(event)

    def _on_context_menu(self, pos):
        if self._task_id is None:
            return
        menu = QMenu(self)
        act_edit = menu.addAction("编辑此任务")
        act_edit.triggered.connect(lambda: self.rightClicked.emit(self._task_id))
        menu.exec(self.mapToGlobal(pos))

    def clear_data(self):
        self._task_id = None
        self.path_label.setText("—")
        self.meta_label.setText("")
        self.setVisible(False)


class Top3Panel(QWidget):
    """TOP3 面板。"""

    taskClicked = pyqtSignal(int)
    taskRightClicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("top3Panel")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QLabel("关键任务 TOP3")
        title.setStyleSheet(f"""
            font-size: {AppleTheme.FONT_SIZE_SUBTITLE}px;
            font-weight: 700;
            color: {AppleTheme.ACCENT};
            padding: 0 4px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(title)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)
        layout.addLayout(cards_layout)

        self.cards: List[Top3Card] = []
        for i in range(3):
            card = Top3Card(i)
            card.clicked.connect(self.taskClicked.emit)
            card.rightClicked.connect(self.taskRightClicked.emit)
            card.setVisible(False)
            self.cards.append(card)
            cards_layout.addWidget(card, 1)

    def update_top3(self, top_data: List[dict]):
        for i, card in enumerate(self.cards):
            if i < len(top_data):
                card.set_data(top_data[i])
            else:
                card.clear_data()

    def clear(self):
        for card in self.cards:
            card.clear_data()
