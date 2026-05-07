"""限同层级拖拽排序的 QTreeWidget 子类。"""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional


class DragDropTreeWidget(QTreeWidget):
    """QTreeWidget 子类：仅允许同层级拖拽排序。"""

    orderChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropOverwriteMode(False)

    def dropEvent(self, event):
        dragged = self.currentItem()
        if not dragged:
            event.ignore()
            return

        target = self.itemAt(event.position().toPoint())

        # 获取被拖拽项的 parent_id (存储于 UserRole+100)
        dragged_parent = dragged.data(0, Qt.ItemDataRole.UserRole + 100)

        if target is None:
            # 拖到空白区域 → 同层末尾，允许
            super().dropEvent(event)
            self.orderChanged.emit()
            return

        # 获取目标项的 parent_id
        target_parent = target.data(0, Qt.ItemDataRole.UserRole + 100)

        # 只允许同父级间拖拽
        if dragged_parent != target_parent:
            event.ignore()
            return

        # 不允许拖到自身或其子项上
        if self._is_descendant(dragged, target):
            event.ignore()
            return

        super().dropEvent(event)
        self.orderChanged.emit()

    def _is_descendant(self, ancestor: QTreeWidgetItem, target: QTreeWidgetItem) -> bool:
        """检查 target 是否是 ancestor 的后代。"""
        item = target
        while item:
            if item == ancestor:
                return True
            item = item.parent()
        return False
