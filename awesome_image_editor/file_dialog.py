from typing import Union

from PyQt6.QtCore import QDir, Qt
from PyQt6.QtWidgets import QFileDialog


def create_file_dialog(
    file_mode: QFileDialog.FileMode,
    default_directory: Union[str, QDir],
    name_filter: str,
    accept_mode: QFileDialog.AcceptMode,
):
    dlg = QFileDialog()
    dlg.setNameFilter(name_filter)
    dlg.setDirectory(default_directory)

    # Disable entire app while showing dialog
    dlg.setWindowModality(Qt.WindowModality.ApplicationModal)

    # Use Qt custom file dialog instead of system's native file dialog,
    # to avoid bug https://stackoverflow.com/a/12406457/8094047
    dlg.setOption(QFileDialog.Option.DontUseNativeDialog, True)

    dlg.setFileMode(file_mode)
    dlg.setAcceptMode(accept_mode)
    return dlg


def create_save_file_dialog(default_directory: Union[str, QDir], name_filter: str):
    return create_file_dialog(
        QFileDialog.FileMode.AnyFile,
        default_directory,
        name_filter,
        QFileDialog.AcceptMode.AcceptSave,
    )


def create_open_file_dialog(default_directory: Union[str, QDir], name_filter: str):
    return create_file_dialog(
        QFileDialog.FileMode.ExistingFile,
        default_directory,
        name_filter,
        QFileDialog.AcceptMode.AcceptOpen,
    )
