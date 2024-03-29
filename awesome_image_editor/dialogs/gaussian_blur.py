from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)


class GaussianBlurDialog(QDialog):
    DEFAULT_RADIUS = 7.2
    MIN_RADIUS = 0.1
    MAX_RADIUS = 400.0

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gaussian Blur")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        layout = QHBoxLayout()
        self.setLayout(layout)

        (
            self.spinbox,
            slider,
            slider_spinbox_layout,
        ) = self.create_slider_spinbox_layout()
        layout.addLayout(slider_spinbox_layout)

        self.blur_radius_changed = self.spinbox.valueChanged

        buttons_layout = QVBoxLayout()
        layout.addLayout(buttons_layout)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.accept())
        buttons_layout.addWidget(ok_button)

        reset_button = QPushButton("Reset")
        buttons_layout.addWidget(reset_button)

        def on_reset_clicked():
            self.spinbox.setValue(self.DEFAULT_RADIUS)
            slider.setValue(int(self.DEFAULT_RADIUS * 10))

        self.preview_checkbox = QCheckBox("Preview")
        self.preview_checkbox.setChecked(True)
        self.preview_checkbox_toggled = self.preview_checkbox.toggled
        buttons_layout.addWidget(self.preview_checkbox)

        reset_button.clicked.connect(on_reset_clicked)

    def get_blur_radius(self):
        return self.spinbox.value()

    def is_preview_enabled(self):
        return self.preview_checkbox.isEnabled()

    def create_spinbox_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Radius:"))
        layout.addStretch(1)
        spinbox = QDoubleSpinBox()
        spinbox.setDecimals(1)
        spinbox.setRange(self.MIN_RADIUS, self.MAX_RADIUS)
        spinbox.setValue(self.DEFAULT_RADIUS)
        layout.addWidget(spinbox)
        return spinbox, layout

    def create_slider_widget(self):
        slider = QSlider()
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setRange(int(self.MIN_RADIUS * 10), int(self.MAX_RADIUS * 10))
        slider.setValue(int(self.DEFAULT_RADIUS * 10))
        return slider

    def create_slider_spinbox_layout(self):
        layout = QVBoxLayout()
        spinbox, spinbox_layout = self.create_spinbox_layout()
        layout.addLayout(spinbox_layout)

        slider = self.create_slider_widget()
        layout.addWidget(slider)

        def on_spinbox_value_change(value):
            clamped_value = min(max(value, self.MIN_RADIUS), self.MAX_RADIUS)
            new_slider_value = int(clamped_value * 10)
            slider.setValue(new_slider_value)

        def on_slider_move(value):
            spinbox.setValue(min(max(value / 10, self.MIN_RADIUS), self.MAX_RADIUS))

        slider.sliderMoved.connect(on_slider_move)
        spinbox.valueChanged.connect(on_spinbox_value_change)

        return spinbox, slider, layout
