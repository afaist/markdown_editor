"""Theme and Font Handler — управление темами и шрифтами."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class ThemeFontHandler:
    """Обработчик тем предпросмотра/редактора и управления шрифтами."""

    def __init__(self, editor: MarkdownEditorPyQt):
        self.editor = editor

    # ─── Переключение тем ──────────────────────────────────────────────

    def toggle_theme(self) -> None:
        """Переключить тему предпросмотра."""
        new_theme = self.editor.theme_manager.toggle_preview_theme()
        self.editor.update_preview()
        if self.editor._statusbar_ref:
            self.editor._statusbar_ref.showMessage(f"Тема: {new_theme.capitalize()}")

    def set_theme(self, theme_name: str) -> None:
        """Установить тему предпросмотра."""
        self.editor.theme_manager.set_preview_theme(theme_name)
        self.editor.update_preview()
        if self.editor._statusbar_ref:
            self.editor._statusbar_ref.showMessage(f"Тема: {theme_name.capitalize()}")

    def toggle_editor_theme(self) -> None:
        """Переключить тему редактора."""
        new_theme = self.editor.theme_manager.toggle_editor_theme()
        self.editor.theme_manager.set_editor_theme(new_theme, self.editor.editor)
        if self.editor._statusbar_ref:
            self.editor._statusbar_ref.showMessage(f"Тема редактора: {new_theme.capitalize()}")

    def set_editor_theme(self, theme_name: str) -> None:
        """Установить тему редактора."""
        self.editor.theme_manager.set_editor_theme(theme_name, self.editor.editor)
        if self.editor._statusbar_ref:
            self.editor._statusbar_ref.showMessage(f"Тема редактора: {theme_name.capitalize()}")

    # ─── Шрифты ─────────────────────────────────────────────────────────

    def on_font_changed(self, family: str) -> None:
        """Обработка изменения шрифта из комбобокса."""
        self.editor.theme_manager.set_font(
            family, self.editor.theme_manager.font_size, self.editor.editor
        )
        self._update_font_size_label()
        if self.editor._statusbar_ref:
            self.editor._statusbar_ref.showMessage(
                f"Шрифт: {family}, размер: {self.editor.theme_manager.font_size}"
            )

    def increase_font(self) -> None:
        """Увеличить размер шрифта."""
        new_size = self.editor.theme_manager.increase_font(self.editor.editor)
        self._update_font_size_label()
        if self.editor._statusbar_ref:
            self.editor._statusbar_ref.showMessage(f"Размер шрифта: {new_size}")

    def decrease_font(self) -> None:
        """Уменьшить размер шрифта."""
        new_size = self.editor.theme_manager.decrease_font(self.editor.editor)
        self._update_font_size_label()
        if self.editor._statusbar_ref:
            self.editor._statusbar_ref.showMessage(f"Размер шрифта: {new_size}")

    def reset_font(self) -> None:
        """Сбросить шрифт к значениям по умолчанию."""
        self.editor.theme_manager.reset_font_to_default(self.editor.editor)
        if self.editor.font_combo:
            font_idx = self.editor.font_combo.findText("Consolas", Qt.MatchFlag.MatchExactly)
            if font_idx >= 0:
                self.editor.font_combo.setCurrentIndex(font_idx)
            else:
                for default_font in self.editor.theme_manager.DEFAULT_FONTS:
                    idx = self.editor.font_combo.findText(default_font, Qt.MatchFlag.MatchExactly)
                    if idx >= 0:
                        self.editor.font_combo.setCurrentIndex(idx)
                        break
                else:
                    if self.editor.font_combo.count() > 0:
                        self.editor.font_combo.setCurrentIndex(0)
                        self.editor.theme_manager._font_family = (
                            self.editor.font_combo.currentText()
                        )
                        self._update_font_size_label()
        if self.editor._statusbar_ref:
            self.editor._statusbar_ref.showMessage(
                f"Шрифт сброшен: {self.editor.theme_manager.font_family}, "
                f"размер: {self.editor.theme_manager.font_size}"
            )

    def _update_font_size_label(self) -> None:
        """Обновить метку с размером шрифта."""
        if self.editor.font_size_label:
            self.editor.font_size_label.setText(str(self.editor.theme_manager.font_size))
