import traceback
from datetime import date
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from qfluentwidgets import (
    PrimaryPushButton, PushButton, LineEdit,
    TextEdit, ComboBox, SpinBox, DatePicker, SubtitleLabel,
    InfoBar, InfoBarPosition,
)
from ..models.task import Task
from ..utils.enums import TaskStatus, Priority
from ..utils.apple_theme import AppleTheme

DARK_EDIT_QSS = f"""
QDialog {{
    background: {AppleTheme.EDITOR_BG};
    border: 1px solid rgba(166,226,42,30);
    border-radius: {AppleTheme.RADIUS_WINDOW}px;
}}
QLabel {{
    color: {AppleTheme.TEXT_PRIMARY};
    font-size: {AppleTheme.FONT_SIZE_BODY}px;
}}
QLineEdit, TextEdit {{
    background: rgba(64,62,65,200);
    border: 1px solid rgba(255,255,255,12);
    border-radius: {AppleTheme.RADIUS_INPUT}px;
    padding: 6px 10px;
    color: {AppleTheme.TEXT_PRIMARY};
    selection-background-color: rgba(166,226,42,40);
    selection-color: {AppleTheme.TEXT_PRIMARY};
}}
QLineEdit:focus, TextEdit:focus {{
    border-color: {AppleTheme.ACCENT};
    background: rgba(64,62,65,250);
}}
ComboBox {{
    background: rgba(64,62,65,200);
    border: 1px solid rgba(255,255,255,12);
    border-radius: {AppleTheme.RADIUS_INPUT}px;
    padding: 5px 10px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
ComboBox:hover {{
    border-color: rgba(166,226,42,80);
}}
SpinBox {{
    background: rgba(64,62,65,200);
    border: 1px solid rgba(255,255,255,12);
    border-radius: {AppleTheme.RADIUS_INPUT}px;
    padding: 5px 10px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
SpinBox:hover {{
    border-color: rgba(166,226,42,80);
}}
PushButton {{
    background: rgba(255,255,255,18);
    border: 1px solid rgba(255,255,255,12);
    border-radius: {AppleTheme.RADIUS_BUTTON}px;
    padding: 8px 20px;
    color: {AppleTheme.TEXT_PRIMARY};
}}
PushButton:hover {{
    background: rgba(255,255,255,28);
    border-color: rgba(166,226,42,80);
}}
PrimaryPushButton {{
    background: {AppleTheme.ACCENT};
    border: none;
    border-radius: {AppleTheme.RADIUS_BUTTON}px;
    padding: 8px 20px;
    color: #2D2A2E;
    font-weight: 700;
}}
PrimaryPushButton:hover {{
    background: {AppleTheme.ACCENT_HOVER};
}}
"""


class TaskEditDialog(QDialog):
    """Monokai Pro 风格任务编辑对话框。"""

    def __init__(self, task: Task, max_depth_ok: bool = True, parent=None):
        super().__init__(parent)
        self.task = task
        self.max_depth_ok = max_depth_ok
        self.setWindowTitle("编辑任务" if task.id else "新建任务")
        self.setMinimumSize(440, 540)
        self.setStyleSheet(DARK_EDIT_QSS)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(166, 226, 42, 30))
        self.setGraphicsEffect(shadow)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 24, 28, 24)

        header_layout = QHBoxLayout()
        icon_label = QLabel("✏")
        icon_label.setStyleSheet(f"font-size: 22px; color: {AppleTheme.ACCENT};")
        header_layout.addWidget(icon_label)
        title = SubtitleLabel("编辑任务" if self.task.id else "新建任务")
        title.setStyleSheet(f"""
            font-size: {AppleTheme.FONT_SIZE_SUBTITLE + 2}px;
            font-weight: 700;
            color: {AppleTheme.ACCENT};
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: rgba(166,226,42,30); margin: 0px;")
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        label_style = f"""
            font-size: {AppleTheme.FONT_SIZE_BODY}px;
            font-weight: 500;
            color: {AppleTheme.TEXT_SECONDARY};
        """

        name_label = QLabel("任务名称 *")
        name_label.setStyleSheet(label_style)
        self.name_edit = LineEdit()
        self.name_edit.setPlaceholderText("输入任务名称")
        form.addRow(name_label, self.name_edit)

        status_label = QLabel("状态")
        status_label.setStyleSheet(label_style)
        self.status_combo = ComboBox()
        self.status_combo.addItems(TaskStatus.values())
        form.addRow(status_label, self.status_combo)

        priority_label = QLabel("优先级")
        priority_label.setStyleSheet(label_style)
        self.priority_combo = ComboBox()
        self.priority_combo.addItems(Priority.labels())
        form.addRow(priority_label, self.priority_combo)

        progress_label = QLabel("进度")
        progress_label.setStyleSheet(label_style)
        self.progress_spin = SpinBox()
        self.progress_spin.setRange(0, 100)
        self.progress_spin.setSuffix("%")
        form.addRow(progress_label, self.progress_spin)

        start_label = QLabel("开始日期")
        start_label.setStyleSheet(label_style)
        self.start_date = DatePicker()
        form.addRow(start_label, self.start_date)

        due_label = QLabel("截止日期")
        due_label.setStyleSheet(label_style)
        self.due_date = DatePicker()
        form.addRow(due_label, self.due_date)

        risk_label = QLabel("风险")
        risk_label.setStyleSheet(label_style)
        self.risk_edit = LineEdit()
        self.risk_edit.setPlaceholderText("描述风险等级")
        form.addRow(risk_label, self.risk_edit)

        remarks_label = QLabel("备注")
        remarks_label.setStyleSheet(label_style)
        self.remarks_edit = TextEdit()
        self.remarks_edit.setPlaceholderText("详细备注...")
        self.remarks_edit.setFixedHeight(72)
        form.addRow(remarks_label, self.remarks_edit)

        layout.addLayout(form)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = PushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addSpacing(8)
        self.save_btn = PrimaryPushButton("保存")
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def _load_data(self):
        try:
            t = self.task
            self.name_edit.setText(t.name)
            self.status_combo.setCurrentIndex(
                TaskStatus.values().index(t.status) if t.status in TaskStatus.values() else 0
            )
            self.priority_combo.setCurrentIndex(
                t.priority - 1 if 1 <= t.priority <= 5 else 2
            )
            self.progress_spin.setValue(t.progress)
            if t.start_date:
                qd = QDate(t.start_date.year, t.start_date.month, t.start_date.day)
                self.start_date.setDate(qd)
            if t.due_date:
                qd = QDate(t.due_date.year, t.due_date.month, t.due_date.day)
                self.due_date.setDate(qd)
            self.risk_edit.setText(t.risk)
            self.remarks_edit.setPlainText(t.remarks)
        except Exception as e:
            InfoBar.error(title="加载错误", content=str(e),
                          orient=Qt.Orientation.Horizontal, isClosable=True,
                          position=InfoBarPosition.TOP, parent=self)

    def _on_save(self):
        try:
            name = self.name_edit.text().strip()
            if not name:
                InfoBar.warning(title="验证失败", content="任务名称不能为空",
                                orient=Qt.Orientation.Horizontal, isClosable=True,
                                position=InfoBarPosition.TOP, parent=self)
                return

            self.task.name = name
            self.task.status = TaskStatus.values()[self.status_combo.currentIndex()]
            self.task.priority = self.priority_combo.currentIndex() + 1
            self.task.progress = self.progress_spin.value()

            try:
                sd = self.start_date.date
                self.task.start_date = date(sd.year(), sd.month(), sd.day())
            except Exception:
                self.task.start_date = None

            try:
                dd = self.due_date.date
                self.task.due_date = date(dd.year(), dd.month(), dd.day())
            except Exception:
                self.task.due_date = None

            self.task.risk = self.risk_edit.text().strip()
            self.task.remarks = self.remarks_edit.toPlainText().strip()

            if self.task.status == TaskStatus.DONE.value:
                self.task.progress = 100

            self.accept()
        except Exception as e:
            InfoBar.error(title="保存失败", content=str(e),
                          orient=Qt.Orientation.Horizontal, isClosable=True,
                          position=InfoBarPosition.TOP, parent=self)

    def get_task(self) -> Task:
        return self.task
