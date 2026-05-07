import traceback
from datetime import date
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QApplication,
    QTreeWidgetItem, QHeaderView, QFileDialog, QMenu,
    QMessageBox, QLabel, QComboBox, QLineEdit, QFrame,
    QDateEdit, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QSize, QTimer, QDate
from PyQt6.QtGui import QColor, QFont, QIcon, QAction

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
    border-radius: 6px;
    padding: 5px 10px;
    color: {AppleTheme.TEXT_SECONDARY};
}}
NavigationTreeWidget::item:selected {{
    background: {AppleTheme.ACCENT_LIGHT};
    color: {AppleTheme.ACCENT};
}}
NavigationTreeWidget::item:hover {{
    background: {AppleTheme.ACCENT_SOFT};
}}

QPushButton {{
    background: #FFFFFF;
    border: 1px solid #E0E2E6;
    border-radius: {AppleTheme.RADIUS_BUTTON}px;
    padding: 6px 14px;
    font-size: {AppleTheme.FONT_SIZE_BODY}px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QPushButton:hover {{
    background: #F8F9FB;
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
    background: #1D4ED8;
}}

SearchLineEdit {{
    background: #FFFFFF;
    border: 1px solid #E0E2E6;
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
    border: 1px solid #E0E2E6;
    border-radius: {AppleTheme.RADIUS_INPUT}px;
    padding: 4px 10px;
    color: {AppleTheme.TEXT_PRIMARY};
    min-width: 100px;
}}
ComboBox:hover {{
    border-color: {AppleTheme.ACCENT};
}}
QComboBox QAbstractItemView {{
    background: #FFFFFF;
    border: 1px solid #E0E2E6;
    selection-background-color: {AppleTheme.ACCENT_LIGHT};
    color: {AppleTheme.TEXT_PRIMARY};
}}

QTreeWidget {{
    background: #FFFFFF;
    alternate-background-color: #FAFBFC;
    border: none;
    border-radius: {AppleTheme.RADIUS_CARD}px;
    outline: none;
    font-size: {AppleTheme.FONT_SIZE_BODY}px;
    padding: 2px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QTreeWidget::item {{
    padding: 3px 2px;
    border-radius: 3px;
    border-bottom: 1px solid #F0F1F3;
    min-height: 28px;
}}
QTreeWidget::item:selected {{
    background: {AppleTheme.ACCENT_LIGHT};
    color: {AppleTheme.TEXT_PRIMARY};
}}
QTreeWidget::item:hover:!selected {{
    background: #F8FAFD;
}}
QTreeWidget::branch {{
    background: transparent;
}}

QHeaderView::section {{
    background: #F8F9FB;
    border: none;
    border-bottom: 2px solid {AppleTheme.ACCENT};
    padding: 10px 6px;
    font-weight: 700;
    font-size: {AppleTheme.FONT_SIZE_SMALL}px;
    color: {AppleTheme.TEXT_SECONDARY};
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

QMenu {{
    background: #FFFFFF;
    border: 1px solid #E0E2E6;
    border-radius: {AppleTheme.RADIUS_INPUT}px;
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
    background: #E0E2E6;
    margin: 4px 8px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #C8CCD4;
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: #A0A5B0;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: #C8CCD4;
    border-radius: 3px;
    min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QMessageBox {{
    background: #FFFFFF;
}}
QMessageBox QLabel {{
    color: {AppleTheme.TEXT_PRIMARY};
}}

QDateEdit {{
    background: #FFFFFF;
    border: 1px solid #E0E2E6;
    border-radius: 3px;
    padding: 1px 4px;
    font-size: {AppleTheme.FONT_SIZE_SMALL}px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QDateEdit:hover {{
    border-color: {AppleTheme.ACCENT};
}}
QDateEdit:focus {{
    border-color: {AppleTheme.ACCENT};
}}
QDateEdit::drop-down {{
    border: none;
    width: 16px;
}}

QTreeWidget QComboBox {{
    background: #FFFFFF;
    border: 1px solid #E0E2E6;
    border-radius: 3px;
    padding: 1px 4px;
    font-size: {AppleTheme.FONT_SIZE_SMALL}px;
    color: {AppleTheme.TEXT_PRIMARY};
    min-width: 60px;
}}
QTreeWidget QComboBox:hover {{
    border-color: {AppleTheme.ACCENT};
}}
QTreeWidget QComboBox QAbstractItemView {{
    background: #FFFFFF;
    border: 1px solid {AppleTheme.ACCENT};
    selection-background-color: {AppleTheme.ACCENT_LIGHT};
    color: {AppleTheme.TEXT_PRIMARY};
}}
QTreeWidget QComboBox::drop-down {{
    border: none;
    width: 14px;
}}

QTreeWidget QLineEdit {{
    background: #FFFFFF;
    border: 1px solid #E0E2E6;
    border-radius: 3px;
    padding: 1px 4px;
    font-size: {AppleTheme.FONT_SIZE_SMALL}px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QTreeWidget QLineEdit:hover {{
    border-color: {AppleTheme.ACCENT};
}}
QTreeWidget QLineEdit:focus {{
    border-color: {AppleTheme.ACCENT};
}}

QTreeWidget QDateEdit {{
    background: #FFFFFF;
    border: 1px solid #E0E2E6;
    border-radius: 3px;
    padding: 1px 4px;
    font-size: {AppleTheme.FONT_SIZE_SMALL}px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
QTreeWidget QDateEdit:hover {{
    border-color: {AppleTheme.ACCENT};
}}
QTreeWidget QDateEdit:focus {{
    border-color: {AppleTheme.ACCENT};
}}
QTreeWidget QDateEdit::drop-down {{
    border: none;
    width: 14px;
}}
"""


class MainWindow(FluentWindow):
    """AuraTasks Pro — 现代浅色暖白设计。"""

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
        self._risk_timers: Dict[int, QTimer] = {}
        self._refreshing = False

        self._setup_ui()
        self._setup_delegates()
        self.refresh_tree()

    def showEvent(self, event):
        super().showEvent(event)
        enable_acrylic(self, gradient_color=0xCCF5F5F7)

    # ─── 布局构建 ──────────────────────────────────────────

    def _setup_ui(self):
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainInterface")
        self.main_widget.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(20, 14, 20, 14)

        # ─── 顶栏 ──────────────────────────────────────
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
        sort_label.setStyleSheet(
            f"color: {AppleTheme.TEXT_SECONDARY}; background: transparent; border: none;"
        )
        top_layout.addWidget(sort_label)
        self.sort_combo = ComboBox()
        self.sort_combo.addItems(["自动排序", "按优先级", "按截止日期", "手动排序"])
        self.sort_combo.setCurrentIndex(0)
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        top_layout.addWidget(self.sort_combo)

        main_layout.addWidget(top_bar)

        # ─── 中部 ──────────────────────────────────────
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(14)

        # 左侧工具栏卡片
        sidebar = self._make_card_accent()
        sidebar.setFixedWidth(140)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 18, 14, 18)
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
        sep.setStyleSheet("background: #E0E2E6; max-height: 1px; border: none;")
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
        self.status_label.setStyleSheet(
            f"color: {AppleTheme.TEXT_SECONDARY}; font-size: {AppleTheme.FONT_SIZE_SMALL}px; "
            f"font-weight: 500; background: transparent; border: none;"
        )
        sidebar_layout.addWidget(self.status_label)

        mid_layout.addWidget(sidebar)

        # 主树卡片
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

        # ─── 底部 TOP3 ─────────────────────────────────
        self.top3_panel = Top3Panel()
        top3_wrapper = self._make_card_accent()
        top3_wrapper_layout = QVBoxLayout(top3_wrapper)
        top3_wrapper_layout.setContentsMargins(14, 14, 14, 14)
        top3_wrapper_layout.addWidget(self.top3_panel)
        self.top3_panel.taskClicked.connect(self._navigate_to_task)
        self.top3_panel.taskRightClicked.connect(self._edit_top3_task)
        main_layout.addWidget(top3_wrapper)

        self.addSubInterface(
            self.main_widget, FluentIcon.HOME, "任务列表",
            NavigationItemPosition.TOP
        )

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

    # ─── Delegate ────────────────────────────────────────────

    def _setup_delegates(self):
        self.progress_delegate = ProgressBarDelegate(self.tree)
        self.progress_delegate.set_tree(self.tree)
        self.risk_delegate = RiskIconDelegate(self.tree)
        self.tree.setItemDelegateForColumn(1, self.progress_delegate)
        self.tree.setItemDelegateForColumn(6, self.risk_delegate)

    # ─── 安全执行 ────────────────────────────────────────────

    def _safe_exec(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败：\n{e}\n\n{traceback.format_exc()}")
            return None

    # ─── 刷新 ────────────────────────────────────────────────

    def refresh_tree(self, filter_text: str = ""):
        self._refreshing = True
        try:
            self.tree.clear()
            self.task_item_map.clear()
            self.item_task_map.clear()
            for timer in self._risk_timers.values():
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

        # 列 2: 状态 ComboBox
        status_combo = QComboBox()
        status_combo.addItems(TaskStatus.values())
        for i, s in enumerate(TaskStatus.values()):
            fg = AppleTheme.STATUS_COLORS.get(s, (AppleTheme.TEXT_PRIMARY,))[0]
            status_combo.setItemData(i, QColor(fg), Qt.ItemDataRole.ForegroundRole)
        idx = TaskStatus.values().index(task.status) if task.status in TaskStatus.values() else 0
        status_combo.blockSignals(True)
        status_combo.setCurrentIndex(idx)
        status_combo.blockSignals(False)
        status_combo.currentIndexChanged.connect(
            lambda i, tid=task.id: self._on_status_changed(tid, TaskStatus.values()[i])
        )
        self.tree.setItemWidget(item, 2, status_combo)

        # 列 3: 优先级 ComboBox
        prio_combo = QComboBox()
        for i, label in enumerate(Priority.labels()):
            prio_combo.addItem(label)
            prio_combo.setItemData(i, QColor(Priority(i + 1).color), Qt.ItemDataRole.ForegroundRole)
        pidx = task.priority - 1 if 1 <= task.priority <= 5 else 2
        prio_combo.blockSignals(True)
        prio_combo.setCurrentIndex(pidx)
        prio_combo.blockSignals(False)
        prio_combo.currentIndexChanged.connect(
            lambda i, tid=task.id: self._on_priority_changed(tid, i + 1)
        )
        self.tree.setItemWidget(item, 3, prio_combo)

        # 列 4: 开始日期 QDateEdit
        start_date_edit = QDateEdit()
        start_date_edit.setCalendarPopup(True)
        start_date_edit.setSpecialValueText("—")
        start_date_edit.setDisplayFormat("yyyy-MM-dd")
        if task.start_date:
            start_date_edit.setDate(QDate(task.start_date.year, task.start_date.month, task.start_date.day))
        else:
            start_date_edit.clear()
            start_date_edit.setDate(start_date_edit.minimumDate())
        start_date_edit.dateChanged.connect(
            lambda qd, tid=task.id: self._on_date_changed(tid, "start", qd)
        )
        self.tree.setItemWidget(item, 4, start_date_edit)

        # 列 5: 截止日期 QDateEdit
        due_date_edit = QDateEdit()
        due_date_edit.setCalendarPopup(True)
        due_date_edit.setSpecialValueText("—")
        due_date_edit.setDisplayFormat("yyyy-MM-dd")
        if task.due_date:
            due_date_edit.setDate(QDate(task.due_date.year, task.due_date.month, task.due_date.day))
        else:
            due_date_edit.clear()
            due_date_edit.setDate(due_date_edit.minimumDate())
        due_date_edit.dateChanged.connect(
            lambda qd, tid=task.id: self._on_date_changed(tid, "due", qd)
        )
        self.tree.setItemWidget(item, 5, due_date_edit)

        # 列 6: 风险 ComboBox (替代原先的 QLineEdit)
        risk_combo = QComboBox()
        risk_combo.addItems(RISK_LEVELS)
        risk_idx = RISK_LEVELS.index(task.risk) if task.risk in RISK_LEVELS else 0
        risk_combo.blockSignals(True)
        risk_combo.setCurrentIndex(risk_idx)
        risk_combo.blockSignals(False)
        # 给高风险选项上色
        for i, rl in enumerate(RISK_LEVELS):
            if rl in ("高", "严重", "紧急"):
                risk_combo.setItemData(i, QColor(AppleTheme.DANGER), Qt.ItemDataRole.ForegroundRole)
        risk_combo.currentIndexChanged.connect(
            lambda i, tid=task.id: self._on_risk_level_changed(tid, RISK_LEVELS[i])
        )
        self.tree.setItemWidget(item, 6, risk_combo)

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
        tasks = self.service.get_task_tree()
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

    # ─── 内联编辑回调 ────────────────────────────────────────

    def _on_status_changed(self, task_id: int, status: str):
        self.service.mark_status(task_id, status)
        self.refresh_tree()

    def _on_priority_changed(self, task_id: int, priority: int):
        task = self.service.repo.get_task_by_id(task_id)
        if task:
            task.priority = priority
            self.service.repo.update_task(task)
            self.refresh_tree()

    def _on_risk_level_changed(self, task_id: int, risk: str):
        task = self.service.repo.get_task_by_id(task_id)
        if task:
            val = "" if risk == "无" else risk
            if task.risk != val:
                task.risk = val
                self.service.repo.update_task(task)
                self.refresh_tree()

    def _on_date_changed(self, task_id: int, field: str, qdate: QDate):
        task = self.service.repo.get_task_by_id(task_id)
        if not task:
            return
        if qdate.isNull() or qdate == QDate(1752, 9, 14):  # minimum date = cleared
            new_val = None
        else:
            try:
                new_val = date(qdate.year(), qdate.month(), qdate.day())
            except Exception:
                return
        old_val = task.start_date if field == "start" else task.due_date
        if old_val != new_val:
            if field == "start":
                task.start_date = new_val
            else:
                task.due_date = new_val
            self.service.repo.update_task(task)
            QTimer.singleShot(0, self.refresh_tree)

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

    # ─── 拖拽排序 ────────────────────────────────────────────

    def _on_drag_finished(self):
        root_ids = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            t = self.item_task_map.get(id(item))
            if t:
                root_ids.append(t.id)
        if root_ids:
            self.service.reorder_siblings(None, root_ids)
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            t = self.item_task_map.get(id(item))
            if t and item.childCount() > 0:
                child_ids = []
                for j in range(item.childCount()):
                    child = item.child(j)
                    ct = self.item_task_map.get(id(child))
                    if ct:
                        child_ids.append(ct.id)
                if child_ids:
                    self.service.reorder_siblings(t.id, child_ids)

    # ─── TOP3 ─────────────────────────────────────────────────

    def _refresh_top3(self):
        top_data = self.service.get_top3()
        self.top3_panel.update_top3(top_data)

    def _navigate_to_task(self, task_id: int):
        item = self.task_item_map.get(task_id)
        if item:
            self.tree.setCurrentItem(item)
            self.tree.scrollToItem(item)

    def _edit_top3_task(self, task_id: int):
        """Top3 卡片右键 → 快速编辑"""
        task = self.service.repo.get_task_by_id(task_id)
        if not task:
            return
        dlg = TaskEditDialog(task, parent=self)
        if dlg.exec():
            self.service.update_task(dlg.get_task())
            self.refresh_tree()

    # ─── 交互操作 ────────────────────────────────────────────

    def _get_selected_task(self) -> Optional[Task]:
        items = self.tree.selectedItems()
        if not items:
            return None
        return self.item_task_map.get(id(items[0]))

    def _add_task(self):
        self._safe_exec(self._do_add_task)

    def _do_add_task(self):
        task = Task(name="新任务")
        dlg = TaskEditDialog(task, parent=self)
        if dlg.exec():
            self.service.add_task(dlg.get_task())
            self.refresh_tree()

    def _add_child_task(self):
        self._safe_exec(self._do_add_child_task)

    def _do_add_child_task(self):
        parent = self._get_selected_task()
        if not parent:
            InfoBar.warning(
                title="提示", content="请先选择父任务",
                orient=Qt.Orientation.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, parent=self,
            )
            return
        child = Task(parent_id=parent.id, name="新子任务")
        max_ok = self.service.repo.get_max_depth(parent.id) < 2
        dlg = TaskEditDialog(child, max_depth_ok=max_ok, parent=self)
        if dlg.exec():
            self.service.add_task(dlg.get_task())
            self.refresh_tree()

    def _edit_selected(self):
        self._safe_exec(self._do_edit_selected)

    def _do_edit_selected(self):
        task = self._get_selected_task()
        if not task:
            return
        dlg = TaskEditDialog(task, parent=self)
        if dlg.exec():
            self.service.update_task(dlg.get_task())
            self.refresh_tree()

    def _delete_selected(self):
        self._safe_exec(self._do_delete_selected)

    def _do_delete_selected(self):
        task = self._get_selected_task()
        if not task:
            return
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定删除任务「{task.name}」及其所有子任务吗？",
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

    # ─── 右键菜单 ────────────────────────────────────────────

    def _show_context_menu(self, pos):
        try:
            item = self.tree.itemAt(pos)
            if not item:
                return
            task = self.item_task_map.get(id(item))
            if not task:
                return
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

    # ─── 搜索与排序 ──────────────────────────────────────────

    def _on_search(self, text: str):
        self.refresh_tree(filter_text=text.strip())

    def _on_sort_changed(self, index: int):
        modes = ["auto", "priority", "due_date", "manual"]
        self._sort_mode = modes[index] if index < len(modes) else "auto"
        self.refresh_tree()

    # ─── 导出/导入 ──────────────────────────────────────────

    def _export_xlsx(self):
        self._safe_exec(self._do_export_xlsx)

    def _do_export_xlsx(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出 Excel", "", "Excel 文件 (*.xlsx)")
        if path:
            export_xlsx(self.service.get_task_tree(), path)
            InfoBar.success(
                title="导出成功", content=f"已导出到 {path}",
                orient=Qt.Orientation.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, parent=self,
            )

    def _export_pdf(self):
        self._safe_exec(self._do_export_pdf)

    def _do_export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出 PDF", "", "PDF 文件 (*.pdf)")
        if path:
            export_pdf(self.service.get_task_tree(), path)
            InfoBar.success(
                title="导出成功", content=f"已导出到 {path}",
                orient=Qt.Orientation.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, parent=self,
            )

    def _import_xlsx(self):
        self._safe_exec(self._do_import_xlsx)

    def _do_import_xlsx(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入 Excel", "", "Excel 文件 (*.xlsx)")
        if not path:
            return
        imported_tasks = import_xlsx(path)
        for t in imported_tasks:
            self._import_task_recursive(t)
        self.refresh_tree()
        InfoBar.success(
            title="导入成功", content="任务已导入",
            orient=Qt.Orientation.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, parent=self,
        )

    def _import_task_recursive(self, task: Task, parent_id: Optional[int] = None):
        task.parent_id = parent_id
        new_id = self.service.add_task(task)
        for child in task.children:
            self._import_task_recursive(child, new_id)

    # ─── 关闭 ────────────────────────────────────────────────

    def closeEvent(self, event):
        for timer in self._risk_timers.values():
            timer.stop()
        self.service.close()
        super().closeEvent(event)
