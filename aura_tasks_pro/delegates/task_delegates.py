from typing import Optional

from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor
from ..utils.apple_theme import AppleTheme


class ProgressBarDelegate(QStyledItemDelegate):
    """可点击设置进度的进度条委托。"""

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
        # 与文本同层居中：上下各留 5px 边距
        bar_rect = rect.adjusted(8, 5, -8, -5)

        # 轨道
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#E5E7EB"))
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
            bar_rect = option.rect.adjusted(8, 5, -8, -5)
            if bar_rect.contains(event.pos()):
                click_x = event.pos().x() - bar_rect.x()
                new_progress = int(click_x / bar_rect.width() * 100)
                new_progress = max(0, min(100, new_progress))
                model.setData(index, new_progress, Qt.ItemDataRole.DisplayRole)
                return True
        return super().editorEvent(event, model, option, index)


class RiskIconDelegate(QStyledItemDelegate):
    """风险列委托 — 高风险红色警告标签。"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter: QPainter, option, index: QModelIndex):
        text = index.data(Qt.ItemDataRole.DisplayRole) or ""
        is_high = index.data(Qt.ItemDataRole.UserRole + 1) or False

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if is_high and text:
            badge_rect = option.rect.adjusted(2, 3, -2, -3)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 97, 136, 30))
            painter.drawRoundedRect(badge_rect, 3, 3)

            icon_rect = option.rect.adjusted(6, 0, 0, 0)
            icon_rect.setWidth(18)
            font = painter.font()
            font.setPixelSize(13)
            painter.setFont(font)
            painter.setPen(QColor(AppleTheme.DANGER))
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "⚠")

            text_rect = option.rect.adjusted(26, 0, -4, 0)
            font.setPixelSize(12)
            font.setWeight(600)
            painter.setFont(font)
            painter.setPen(QColor(AppleTheme.DANGER))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
        else:
            font = painter.font()
            font.setPixelSize(12)
            painter.setFont(font)
            painter.setPen(QColor(AppleTheme.TEXT_SECONDARY))
            painter.drawText(
                option.rect.adjusted(6, 0, 0, 0),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                text,
            )

        painter.restore()
