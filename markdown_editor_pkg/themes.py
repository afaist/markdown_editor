"""Темы предпросмотра и редактора Markdown."""

from __future__ import annotations

from typing import ClassVar

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTextEdit

from markdown_editor_pkg.themes_loader import load_editor_themes, load_preview_themes


class ThemesManager:
    """Управление темами предпросмотра (CSS для WebView), редактора, шрифтами и размером шрифта."""

    # Стандартные шрифты (без системных)
    DEFAULT_FONTS: ClassVar[list[str]] = [
        "Consolas",
        "Courier New",
        "Monaco",
        "Fira Code",
        "JetBrains Mono",
        "Arial",
        "Times New Roman",
        "Verdana",
        "Georgia",
        "Ubuntu Mono",
        "DejaVu Sans Mono",
        "Liberation Mono",
        "Menlo",
        "SF Mono",
    ]

    # Минимальный и максимальный размер шрифта
    MIN_FONT_SIZE = 6
    MAX_FONT_SIZE = 72
    DEFAULT_FONT_SIZE = 11

    THEME_ORDER: ClassVar[list[str]] = [
        "light",
        "dark",
        "contrast",
        "monokai",
        "dracula",
        "one-dark",
        "github-dark",
        "solarized-dark",
    ]

    def __init__(self) -> None:
        """Инициализация менеджера тем с настройками по умолчанию."""
        self.theme_name = "light"
        self.editor_theme = "light"
        # Шрифт и размер шрифта по умолчанию
        self._font_family = "Consolas"
        self._font_size = 11

    # ─── Персистентность ──────────────────────────────────────────────

    def _persist_theme(self) -> None:
        """Сохранить текущую тему предпросмотра в Settings."""
        from markdown_editor_pkg.settings import Settings

        Settings().set("theme", self.theme_name)

    def _persist_editor_theme(self) -> None:
        """Сохранить текущую тему редактора в Settings."""
        from markdown_editor_pkg.settings import Settings

        Settings().set("editor_theme", self.editor_theme)

    def _persist_font(self) -> None:
        """Сохранить текущий шрифт и размер в Settings."""
        from markdown_editor_pkg.settings import Settings

        Settings().set("editor_font", self._font_family)
        Settings().set("editor_font_size", self._font_size)

    # ─── CSS-темы (предпросмотр) ───────────────────────────────────────

    @classmethod
    def _get_themes_css(cls) -> dict[str, str]:
        """Load preview CSS themes from files."""
        return load_preview_themes()

    def get_preview_css(self) -> str:
        """Получить CSS-стили для текущей темы предпросмотра.

        Returns:
            CSS-строка для текущей темы (light/dark/contrast).
        """
        return self._get_themes_css().get(self.theme_name, self._get_themes_css()["light"])

    def toggle_preview_theme(self) -> str:
        """Переключить тему предпросмотра. Возвращает новое имя темы."""
        current_idx = self.THEME_ORDER.index(self.theme_name)
        self.theme_name = self.THEME_ORDER[(current_idx + 1) % len(self.THEME_ORDER)]
        self._persist_theme()
        return self.theme_name

    def set_preview_theme(self, theme_name: str, *, persist: bool = True) -> None:
        """Установить тему предпросмотра.

        Args:
            theme_name: Имя темы.
            persist: Сохранять ли тему в Settings (по True).
        """
        if theme_name in self._get_themes_css():
            self.theme_name = theme_name
            if persist:
                self._persist_theme()

    # ─── QSS-темы (редактор) ──────────────────────────────────────────

    @classmethod
    def _get_editor_styles(cls) -> dict[str, str]:
        """Load editor QSS themes from files."""
        return load_editor_themes()

    def get_editor_style(self) -> str:
        """Получить QSS-стиль для текущей темы редактора.

        Returns:
            QSS-строка для текущей темы редактора.
        """
        base = self._get_editor_styles().get(self.editor_theme, self._get_editor_styles()["light"])
        return base

    def toggle_editor_theme(self) -> str:
        """Переключить тему редактора. Возвращает новое имя темы."""
        current_idx = self.THEME_ORDER.index(self.editor_theme)
        self.editor_theme = self.THEME_ORDER[(current_idx + 1) % len(self.THEME_ORDER)]
        self._persist_editor_theme()
        return self.editor_theme

    def set_editor_theme(
        self, theme_name: str, text_edit: QTextEdit | None = None, *, persist: bool = True
    ) -> None:
        """Установить тему редактора и применить стиль к QTextEdit.

        Args:
            theme_name: Имя темы.
            text_edit: Виджет QTextEdit для применения стиля.
            persist: Сохранять ли тему в Settings (по True).
        """
        if theme_name in self._get_editor_styles():
            self.editor_theme = theme_name
            if text_edit is not None:
                text_edit.setStyleSheet(self._get_editor_styles()[theme_name])
            if persist:
                self._persist_editor_theme()

    # ─── Шрифты ───────────────────────────────────────────────────────

    @property
    def font_family(self) -> str:
        """Получить текущее семейство шрифта."""
        return self._font_family

    @font_family.setter
    def font_family(self, value: str) -> None:
        """Установить семейство шрифта."""
        self._font_family = value

    def get_available_fonts(self) -> list[str]:
        """Получить список доступных шрифтов."""
        return list(self.DEFAULT_FONTS)

    @property
    def font_size(self) -> int:
        """Получить текущий размер шрифта."""
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        """Установить размер шрифта с ограничением."""
        self._font_size = max(self.MIN_FONT_SIZE, min(self.MAX_FONT_SIZE, value))

    def set_font(
        self, family: str, size: int, text_edit: QTextEdit | None, *, persist: bool = True
    ) -> None:
        """Установить шрифт и размер для QTextEdit.

        Args:
            family: Семейство шрифта.
            size: Размер шрифта.
            text_edit: Виджет QTextEdit для применения шрифта.
            persist: Сохранять ли шрифт в Settings (по True).
        """
        if persist:
            self._font_family = family
            self._font_size = size
            self._persist_font()
        else:
            self._font_family = family
            self._font_size = size
        if text_edit is not None:
            font = QFont(family, size)
            text_edit.setFont(font)

    def increase_font(self, text_edit: QTextEdit | None) -> int:
        """Увеличить размер шрифта на 1. Возвращает новый размер."""
        if self.font_size < self.MAX_FONT_SIZE:
            self.font_size += 1
        if text_edit is not None:
            font = QFont(self.font_family, self.font_size)
            text_edit.setFont(font)
        return self.font_size

    def decrease_font(self, text_edit: QTextEdit | None) -> int:
        """Уменьшить размер шрифта на 1. Возвращает новый размер."""
        if self.font_size > self.MIN_FONT_SIZE:
            self.font_size -= 1
        if text_edit is not None:
            font = QFont(self.font_family, self.font_size)
            text_edit.setFont(font)
        return self.font_size

    def reset_font_to_default(self, text_edit: QTextEdit | None) -> None:
        """Сбросить шрифт и размер к значениям по умолчанию."""
        self._font_family = self.DEFAULT_FONTS[0]
        self._font_size = self.DEFAULT_FONT_SIZE
        self._persist_font()
        if text_edit is not None:
            font = QFont(self._font_family, self._font_size)
            text_edit.setFont(font)
