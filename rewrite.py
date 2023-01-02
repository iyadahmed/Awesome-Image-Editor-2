from pathlib import Path

from PyQt6.QtCore import Qt, QRect, QDir, QStandardPaths
from PyQt6.QtGui import QImage, QPaintEvent, QPainter, QPainterPath, QImageReader, QImageWriter, QPalette
from PyQt6.QtWidgets import QApplication, QWidget, QTreeWidget, QTreeWidgetItem, QSplitter, QScrollArea, QFileDialog, \
    QHBoxLayout, QMenuBar, QMenu, QDialog, QMessageBox

# Item data roles
LayerDataRole = Qt.ItemDataRole.UserRole + 0

# Item types
ImageLayer = QTreeWidgetItem.ItemType.UserType + 0
ShapeLayer = QTreeWidgetItem.ItemType.UserType + 1


def create_image_file_dialog(accept_mode: QFileDialog.AcceptMode):
    dlg = QFileDialog()

    picture_locations = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.PicturesLocation)
    dlg.setDirectory(picture_locations[-1] if len(picture_locations) > 0 else QDir.currentPath())

    if accept_mode == QFileDialog.AcceptMode.AcceptOpen:
        supported_mime_types = QImageReader.supportedMimeTypes()
    else:
        supported_mime_types = QImageWriter.supportedMimeTypes()

    mime_type_filters = [mt.data().decode() for mt in supported_mime_types]

    supported_mime_types.sort()
    dlg.setMimeTypeFilters(mime_type_filters)
    dlg.selectMimeTypeFilter("image/png")
    dlg.setAcceptMode(accept_mode)
    if accept_mode == QFileDialog.AcceptMode.AcceptSave:
        dlg.setDefaultSuffix("png")

    return dlg


def get_item_data(item: QTreeWidgetItem):
    if item.type() == ImageLayer:
        return item.data(0, LayerDataRole)
    elif item.type() == ShapeLayer:
        return item.data(0, LayerDataRole)
    else:
        raise NotImplementedError


def get_item_data_rect(item_data):
    if isinstance(item_data, QImage):
        return item_data.rect()
    elif isinstance(item_data, QPainterPath):
        return item_data.boundingRect()
    else:
        raise NotImplementedError


def draw_item_data(painter: QPainter, item_data):
    if isinstance(item_data, QImage):
        painter.drawImage(item_data.rect(), item_data)
    elif isinstance(item_data, QPainterPath):
        painter.drawPath(item_data)
    else:
        raise NotImplementedError


class Canvas(QWidget):
    def __init__(self, tree_widget: QTreeWidget, width: int, height: int):
        super().__init__()
        self.setFixedSize(width, height)
        self._tree_widget = tree_widget
        self._tree_widget.itemChanged.connect(self.handle_item_change)
        self._scale_factor = 1.0

    def handle_item_change(self, item: QTreeWidgetItem, column: int):
        self.update()

    def iter_visible_layer_tree_items(self):
        for i in range(self._tree_widget.topLevelItemCount()):
            item = self._tree_widget.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Unchecked:
                continue
            yield item

    def render_visible_layers_to_qpainter(self, painter: QPainter):
        painter.save()
        painter.scale(self._scale_factor, self._scale_factor)
        for item in self.iter_visible_layer_tree_items():
            draw_item_data(painter, get_item_data(item))
        painter.restore()

    def render_visible_layers_to_image(self, filepath: str):
        # Create new empty image to render the scene into
        result = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        if result.isNull():
            QMessageBox.information(self, QApplication.applicationDisplayName(), f"Failed to create image in memory")
            return

        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        self.render_visible_layers_to_qpainter(painter)
        # End painter explicitly to avoid error "QPaintDevice: Cannot destroy paint device that is being painted"
        painter.end()
        result.save(filepath)

    def calc_visible_layers_bounding_rect(self):
        result = QRect()
        for item in self.iter_visible_layer_tree_items():
            rect = get_item_data_rect(get_item_data(item))
            result = result.united(rect)
        return result

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        self.render_visible_layers_to_qpainter(painter)


class LayersTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)

    def add_image_layer(self, layer_name: str, image: QImage):
        new_layer = QTreeWidgetItem(ImageLayer)
        new_layer.setData(0, LayerDataRole, image)
        new_layer.setText(0, layer_name)
        new_layer.setCheckState(0, Qt.CheckState.Checked)
        self.addTopLevelItem(new_layer)
        return new_layer


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        self.layers_tree_widget = LayersTreeWidget()

        # Canvas widget
        canvas_scroll_area = QScrollArea()
        self.canvas = Canvas(self.layers_tree_widget, 1280, 720)
        canvas_scroll_area.setWidget(self.canvas)
        canvas_scroll_area.setBackgroundRole(QPalette.ColorRole.Dark)
        canvas_scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        canvas_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        canvas_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Splitter widget
        splitter = QSplitter()
        splitter.addWidget(canvas_scroll_area)
        splitter.addWidget(self.layers_tree_widget)
        splitter.setStretchFactor(0, 2)  # Make canvas take more space by default

        layout.addWidget(splitter)

        # Setup menubar
        self._menu_bar = QMenuBar()
        layout.setMenuBar(self._menu_bar)
        self._file_menu = QMenu("File")
        self._file_menu.addAction("Import Image", self.import_image)
        self._file_menu.addAction("Export As Image", self.export_as_image)
        self._menu_bar.addMenu(self._file_menu)

    def import_image(self):
        dlg = create_image_file_dialog(QFileDialog.AcceptMode.AcceptOpen)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        filepath = dlg.selectedFiles()[0]
        reader = QImageReader(filepath)
        image = reader.read()
        if image.isNull():
            QMessageBox.information(self, QApplication.applicationDisplayName(),
                                    f"Failed to load image {QDir.toNativeSeparators(filepath)}: {reader.errorString()}")
            return

        layer_name = Path(filepath).stem
        self.layers_tree_widget.add_image_layer(layer_name, image)
        self.canvas.update()

    def export_as_image(self):
        dlg = create_image_file_dialog(QFileDialog.AcceptMode.AcceptSave)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        filepath = dlg.selectedFiles()[0]
        self.canvas.render_visible_layers_to_image(filepath)


def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.showMaximized()
    app.exec()


if __name__ == "__main__":
    main()
