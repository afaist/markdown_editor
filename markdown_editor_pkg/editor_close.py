"""Close handler — обработка закрытия окна."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class CloseHandler:
    """Обработчик события закрытия окна."""

    def __init__(self, editor: MarkdownEditorPyQt):
        self.editor = editor

    def on_close(self, event: QCloseEvent) -> None:
        """Обработка события закрытия окна."""
        if self.editor.is_dirty:
            msg = QMessageBox(self.editor)
            msg.setWindowTitle("Подтверждение выхода")
            msg.setText("Вы собираетесь выйти. Сохранить текущий файл?")
            msg.setStandardButtons(
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel
            )

            save_btn = msg.button(QMessageBox.StandardButton.Save)
            if save_btn:
                save_btn.setText("Сохранить")
            discard_btn = msg.button(QMessageBox.StandardButton.Discard)
            if discard_btn:
                discard_btn.setText("Без сохранения")
            cancel_btn = msg.button(QMessageBox.StandardButton.Cancel)
            if cancel_btn:
                cancel_btn.setText("Отмена")

            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Save:
                self.editor.file_ops.save_file()
                if self.editor.is_dirty:
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            else:
                event.accept()
        else:
            event.accept()
