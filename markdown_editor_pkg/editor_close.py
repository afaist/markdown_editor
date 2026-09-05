"""Close handler — window close processing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMessageBox

from markdown_editor_pkg.i18n import tr

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class CloseHandler:
    """Window close event handler."""

    def __init__(self, editor: MarkdownEditorPyQt):
        self.editor = editor

    def on_close(self, event: QCloseEvent) -> None:
        """Handle the window close event."""
        if self.editor.is_dirty:
            msg = QMessageBox(self.editor)
            msg.setWindowTitle(tr("Confirm Exit"))
            msg.setText(tr("You are about to exit. Save the current file?"))
            msg.setStandardButtons(
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel
            )

            save_btn = msg.button(QMessageBox.StandardButton.Save)
            if save_btn:
                save_btn.setText(tr("Save"))
            discard_btn = msg.button(QMessageBox.StandardButton.Discard)
            if discard_btn:
                discard_btn.setText(tr("Discard"))
            cancel_btn = msg.button(QMessageBox.StandardButton.Cancel)
            if cancel_btn:
                cancel_btn.setText(tr("Cancel"))

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
