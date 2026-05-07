import traceback
from datetime import date
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QApplication,
    QTreeWidgetItem, QHeaderView, QFileDialog, QMenu,
    QMessageBox, QLabel, QComboBox, QLineEdit, QFrame,
    QDateEdit, QGraphicsDropShadowEffect, QDialog,
    QCalendarWidget, QPushButton, QInputDialog, QAbstractItemView,
)
from PyQt6.QtCore import Qt, QSize, QTimer, QDate, QPoint
from PyQt6.QtGui import QColor, QFont, QIcon, QAction, QCursor

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon,
    PushButton, PrimaryPushButton, SearchLineEdit,
    ComboBox, InfoBar, InfoBarPosition, TitleLabel, BodyLabel,
    CaptionLabel, setTheme, Theme, LineEdit,
)

from ..models.task import Task
from ..models.workspace import Workspace
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

COLUMNS = ["任务名称", "进度", "状态", "优先级", "开始日期", "截止日期", "风险", "备注"]
RISK_LEVELS = ["无", "低", "中", "高", "严重", "紧急"]

GLASS_CARD = f"""
    background: {AppleTheme.GLASS_BG};
    border: 1px solid {AppleTheme.GLASS_BORDER_SUBTLE};
    border-radius: {AppleTheme.RADIUS_BENTO}px;
"""
GLASS_CARD_ACCENT = f"""
    background: {AppleTheme.GLASS_BG};
    border: 1px solid {AppleTheme.GLASS_BORDER};
    border-radius: {AppleTheme.RADIUS_BENTO}px;
"""

LIGHT_QSS = f"""
QWidget {{
    font-family: {AppleTheme.FONT_FAMILY};
    font-size: {AppleTheme.FONT_SIZE_BODY}px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QMainWindow, FluentWindow {{
    background: {AppleTheme.WINDOW_BG};
}}
NavigationPanel {{
    background: {AppleTheme.SIDEBAR_BG};
    border-right: 1px solid {AppleTheme.GLASS_BORDER_SUBTLE};
}}
NavigationTreeWidget {{
    background: transparent;
}}
NavigationTreeWidget::item {{
    border-radius: 8px;
    padding: 5px 10px;
    color: {AppleTheme.TEXT_SECONDARY};
}}
NavigationTreeWidget::item:selected {{
    background: {AppleTheme.ACCENT_LIGHT};
    color: {AppleTheme.ACCENT};
    font-weight: 600;
}}
NavigationTreeWidget::item:hover {{
    background: {AppleTheme.ACCENT_SOFT};
}}
QPushButton {{
    background: #FFFFFF;
    border: 1px solid #CCDED9;
    border-radius: {AppleTheme.RADIUS_BUTTON}px;
    padding: 6px 14px;
    font-size: {AppleTheme.FONT_SIZE_BODY}px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QPushButton:hover {{
    background: #F4FAF8;
    border-color: {AppleTheme.ACCENT};
}}
QPushButton:pressed {{
    background: {AppleTheme.ACCENT_LIGHT};
}}
PrimaryPushButton {{
    background: {AppleTheme.ACCENT};
    border: none;
    border-radius: {AppleTheme.RADIUS_BUTTON}px;
    padding: 6px 14px;
    color: #FFFFFF;
    font-weight: 700;
}}
PrimaryPushButton:hover {{
    background: {AppleTheme.ACCENT_HOVER};
}}
PrimaryPushButton:pressed {{
    background: #0F766E;
}}
SearchLineEdit {{
    background: #FFFFFF;
    border: 1px solid #CCDED9;
    border-radius: {AppleTheme.RADIUS_INPUT}px;
    padding: 6px 12px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
SearchLineEdit:focus {{
    border-color: {AppleTheme.ACCENT};
    background: #FFFFFF;
}}
ComboBox {{
    background: #FFFFFF;
    border: 1px solid #CCDED9;
    border-radius: {AppleTheme.RADIUS_INPUT}px;
    padding: 4px 10px;
    color: {AppleTheme.TEXT_PRIMARY};
    min-width: 100px;
}}
ComboBox:hover {{ border-color: {AppleTheme.ACCENT}; }}
QComboBox QAbstractItemView {{
    background: #FFFFFF;
    border: 1px solid #CCDED9;
    selection-background-color: {AppleTheme.ACCENT_LIGHT};
    color: {AppleTheme.TEXT_PRIMARY};
}}
QTreeWidget {{
    background: #FFFFFF;
    alternate-background-color: #F6FCFA;
    border: none;
    border-radius: {AppleTheme.RADIUS_CARD}px;
    outline: none;
    font-size: {AppleTheme.FONT_SIZE_BODY}px;
    padding: 2px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QTreeWidget::item {{
    padding: 5px 2px;
    border-radius: 4px;
    border-bottom: 1px solid #E8F2EF;
    min-height: 30px;
}}
QTreeWidget::item:selected {{
    background: {AppleTheme.ACCENT_LIGHT};
    color: {AppleTheme.TEXT_PRIMARY};
}}
QTreeWidget::item:hover:!selected {{
    background: #F0FAF7;
}}
QTreeWidget::branch {{ background: transparent; }}
QHeaderView::section {{
    background: #F4FAF8;
    border: none;
    border-bottom: 2px solid {AppleTheme.ACCENT};
    padding: 10px 6px;
    font-weight: 700;
    font-size: {AppleTheme.FONT_SIZE_SMALL}px;
    color: {AppleTheme.TEXT_SECONDARY};
    letter-spacing: 0.5px;
}}
QMenu {{
    background: #FFFFFF;
    border: 1px solid #CCDED9;
    border-radius: 8px;
    padding: 6px;
}}
QMenu::item {{
    padding: 8px 28px;
    border-radius: 4px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QMenu::item:selected {{
    background: {AppleTheme.ACCENT_LIGHT};
    color: {AppleTheme.ACCENT};
}}
QMenu::separator {{
    height: 1px;
    background: #CCDED9;
    margin: 4px 8px;
}}
QScrollBar:vertical {{
    background: transparent; width: 6px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #B8CFCB; border-radius: 3px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: #8AAAA5; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent; height: 6px; margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: #B8CFCB; border-radius: 3px; min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QMessageBox {{ background: #FFFFFF; }}
QMessageBox QLabel {{ color: {AppleTheme.TEXT_PRIMARY}; }}
QCalendarWidget {{
    background: #FFFFFF;
    border: 1px solid #CCDED9;
    border-radius: 8px;
}}
QCalendarWidget QToolButton {{
    color: {AppleTheme.TEXT_PRIMARY};
    background: transparent;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-weight: 600;
}}
QCalendarWidget QToolButton:hover {{ background: {AppleTheme.ACCENT_SOFT}; }}
QCalendarWidget QAbstractItemView {{
    background: #FFFFFF;
    selection-background-color: {AppleTheme.ACCENT_LIGHT};
    selection-color: {AppleTheme.TEXT_PRIMARY};
    border-radius: 4px;
}}
QCalendarWidget QAbstractItemView::item:hover {{
    background: {AppleTheme.ACCENT_SOFT};
}}
"""


class DatePickerPopup(QDialog):
    """日历选择弹窗。"""

    def __init__(self, current_date: Optional[date], parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(LIGHT_QSS)
        self._selected: Optional[date] = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.cal = QCalendarWidget()
        self.cal.setGridVisible(True)
        self.cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        if current_date:
            self.cal.setSelectedDate(QDate(current_date.year, current_date.month, current_date.day))
        layout.addWidget(self.cal)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        clear_btn = QPushButton("清除日期")
        clear_btn.clicked.connect(self._on_clear)
        btn_layout.addWidget(clear_btn)
        ok_btn = PrimaryPushButton("确定")
        ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def _on_ok(self):
        qd = self.cal.selectedDate()
        self._selected = date(qd.year(), qd.month(), qd.day())
        self.accept()

    def _on_clear(self):
        self._selected = None
        self.accept()

    def selected_date(self) -> Optional[date]:
        return self._selected


class MainWindow(FluentWindow):
    """AuraTasks Pro — Popup Menu 编辑 + 多工作区。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AuraTasks Pro")
        self.setMinimumSize(QSize(1100, 720))
        self.resize(1350, 800)

        setTheme(Theme.LIGHT)
        self.setStyleSheet(LIGHT_QSS)

        self.service = TaskService()
        self.task_item_map: Dict[int, QTreeWidgetItem] = {}
        self.item_task_map: Dict[int, Task] = {}
        self._sort_mode = "auto"
        self._refreshing = False
        self._current_workspace_id: Optional[int] = None
        self._workspace_labels: Dict[int, QWidget] = {}

        self._setup_ui()
        self._setup_delegates()
        self._load_workspaces()
        self.refresh_tree()

    def showEvent(self, event):
        super().showEvent(event)
        enable_acrylic(self, gradient_color=0xCCF5F7)

    # ─── 布局 ─────────────────────────────────────────────

    def _setup_ui(self):
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainInterface")
        self.main_widget.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(20, 14, 20, 14)

        # 顶栏
        top_bar = self._make_card()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)
        top_layout.setSpacing(12)
        app_icon = QLabel("✦")
        app_icon.setStyleSheet(
            f"font-size: 22px; color: {AppleTheme.ACCENT}; font-weight: bold; "
            f"background: transparent; border: none;"
        )
        top_layout.addWidget(app_icon)
        app_title = TitleLabel("AuraTasks Pro")
        app_title.setStyleSheet(
            f"font-size: {AppleTheme.FONT_SIZE_TITLE}px; font-weight: 700; "
            f"color: {AppleTheme.TEXT_PRIMARY}; background: transparent; border: none;"
        )
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

        # 中部
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(14)

        # 左侧栏 — 工作区 + 操作按钮
        sidebar = self._make_card_accent()
        sidebar.setFixedWidth(150)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 14, 12, 14)
        sidebar_layout.setSpacing(6)

        # 工作区标题
        ws_header = QHBoxLayout()
        ws_title = BodyLabel("工作区")
        ws_title.setStyleSheet(f"font-weight: 700; color: {AppleTheme.TEXT_SECONDARY}; background: transparent; border: none;")
        ws_header.addWidget(ws_title)
        ws_header.addStretch()
        add_ws_btn = QPushButton("+")
        add_ws_btn.setFixedSize(24, 24)
        add_ws_btn.setStyleSheet(f"""
            QPushButton {{
                background: {AppleTheme.ACCENT_LIGHT};
                border: none; border-radius: 12px;
                font-size: 14px; font-weight: 700;
                color: {AppleTheme.ACCENT}; padding: 0;
            }}
            QPushButton:hover {{ background: {AppleTheme.ACCENT}; color: #FFFFFF; }}
        """)
        add_ws_btn.clicked.connect(self._add_workspace)
        ws_header.addWidget(add_ws_btn)
        sidebar_layout.addLayout(ws_header)

        self.workspace_list_layout = QVBoxLayout()
        self.workspace_list_layout.setSpacing(2)
        sidebar_layout.addLayout(self.workspace_list_layout)

        # 分隔
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #CCDED9; max-height: 1px; border: none;")
        sidebar_layout.addWidget(sep)
        sidebar_layout.addSpacing(4)

        # 操作按钮
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

        sidebar_layout.addSpacing(2)
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: #CCDED9; max-height: 1px; border: none;")
        sidebar_layout.addWidget(sep2)
        sidebar_layout.addSpacing(2)

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
        self.status_label.setStyleSheet(
            f"color: {AppleTheme.TEXT_SECONDARY}; font-size: {AppleTheme.FONT_SIZE_SMALL}px; "
            f"font-weight: 500; background: transparent; border: none;"
        )
        sidebar_layout.addWidget(self.status_label)
        mid_layout.addWidget(sidebar)

        # 主树
        tree_card = self._make_card()
        tree_card_layout = QVBoxLayout(tree_card)
        tree_card_layout.setContentsMargins(4, 4, 4, 4)

        self.tree = DragDropTreeWidget()
        self.tree.setHeaderLabels(COLUMNS)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(24)
        self.tree.setRootIsDecorated(True)
        self.tree.setAllColumnsShowFocus(False)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.itemDoubleClicked.connect(self._edit_selected)
        self.tree.orderChanged.connect(self._on_drag_finished)
        self.tree.itemChanged.connect(self._on_item_data_changed)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # 单击单元格 → 弹出选择菜单
        self.tree.clicked.connect(self._on_cell_clicked)

        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 110)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 90)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 80)
        for col in range(4, len(COLUMNS)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        tree_card_layout.addWidget(self.tree)
        mid_layout.addWidget(tree_card, 1)
        main_layout.addLayout(mid_layout, 1)

        # 底部 TOP3
        self.top3_panel = Top3Panel()
        top3_wrapper = self._make_card_accent()
        top3_wrapper_layout = QVBoxLayout(top3_wrapper)
        top3_wrapper_layout.setContentsMargins(14, 14, 14, 14)
        top3_wrapper_layout.addWidget(self.top3_panel)
        self.top3_panel.taskClicked.connect(self._navigate_to_task)
        self.top3_panel.taskRightClicked.connect(self._on_top3_right_click)
        main_layout.addWidget(top3_wrapper)

        self.addSubInterface(self.main_widget, FluentIcon.HOME, "任务列表", NavigationItemPosition.TOP)

    def _make_card(self) -> QWidget:
        card = QWidget()
        card.setStyleSheet(f"QWidget {{ {GLASS_CARD} }}")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        return card

    def _make_card_accent(self) -> QWidget:
        card = QWidget()
        card.setStyleSheet(f"QWidget {{ {GLASS_CARD_ACCENT} }}")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        return card

    # ─── 工作区 ──────────────────────────────────────────

    def _load_workspaces(self):
        workspaces = self.service.get_workspaces()
        if workspaces:
            self._current_workspace_id = workspaces[0].id
        self._rebuild_workspace_ui()

    def _rebuild_workspace_ui(self):
        # 清空旧 UI
        while self.workspace_list_layout.count():
            item = self.workspace_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._workspace_labels.clear()

        workspaces = self.service.get_workspaces()
        for ws in workspaces:
            row = QWidget()
            row.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            row.customContextMenuRequested.connect(lambda pos, w=ws: self._workspace_context_menu(pos, w))
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(4, 2, 4, 2)
            row_layout.setSpacing(4)

            label = QLabel(ws.name)
            label.setCursor(Qt.CursorShape.PointingHandCursor)
            is_current = ws.id == self._current_workspace_id
            label.setStyleSheet(
                f"font-size: {AppleTheme.FONT_SIZE_BODY}px; font-weight: {'700' if is_current else '400'}; "
                f"color: {'#0D9488' if is_current else AppleTheme.TEXT_PRIMARY}; "
                f"background: {'rgba(13,148,136,0.10)' if is_current else 'transparent'}; "
                f"border-radius: 6px; padding: 4px 8px; border: none;"
            )
            label.mousePressEvent = lambda e, wid=ws.id: self._switch_workspace(wid)
            row_layout.addWidget(label, 1)
            row_layout.addStretch()

            self.workspace_list_layout.addWidget(row)
            self._workspace_labels[ws.id] = row

        self.workspace_list_layout.addStretch()

    def _switch_workspace(self, ws_id: int):
        self._current_workspace_id = ws_id
        self._rebuild_workspace_ui()
        self.refresh_tree()

    def _add_workspace(self):
        name, ok = QInputDialog.getText(self, "新建工作区", "工作区名称:")
        if ok and name.strip():
            self.service.create_workspace(name.strip())
            self._rebuild_workspace_ui()

    def _workspace_context_menu(self, pos, ws: Workspace):
        menu = QMenu(self)
        act_rename = menu.addAction("重命名")
        act_rename.triggered.connect(lambda: self._rename_workspace(ws))
        if ws.id != self._current_workspace_id:
            act_del = menu.addAction("删除")
            act_del.triggered.connect(lambda: self._delete_workspace(ws))
        menu.exec(pos)

    def _rename_workspace(self, ws: Workspace):
        name, ok = QInputDialog.getText(self, "重命名工作区", "新名称:", text=ws.name)
        if ok and name.strip():
            ws.name = name.strip()
            self.service.update_workspace(ws)
            self._rebuild_workspace_ui()

    def _delete_workspace(self, ws: Workspace):
        reply = QMessageBox.question(
            self, "确认删除", f"删除工作区「{ws.name}」及其所有任务？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.service.delete_workspace(ws.id)
            self._current_workspace_id = None
            self._load_workspaces()
            self.refresh_tree()

    # ─── Delegate ───────────────────────────────────────

    def _setup_delegates(self):
        self.progress_delegate = ProgressBarDelegate(self.tree)
        self.progress_delegate.set_tree(self.tree)
        self.risk_delegate = RiskIconDelegate(self.tree)
        self.tree.setItemDelegateForColumn(1, self.progress_delegate)

    # ─── 单元格点击 → 弹出选择菜单 ──────────────────────

    def _on_cell_clicked(self, index):
        """单击单元格弹出对应选择列表。"""
        item = self.tree.itemFromIndex(index)
        if not item:
            return
        task = self.item_task_map.get(id(item))
        if not task or task.id is None:
            return

        col = index.column()
        # 获取单元格的全局坐标
        rect = self.tree.visualItemRect(item)
        header = self.tree.header()
        x_offset = header.sectionViewportPosition(col)
        cell_rect = self.tree.viewport().mapToGlobal(
            QPoint(x_offset + 5, rect.y() + rect.height())
        )

        if col == 2:
            self._popup_status(task, cell_rect)
        elif col == 3:
            self._popup_priority(task, cell_rect)
        elif col == 4:
            self._popup_date(task, "start", cell_rect)
        elif col == 5:
            self._popup_date(task, "due", cell_rect)
        elif col == 6:
            self._popup_risk(task, cell_rect)

    def _popup_status(self, task: Task, pos: QPoint):
        menu = QMenu(self)
        for s in TaskStatus.values():
            act = menu.addAction(s)
            fg = AppleTheme.STATUS_COLORS.get(s, (AppleTheme.TEXT_PRIMARY,))[0]
            act.setIcon(QIcon())  # placeholder for color dot
            font = act.font()
            font.setWeight(700 if s == task.status else 400)
            act.setFont(font)
            act.triggered.connect(lambda checked, st=s: self._quick_set_status(task.id, st))
        menu.exec(pos)

    def _popup_priority(self, task: Task, pos: QPoint):
        menu = QMenu(self)
        for i, label in enumerate(Priority.labels()):
            prio = i + 1
            act = menu.addAction(f"● {label}")
            act.setData(QColor(Priority(prio).color))
            font = act.font()
            font.setWeight(700 if prio == task.priority else 400)
            act.setFont(font)
            act.triggered.connect(lambda checked, p=prio: self._quick_set_priority(task.id, p))
        menu.exec(pos)

    def _popup_risk(self, task: Task, pos: QPoint):
        menu = QMenu(self)
        for rl in RISK_LEVELS:
            act = menu.addAction(rl)
            font = act.font()
            current_val = task.risk if task.risk else "无"
            font.setWeight(700 if rl == current_val else 400)
            act.setFont(font)
            if rl in ("高", "严重", "紧急"):
                act.setIcon(QIcon())
            act.triggered.connect(lambda checked, r=rl: self._quick_set_risk(task.id, r))
        menu.exec(pos)

    def _popup_date(self, task: Task, field: str, pos: QPoint):
        current = task.start_date if field == "start" else task.due_date
        dlg = DatePickerPopup(current, self)
        dlg.move(pos)
        if dlg.exec():
            new_val = dlg.selected_date()
            old_val = task.start_date if field == "start" else task.due_date
            if old_val != new_val:
                if field == "start":
                    task.start_date = new_val
                else:
                    task.due_date = new_val
                self.service.repo.update_task(task)
                self.refresh_tree()

    def _quick_set_status(self, task_id: int, status: str):
        self.service.mark_status(task_id, status)
        self.refresh_tree()

    def _quick_set_priority(self, task_id: int, priority: int):
        task = self.service.repo.get_task_by_id(task_id)
        if task:
            task.priority = priority
            self.service.repo.update_task(task)
            self.refresh_tree()

    def _quick_set_risk(self, task_id: int, risk: str):
        task = self.service.repo.get_task_by_id(task_id)
        if task:
            task.risk = "" if risk == "无" else risk
            self.service.repo.update_task(task)
            self.refresh_tree()

    # ─── 安全执行 ───────────────────────────────────────

    def _safe_exec(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败：\n{e}\n\n{traceback.format_exc()}")
            return None

    # ─── 刷新 ───────────────────────────────────────────

    def refresh_tree(self, filter_text: str = ""):
        self._refreshing = True
        try:
            self.tree.clear()
            self.task_item_map.clear()
            self.item_task_map.clear()

            tasks = self.service.get_task_tree(workspace_id=self._current_workspace_id)

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
        finally:
            self._refreshing = False

    def _match_filter(self, task: Task, text: str) -> bool:
        text_lower = text.lower()
        if text_lower in task.name.lower() or text_lower in task.remarks.lower():
            return True
        return any(self._match_filter(c, text_lower) for c in task.children)

    def _add_children(self, parent_item: QTreeWidgetItem, parent_task: Task, filter_text: str):
        for child_task in parent_task.children:
            if filter_text and not self._match_filter(child_task, filter_text):
                continue
            child_item = self._create_item(child_task, filter_text)
            parent_item.addChild(child_item)
            self._add_children(child_item, child_task, filter_text)
        parent_item.setExpanded(True)

    def _create_item(self, task: Task, filter_text: str = "") -> QTreeWidgetItem:
        item = QTreeWidgetItem()
        item.setText(0, task.name)
        item.setData(0, Qt.ItemDataRole.UserRole + 100, task.parent_id)

        # 列 1: 进度 (Delegate 渲染)
        progress_val = task.progress
        if task.children:
            progress_val = self.service.calculate_progress(task)
        item.setData(1, Qt.ItemDataRole.DisplayRole, progress_val)

        # 列 2: 状态 (纯文本，点击弹出菜单)
        item.setText(2, task.status)
        status_color = AppleTheme.STATUS_COLORS.get(task.status, (AppleTheme.TEXT_PRIMARY,))[0]
        item.setForeground(2, QColor(status_color))

        # 列 3: 优先级 (纯文本，点击弹出菜单)
        item.setText(3, task.priority_label)
        prio_color = AppleTheme.PRIORITY_COLORS.get(task.priority, AppleTheme.ACCENT)
        item.setForeground(3, QColor(prio_color))
        font = item.font(3)
        font.setWeight(QFont.Weight.Medium)
        item.setFont(3, font)

        # 列 4: 开始日期
        item.setText(4, task.start_date.isoformat() if task.start_date else "—")
        item.setForeground(4, QColor(AppleTheme.TEXT_SECONDARY if not task.start_date else AppleTheme.TEXT_PRIMARY))

        # 列 5: 截止日期
        item.setText(5, task.due_date.isoformat() if task.due_date else "—")
        if task.due_date:
            days_left = (task.due_date - date.today()).days
            if days_left < 0:
                item.setForeground(5, QColor(AppleTheme.DANGER))
            elif days_left <= 3:
                item.setForeground(5, QColor(AppleTheme.ORANGE))
            else:
                item.setForeground(5, QColor(AppleTheme.TEXT_PRIMARY))
        else:
            item.setForeground(5, QColor(AppleTheme.TEXT_SECONDARY))

        # 列 6: 风险
        risk_display = task.risk if task.risk else "无"
        item.setText(6, risk_display)
        if task.is_high_risk:
            item.setForeground(6, QColor(AppleTheme.DANGER))
            font_r = item.font(6)
            font_r.setWeight(QFont.Weight.Bold)
            item.setFont(6, font_r)
        else:
            item.setForeground(6, QColor(AppleTheme.TEXT_SECONDARY))

        # 列 7: 备注
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

    def _update_status(self):
        tasks = self.service.get_task_tree(workspace_id=self._current_workspace_id)
        total = self._count_all(tasks)
        done = self._count_by_status(tasks, TaskStatus.DONE.value)
        if total:
            self.status_label.setText(
                f"共 {total} 项\n已完成 {done}\n完成率 {done / total * 100:.1f}%"
            )
        else:
            self.status_label.setText("暂无任务\n点击「新建」开始")

    def _count_all(self, tasks: List[Task]) -> int:
        return sum(1 + self._count_all(t.children) for t in tasks)

    def _count_by_status(self, tasks: List[Task], status: str) -> int:
        count = 0
        for t in tasks:
            if t.status == status:
                count += 1
            count += self._count_by_status(t.children, status)
        return count

    # ─── 进度条点击保存 ─────────────────────────────────

    def _on_item_data_changed(self, item: QTreeWidgetItem, column: int):
        if self._refreshing or column != 1:
            return
        task = self.item_task_map.get(id(item))
        if not task:
            return
        new_progress = item.data(1, Qt.ItemDataRole.DisplayRole)
        if new_progress is None:
            return
        try:
            new_progress = int(new_progress)
        except (TypeError, ValueError):
            return
        new_progress = max(0, min(100, new_progress))
        if task.progress != new_progress:
            task.progress = new_progress
            self.service.repo.update_task(task)
            QTimer.singleShot(0, self.refresh_tree)

    # ─── 拖拽排序 ───────────────────────────────────────

    def _on_drag_finished(self):
        root_ids = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            t = self.item_task_map.get(id(item))
            if t: root_ids.append(t.id)
        if root_ids: self.service.reorder_siblings(None, root_ids)
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            t = self.item_task_map.get(id(item))
            if t and item.childCount() > 0:
                child_ids = [self.item_task_map.get(id(item.child(j))).id
                           for j in range(item.childCount())
                           if self.item_task_map.get(id(item.child(j)))]
                if child_ids: self.service.reorder_siblings(t.id, child_ids)

    # ─── TOP3 ───────────────────────────────────────────

    def _refresh_top3(self):
        top_data = self.service.get_top3(workspace_id=self._current_workspace_id)
        self.top3_panel.update_top3(top_data)

    def _navigate_to_task(self, task_id: int):
        item = self.task_item_map.get(task_id)
        if item:
            self.tree.setCurrentItem(item)
            self.tree.scrollToItem(item)

    def _on_top3_right_click(self, task_id: int):
        """Top3 卡片右键 → 弹出快速编辑菜单。"""
        task = self.service.repo.get_task_by_id(task_id)
        if not task:
            return
        menu = QMenu(self)

        # 状态子菜单
        status_menu = menu.addMenu("标记状态")
        for s in TaskStatus.values():
            act = status_menu.addAction(s)
            act.triggered.connect(lambda checked, st=s: self._quick_set_status(task_id, st))

        # 优先级子菜单
        prio_menu = menu.addMenu("优先级")
        for i, label in enumerate(Priority.labels()):
            act = prio_menu.addAction(f"● {label}")
            act.triggered.connect(lambda checked, p=i+1: self._quick_set_priority(task_id, p))

        # 风险子菜单
        risk_menu = menu.addMenu("风险等级")
        for rl in RISK_LEVELS:
            act = risk_menu.addAction(rl)
            act.triggered.connect(lambda checked, r=rl: self._quick_set_risk(task_id, r))

        # 进度子菜单
        prog_menu = menu.addMenu("进度")
        for pct in [0, 25, 50, 75, 100]:
            act = prog_menu.addAction(f"{pct}%")
            act.triggered.connect(lambda checked, p=pct: self._quick_set_progress(task_id, p))

        menu.addSeparator()
        act_full = menu.addAction("完整编辑...")
        act_full.triggered.connect(lambda: self._edit_top3_task(task_id))

        menu.exec(QCursor.pos())

    def _edit_top3_task(self, task_id: int):
        task = self.service.repo.get_task_by_id(task_id)
        if not task: return
        dlg = TaskEditDialog(task, parent=self)
        if dlg.exec():
            self.service.update_task(dlg.get_task())
            self.refresh_tree()

    def _quick_set_progress(self, task_id: int, progress: int):
        task = self.service.repo.get_task_by_id(task_id)
        if task:
            task.progress = progress
            self.service.repo.update_task(task)
            self.refresh_tree()

    # ─── 交互操作 ───────────────────────────────────────

    def _get_selected_task(self) -> Optional[Task]:
        items = self.tree.selectedItems()
        if not items:
            return None
        return self.item_task_map.get(id(items[0]))

    def _add_task(self):
        self._safe_exec(self._do_add_task)

    def _do_add_task(self):
        task = Task(name="新任务", workspace_id=self._current_workspace_id)
        dlg = TaskEditDialog(task, parent=self)
        if dlg.exec():
            self.service.add_task(dlg.get_task())
            self.refresh_tree()

    def _add_child_task(self):
        self._safe_exec(self._do_add_child_task)

    def _do_add_child_task(self):
        parent = self._get_selected_task()
        if not parent:
            InfoBar.warning(title="提示", content="请先选择父任务",
                            orient=Qt.Orientation.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP, parent=self)
            return
        child = Task(parent_id=parent.id, name="新子任务", workspace_id=self._current_workspace_id)
        max_ok = self.service.repo.get_max_depth(parent.id) < 2
        dlg = TaskEditDialog(child, max_depth_ok=max_ok, parent=self)
        if dlg.exec():
            self.service.add_task(dlg.get_task())
            self.refresh_tree()

    def _edit_selected(self):
        self._safe_exec(self._do_edit_selected)

    def _do_edit_selected(self):
        task = self._get_selected_task()
        if not task: return
        dlg = TaskEditDialog(task, parent=self)
        if dlg.exec():
            self.service.update_task(dlg.get_task())
            self.refresh_tree()

    def _delete_selected(self):
        self._safe_exec(self._do_delete_selected)

    def _do_delete_selected(self):
        task = self._get_selected_task()
        if not task: return
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除任务「{task.name}」及其所有子任务吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.service.delete_task(task.id)
            self.refresh_tree()

    def _mark_status(self, status: str):
        self._safe_exec(self._do_mark_status, status)

    def _do_mark_status(self, status: str):
        task = self._get_selected_task()
        if task:
            self.service.mark_status(task.id, status)
            self.refresh_tree()

    def _increase_priority(self):
        self._safe_exec(self._do_increase_priority)

    def _do_increase_priority(self):
        task = self._get_selected_task()
        if task:
            self.service.increase_priority(task.id)
            self.refresh_tree()

    def _decrease_priority(self):
        self._safe_exec(self._do_decrease_priority)

    def _do_decrease_priority(self):
        task = self._get_selected_task()
        if task:
            self.service.decrease_priority(task.id)
            self.refresh_tree()

    # ─── 右键菜单 ───────────────────────────────────────

    def _show_context_menu(self, pos):
        try:
            item = self.tree.itemAt(pos)
            if not item: return
            task = self.item_task_map.get(id(item))
            if not task: return
            menu = QMenu(self)
            act_add = menu.addAction("添加子任务")
            act_add.triggered.connect(self._add_child_task)
            act_edit = menu.addAction("编辑详情")
            act_edit.triggered.connect(self._edit_selected)
            act_del = menu.addAction("删除")
            act_del.triggered.connect(self._delete_selected)
            menu.addSeparator()
            status_menu = menu.addMenu("标记状态")
            for s in TaskStatus.values():
                act = status_menu.addAction(s)
                act.triggered.connect(lambda checked, st=s: self._mark_status(st))
            menu.addSeparator()
            act_up = menu.addAction("提高优先级")
            act_up.triggered.connect(self._increase_priority)
            act_down = menu.addAction("降低优先级")
            act_down.triggered.connect(self._decrease_priority)
            menu.exec(self.tree.viewport().mapToGlobal(pos))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"右键菜单错误：\n{e}")

    # ─── 搜索与排序 ─────────────────────────────────────

    def _on_search(self, text: str):
        self.refresh_tree(filter_text=text.strip())

    def _on_sort_changed(self, index: int):
        modes = ["auto", "priority", "due_date", "manual"]
        self._sort_mode = modes[index] if index < len(modes) else "auto"
        self.refresh_tree()

    # ─── 导出/导入 ──────────────────────────────────────

    def _export_xlsx(self):
        self._safe_exec(self._do_export_xlsx)

    def _do_export_xlsx(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出 Excel", "", "Excel 文件 (*.xlsx)")
        if path:
            export_xlsx(self.service.get_task_tree(workspace_id=self._current_workspace_id), path)
            InfoBar.success(title="导出成功", content=f"已导出到 {path}",
                            orient=Qt.Orientation.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP, parent=self)

    def _export_pdf(self):
        self._safe_exec(self._do_export_pdf)

    def _do_export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出 PDF", "", "PDF 文件 (*.pdf)")
        if path:
            export_pdf(self.service.get_task_tree(workspace_id=self._current_workspace_id), path)
            InfoBar.success(title="导出成功", content=f"已导出到 {path}",
                            orient=Qt.Orientation.Horizontal, isClosable=True,
                            position=InfoBarPosition.TOP, parent=self)

    def _import_xlsx(self):
        self._safe_exec(self._do_import_xlsx)

    def _do_import_xlsx(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入 Excel", "", "Excel 文件 (*.xlsx)")
        if not path: return
        imported_tasks = import_xlsx(path)
        for t in imported_tasks:
            self._import_task_recursive(t)
        self.refresh_tree()
        InfoBar.success(title="导入成功", content="任务已导入",
                        orient=Qt.Orientation.Horizontal, isClosable=True,
                        position=InfoBarPosition.TOP, parent=self)

    def _import_task_recursive(self, task: Task, parent_id: Optional[int] = None):
        task.parent_id = parent_id
        task.workspace_id = self._current_workspace_id
        new_id = self.service.add_task(task)
        for child in task.children:
            self._import_task_recursive(child, new_id)

    # ─── 关闭 ───────────────────────────────────────────

    def closeEvent(self, event):
        self.service.close()
        super().closeEvent(event)
