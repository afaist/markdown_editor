"""Session Handler — управление сессиями."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

from markdown_editor_pkg.session_manager import SessionManager

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class SessionHandler:
    """Обработчик сессий: сохранение/загрузка последнего файла."""

    def __init__(self, editor: MarkdownEditorPyQt):
        self.editor = editor

    def save_session(self, filepath: str) -> None:
        """Сохранить путь к файлу в сессии."""
        SessionManager.save(filepath)

    def load_session(self) -> None:
        """Загрузить последнюю сессию (открыть последний файл)."""
        last_file = SessionManager.load()
        if last_file and os.path.exists(last_file):
            self.editor.preview_timer.stop()
            try:
                with open(last_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor._set_editor_text_without_dirty(content)
                self.editor.current_file = last_file
                self.editor.is_dirty = False
                self.editor.update_preview()
                self.editor.update_char_count()
                self.editor.update_file_status()
            except (OSError, UnicodeDecodeError):
                logger.exception("Ошибка при загрузке сессии")
