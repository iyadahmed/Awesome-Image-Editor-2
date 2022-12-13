from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt

from .graphics_scene import AIEGraphicsScene
from .roles import ItemSelectionRole
from .tree_item import TreeItemProtocol


class RootItemParent:
    ...


class RootItem:
    """A proxy class to provide a root item for graphics scene"""

    def __init__(self, scene: AIEGraphicsScene):
        self.name = ""
        self._scene = scene

    def parentItem(self):
        return RootItemParent

    def get_thumbnail(self):
        ...

    def get_size_hint(self):
        ...

    def isSelected(self) -> bool:
        ...

    def setSelected(self, value: bool):
        ...

    def childItems(self):
        # FIXME: can lead to bad performance, implement a root item in a different way (use a group item for example)
        # but in that case, the scene has to be managed by the TreeModel
        return [
            item
            for item in self._scene.items(order=Qt.SortOrder.DescendingOrder)
            if item.parentItem() is None
        ]

    def isVisible(self) -> bool:
        ...

    def setVisible(self, value: bool):
        ...


class TreeModel(QAbstractItemModel):
    def __init__(self, scene: AIEGraphicsScene, parent=None):
        super().__init__(parent)
        self._scene = scene
        self._root_item = RootItem(scene)

        scene.itemAboutToBeAppended.connect(
            lambda i: self.beginInsertRows(QModelIndex(), i, i)
        )
        scene.itemAppended.connect(lambda: self.endInsertRows())

    def scene(self):
        return self._scene

    def columnCount(self, parent: QModelIndex = ...):
        return 1

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid():
            return None

        item = self.getItem(index)

        if item is None:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return item.name

        elif role == Qt.ItemDataRole.DecorationRole:
            return item.get_thumbnail()

        elif role == Qt.ItemDataRole.SizeHintRole:
            return item.get_size_hint()

        elif role == Qt.ItemDataRole.CheckStateRole:
            return (
                Qt.CheckState.Checked if item.isVisible() else Qt.CheckState.Unchecked
            )

        elif role == ItemSelectionRole:
            return item.isSelected()

    def setData_(self, index: QModelIndex, value, role: int = ...):
        item = self.getItem(index)
        if item is None:
            return False

        if role == ItemSelectionRole:
            item.setSelected(value)
            return True

        elif role == Qt.ItemDataRole.CheckStateRole:
            item.setVisible(Qt.CheckState(value) == Qt.CheckState.Checked)
            return True

        return False

    def setData(self, index: QModelIndex, value, role: int = ...) -> bool:
        is_data_changed = self.setData_(index, value, role)
        if is_data_changed:
            self.dataChanged.emit(index, index)
        return is_data_changed

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsUserCheckable
        )

    def getItem(self, index: QModelIndex):
        if index.isValid():
            item: TreeItemProtocol = index.internalPointer()
            if item:
                return item

        return None

    def index(self, row: int, column: int, parent: QModelIndex = ...):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentItem = self.getItem(parent)
        if parentItem is None:
            parentItem = self._root_item

        childItem = parentItem.childItems()[row]

        return self.createIndex(row, column, childItem)

    def row(self, item: TreeItemProtocol):
        parentItem = item.parentItem()
        if parentItem is None:
            parentItem = self._root_item

        if not isinstance(parentItem, RootItemParent):
            return parentItem.childItems().index(item)  # type: ignore

        return 0

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parentItem()

        if parentItem is None:
            # parent is root
            return QModelIndex()

        return self.createIndex(self.row(parentItem), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        parentItem = self.getItem(parent)

        if parentItem is None:
            # root, return number of scene top level items
            return len(self._root_item.childItems())
        else:
            return len(parentItem.childItems())
