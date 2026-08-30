"""Темы предпросмотра и редактора Markdown."""

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFontDatabase

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt


class ThemesManager:
    """Управление темами предпросмотра (CSS для WebView), редактора, шрифтами и размером шрифта."""

    # Стандартные шрифты (без системных)
    DEFAULT_FONTS: list[str] = ["Consolas", "Courier New", "Monaco", "Fira Code", "JetBrains Mono",
                     "Arial", "Times New Roman", "Verdana", "Georgia", "Ubuntu Mono",
                     "DejaVu Sans Mono", "Liberation Mono", "Menlo", "SF Mono"]

    # Минимальный и максимальный размер шрифта
    MIN_FONT_SIZE = 6
    MAX_FONT_SIZE = 72
    DEFAULT_FONT_SIZE = 11

    THEMES_CSS: dict[str, str] = {
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
    }

    THEME_ORDER: list[str] = ["light", "dark", "contrast"]

    def __init__(self) -> None:
        self.theme_name = "light"
        self.editor_theme = "light"
        # Шрифт и размер шрифта по умолчанию
        self._font_family = "Consolas"
        self._font_size = 11

    # ─── CSS-темы (предпросмотр) ───────────────────────────────────────

    def get_preview_css(self) -> str:
        """Получить CSS для темы предпросмотра."""
        return self.THEMES_CSS.get(self.theme_name, self.THEMES_CSS["light"])

    def toggle_preview_theme(self) -> str:
        """Переключить тему предпросмотра. Возвращает новое имя темы."""
        current_idx = self.THEME_ORDER.index(self.theme_name)
        self.theme_name = self.THEME_ORDER[(current_idx + 1) % len(self.THEME_ORDER)]
        return self.theme_name

    def set_preview_theme(self, theme_name: str) -> None:
        """Установить тему предпросмотра."""
        if theme_name in self.THEMES_CSS:
            self.theme_name = theme_name

    # ─── QSS-темы (редактор) ──────────────────────────────────────────

    def get_editor_style(self) -> str:
        """Получить QSS-стиль для редактора."""
        base = self.EDITOR_STYLES.get(self.editor_theme, self.EDITOR_STYLES["light"])
        return base

    def toggle_editor_theme(self) -> str:
        """Переключить тему редактора. Возвращает новое имя темы."""
        current_idx = self.THEME_ORDER.index(self.editor_theme)
        self.editor_theme = self.THEME_ORDER[(current_idx + 1) % len(self.THEME_ORDER)]
        return self.editor_theme

    # Стили для редактора — хранятся отдельно
    EDITOR_STYLES: dict[str, str] = {
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
    }

    def set_editor_theme(self, theme_name: str, text_edit: QTextEdit) -> None:
        """Установить тему редактора и применить стиль к QTextEdit."""
        if theme_name in self.EDITOR_STYLES:
            self.editor_theme = theme_name
            text_edit.setStyleSheet(self.EDITOR_STYLES[theme_name])
            # Применяем текущий шрифт и размер
            self._apply_font_to_edit(text_edit)

    # ─── Шрифт и размер шрифта ────────────────────────────────────────

    @property
    def font_family(self) -> str:
        """Текущее имя шрифта."""
        return self._font_family

    @font_family.setter
    def font_family(self, family: str) -> None:
        """Установить имя шрифта."""
        if family:
            self._font_family = family

    @property
    def font_size(self) -> int:
        """Текущий размер шрифта."""
        return self._font_size

    def _apply_font_to_edit(self, text_edit: QTextEdit) -> None:
        """Применить текущие параметры шрифта к QTextEdit."""
        if text_edit is None:
            return
        # Проверяем, является ли text_edit экземпляром QTextEdit, чтобы избежать ошибок типа
        if not hasattr(text_edit, 'font'):
            return
            
        font = text_edit.font()
        font.setFamily(self._font_family)
        font.setPointSize(self._font_size)
        text_edit.setFont(font)

    def set_font(self, family: str, size: int, text_edit: QTextEdit | None) -> None:
        """Установить шрифт и размер, применить к QTextEdit."""
        if text_edit is None:
            self._font_family = family
            self._font_size = size
            return

        self._font_family = family
        self._font_size = size
        self._apply_font_to_edit(text_edit)
            
    def increase_font(self, text_edit: QTextEdit, step: int = 1) -> int:
        """Увеличить размер шрифта. Возвращает новый размер."""
        self._font_size = min(self.MAX_FONT_SIZE, self._font_size + step)
        if text_edit is not None:
            self._apply_font_to_edit(text_edit)
        return self._font_size

    def decrease_font(self, text_edit: QTextEdit, step: int = 1) -> int:
        """Уменьшить размер шрифта. Возвращает новый размер."""
        self._font_size = max(self.MIN_FONT_SIZE, self._font_size - step)
        if text_edit is not None:
            self._apply_font_to_edit(text_edit)
        return self._font_size

    def get_available_fonts(self) -> list[str]:
        """Получить список доступных шрифтов: сначала DEFAULT_FONTS, затем системные."""
        db = QFontDatabase.families()
        # Сначала шрифты из списка, которые есть в системе
        result: list[str] = [f for f in self.DEFAULT_FONTS if f in db]
        # Затем все остальные системные шрифты (без дубликатов)
        
        for f in sorted(db):
            if f not in result:
                result.append(f)
        return result

    def reset_font_to_default(self, text_edit: QTextEdit | None) -> None:
        """Сбросить шрифт и размер к значениям по умолчанию."""
        self._font_family = "Consolas"
        self._font_size = 11
        if text_edit is not None:
            self._apply_font_to_edit(text_edit)
