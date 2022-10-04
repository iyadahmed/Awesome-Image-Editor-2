from typing import Optional

from PyQt6.QtCore import pyqtSignal, QModelIndex, Qt, QAbstractItemModel
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene

from .items.base import BaseGraphicsItem


class QGraphicsSceneCustom(QGraphicsScene):
    itemAboutToBeAppended = pyqtSignal()
    itemAppended = pyqtSignal(QGraphicsItem)

    def addItem(self, item: QGraphicsItem) -> None:
        self.itemAboutToBeAppended.emit()
        super().addItem(item)
        self.itemAppended.emit(item)


class QGraphicsTreeItem:
    def __init__(self, graphics_item: Optional[BaseGraphicsItem], parent: Optional["QGraphicsTreeItem"]):
        self._parent = parent
        self._graphics_item = graphics_item
        self.childItems = []

    def append_child(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def child_count(self):
        return len(self.childItems)

    def data(self, role: int):
        if role == Qt.ItemDataRole.DisplayRole:
            return getattr(self._graphics_item, "name", "FAILED TO GET LAYER NAME!!")

        elif role == Qt.ItemDataRole.DecorationRole:
            return getattr(self._graphics_item, "get_thumbnail", lambda: None)()

        elif role == Qt.ItemDataRole.SizeHintRole:
            return getattr(self._graphics_item, "get_size_hint", lambda: None)()

    def parent(self):
        return self._parent

    def row(self):
        if self._parent:
            return self._parent.childItems.index(self)

        return 0


class TreeModel(QAbstractItemModel):
    def __init__(self, scene: QGraphicsSceneCustom, parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = QGraphicsTreeItem(None, None)
        for item in scene.items():
            self.rootItem.append_child(QGraphicsTreeItem(item, self.rootItem))

        scene.itemAboutToBeAppended.connect(
            lambda: self.beginInsertRows(QModelIndex(), self.rootItem.child_count(), self.rootItem.child_count()))
        scene.itemAppended.connect(self.item_appended)

    def item_appended(self, item):
        self.rootItem.append_child(QGraphicsTreeItem(item, self.rootItem))
        self.endInsertRows()

    def columnCount(self, parent: QModelIndex = ...):
        return 1

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid():
            return None
        item: QGraphicsTreeItem = index.internalPointer()
        return item.data(role)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def index(self, row: int, column: int, parent: QModelIndex = ...):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.rootItem:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = ...):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()
