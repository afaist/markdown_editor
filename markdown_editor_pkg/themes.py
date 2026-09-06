"""Темы предпросмотра и редактора Markdown."""

from __future__ import annotations

from typing import ClassVar

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTextEdit


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

    THEMES_CSS: ClassVar[dict[str, str]] = {
        "light": """
        body {
            background-color: #ffffff;
            color: #333333;
            font-family: sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 { color: #2c3e50; }
        pre {
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            padding: 10px;
            color: #24292e;
            overflow-x: auto;
        }
        code {
            background-color: #f5f5f5;
            color: #d73a49;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        blockquote {
            border-left: 4px solid #ddd;
            margin: 0;
            padding-left: 16px;
            color: #666;
        }
        a { color: #0366d6; }
        hr { border: none; border-top: 1px solid #ddd; }
        table { border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 6px; }
        th { background-color: #f5f5f5; }
        """,
        "dark": """
        body {
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 { color: #569cd6; }
        pre {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            padding: 10px;
            color: #9cdcfe;
            overflow-x: auto;
        }
        code {
            background-color: #2d2d2d;
            color: #ce9178;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        blockquote {
            border-left: 4px solid #404040;
            margin: 0;
            padding-left: 16px;
            color: #aaaaaa;
        }
        a { color: #6a9fb5; }
        hr { border: none; border-top: 1px solid #404040; }
        table { border-collapse: collapse; }
        th, td { border: 1px solid #404040; padding: 6px; }
        th { background-color: #3d3d3d; }
        """,
        "contrast": """
        body {
            background-color: #000000;
            color: #ffffff;
            font-family: sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 { color: #00ffff; }
        pre {
            background-color: #1a1a1a;
            border: 1px solid #666666;
            padding: 10px;
            color: #ffffff;
            overflow-x: auto;
        }
        code {
            background-color: #1a1a1a;
            color: #00ffff;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        blockquote {
            border-left: 4px solid #666666;
            margin: 0;
            padding-left: 16px;
            color: #ffffff;
        }
        a { color: #00ffff; }
        hr { border: none; border-top: 1px solid #666666; }
        table { border-collapse: collapse; }
        th, td { border: 1px solid #666666; padding: 6px; }
        th { background-color: #2a2a2a; }
        """,
        "monokai": """
        body {
            background-color: #272822;
            color: #F8F8F2;
            font-family: sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 { color: #F92672; }
        pre {
            background-color: #1e1e1e;
            border: 1px solid #49483e;
            padding: 10px;
            color: #F8F8F2;
            overflow-x: auto;
        }
        code {
            background-color: #1e1e1e;
            color: #F8F8F2;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        blockquote {
            border-left: 4px solid #75715e;
            margin: 0;
            padding-left: 16px;
            color: #75715e;
        }
        a { color: #68C1D8; }
        hr { border: none; border-top: 1px solid #49483e; }
        table { border-collapse: collapse; }
        th, td { border: 1px solid #49483e; padding: 6px; }
        th { background-color: #3e3d32; }
        """,
        "dracula": """
        body {
            background-color: #282A36;
            color: #F8F8F2;
            font-family: sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 { color: #FF79C6; }
        pre {
            background-color: #1e1f29;
            border: 1px solid #6272a4;
            padding: 10px;
            color: #F8F8F2;
            overflow-x: auto;
        }
        code {
            background-color: #1e1f29;
            color: #F8F8F2;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        blockquote {
            border-left: 4px solid #6272a4;
            margin: 0;
            padding-left: 16px;
            color: #6272a4;
        }
        a { color: #8BE9FD; }
        hr { border: none; border-top: 1px solid #6272a4; }
        table { border-collapse: collapse; }
        th, td { border: 1px solid #6272a4; padding: 6px; }
        th { background-color: #44475a; }
        """,
        "one-dark": """
        body {
            background-color: #282C34;
            color: #ABB2BF;
            font-family: sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 { color: #E06C75; }
        pre {
            background-color: #1e2127;
            border: 1px solid #3E4451;
            padding: 10px;
            color: #ABB2BF;
            overflow-x: auto;
        }
        code {
            background-color: #1e2127;
            color: #E6C584;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        blockquote {
            border-left: 4px solid #5C6370;
            margin: 0;
            padding-left: 16px;
            color: #5C6370;
        }
        a { color: #61AFEF; }
        hr { border: none; border-top: 1px solid #3E4451; }
        table { border-collapse: collapse; }
        th, td { border: 1px solid #3E4451; padding: 6px; }
        th { background-color: #333842; }
        """,
        "github-dark": """
        body {
            background-color: #0D1117;
            color: #C9D1D9;
            font-family: sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 { color: #54AEFF; }
        pre {
            background-color: #161B22;
            border: 1px solid #30363D;
            padding: 10px;
            color: #C9D1D9;
            overflow-x: auto;
        }
        code {
            background-color: #161B22;
            color: #FFA00A;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        blockquote {
            border-left: 4px solid #30363D;
            margin: 0;
            padding-left: 16px;
            color: #8B949E;
        }
        a { color: #58A6FF; }
        hr { border: none; border-top: 1px solid #30363D; }
        table { border-collapse: collapse; }
        th, td { border: 1px solid #30363D; padding: 6px; }
        th { background-color: #161B22; }
        """,
        "solarized-dark": """
        body {
            background-color: #002B36;
            color: #839496;
            font-family: sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 { color: #B58900; }
        pre {
            background-color: #073642;
            border: 1px solid #586e75;
            padding: 10px;
            color: #839496;
            overflow-x: auto;
        }
        code {
            background-color: #073642;
            color: #2AA198;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        blockquote {
            border-left: 4px solid #586e75;
            margin: 0;
            padding-left: 16px;
            color: #586e75;
        }
        a { color: #2AA198; }
        hr { border: none; border-top: 1px solid #586e75; }
        table { border-collapse: collapse; }
        th, td { border: 1px solid #586e75; padding: 6px; }
        th { background-color: #073642; }
        """,
    }

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

    def get_preview_css(self) -> str:
        """Получить CSS-стили для текущей темы предпросмотра.

        Returns:
            CSS-строка для текущей темы (light/dark/contrast).
        """
        return self.THEMES_CSS.get(self.theme_name, self.THEMES_CSS["light"])

    def toggle_preview_theme(self) -> str:
        """Переключить тему предпросмотра. Возвращает новое имя темы."""
        current_idx = self.THEME_ORDER.index(self.theme_name)
        self.theme_name = self.THEME_ORDER[(current_idx + 1) % len(self.THEME_ORDER)]
        self._persist_theme()
        return self.theme_name

    def set_preview_theme(self, theme_name: str) -> None:
        """Установить тему предпросмотра."""
        if theme_name in self.THEMES_CSS:
            self.theme_name = theme_name
            self._persist_theme()

    # ─── QSS-темы (редактор) ──────────────────────────────────────────

    # Стили для редактора — хранятся отдельно
    EDITOR_STYLES: ClassVar[dict[str, str]] = {
        "light": """
            QTextEdit {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #666666;
                selection-color: #ffffff;
            }
        """,
        "dark": """
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                selection-background-color: #404040;
                selection-color: #ffffff;
            }
        """,
        "contrast": """
            QTextEdit {
                background-color: #000000;
                color: #ffffff;
                selection-background-color: #666666;
                selection-color: #ffffff;
            }
        """,
        "monokai": """
            QTextEdit {
                background-color: #272822;
                color: #F8F8F2;
                selection-background-color: #49483e;
                selection-color: #F8F8F2;
            }
        """,
        "dracula": """
            QTextEdit {
                background-color: #282A36;
                color: #F8F8F2;
                selection-background-color: #44475a;
                selection-color: #F8F8F2;
            }
        """,
        "one-dark": """
            QTextEdit {
                background-color: #282C34;
                color: #ABB2BF;
                selection-background-color: #3E4451;
                selection-color: #ABB2BF;
            }
        """,
        "github-dark": """
            QTextEdit {
                background-color: #0D1117;
                color: #C9D1D9;
                selection-background-color: #30363D;
                selection-color: #C9D1D9;
            }
        """,
        "solarized-dark": """
            QTextEdit {
                background-color: #002B36;
                color: #839496;
                selection-background-color: #073642;
                selection-color: #839496;
            }
        """,
    }

    def get_editor_style(self) -> str:
        """Получить QSS-стиль для текущей темы редактора.

        Returns:
            QSS-строка для текущей темы редактора.
        """
        base = self.EDITOR_STYLES.get(self.editor_theme, self.EDITOR_STYLES["light"])
        return base

    def toggle_editor_theme(self) -> str:
        """Переключить тему редактора. Возвращает новое имя темы."""
        current_idx = self.THEME_ORDER.index(self.editor_theme)
        self.editor_theme = self.THEME_ORDER[(current_idx + 1) % len(self.THEME_ORDER)]
        self._persist_editor_theme()
        return self.editor_theme

    def set_editor_theme(self, theme_name: str, text_edit: QTextEdit | None = None) -> None:
        """Установить тему редактора и применить стиль к QTextEdit."""
        if theme_name in self.EDITOR_STYLES:
            self.editor_theme = theme_name
            if text_edit is not None:
                text_edit.setStyleSheet(self.EDITOR_STYLES[theme_name])
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
        self._persist_font()

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
        self._persist_font()

    def set_font(self, family: str, size: int, text_edit: QTextEdit | None) -> None:
        """Установить шрифт и размер для QTextEdit."""
        self.font_family = family
        self.font_size = size
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
        if text_edit is not None:
            font = QFont(self._font_family, self._font_size)
            text_edit.setFont(font)
