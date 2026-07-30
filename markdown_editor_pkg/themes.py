"""Темы предпросмотра и редактора Markdown."""

from PyQt6.QtWidgets import QTextEdit


class ThemesManager:
    """Управление темами предпросмотра (CSS для WebView) и редактора."""

    THEMES_CSS = {
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

    EDITOR_STYLES = {
        "light": """
            QTextEdit {
                font-family: Arial, sans-serif;
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

    THEME_ORDER = ["light", "dark", "contrast"]

    def __init__(self):
        self.theme_name = "light"
        self.editor_theme = "light"

    def get_preview_css(self) -> str:
        """Получить CSS для темы предпросмотра."""
        return self.THEMES_CSS.get(self.theme_name, self.THEMES_CSS["light"])

    def get_editor_style(self) -> str:
        """Получить QSS-стиль для редактора."""
        return self.EDITOR_STYLES.get(self.editor_theme, self.EDITOR_STYLES["light"])

    def toggle_preview_theme(self) -> str:
        """Переключить тему предпросмотра. Возвращает новое имя темы."""
        current_idx = self.THEME_ORDER.index(self.theme_name)
        self.theme_name = self.THEME_ORDER[(current_idx + 1) % len(self.THEME_ORDER)]
        return self.theme_name

    def set_preview_theme(self, theme_name: str) -> None:
        """Установить тему предпросмотра."""
        if theme_name in self.THEMES_CSS:
            self.theme_name = theme_name

    def toggle_editor_theme(self) -> str:
        """Переключить тему редактора. Возвращает новое имя темы."""
        current_idx = self.THEME_ORDER.index(self.editor_theme)
        self.editor_theme = self.THEME_ORDER[(current_idx + 1) % len(self.THEME_ORDER)]
        return self.editor_theme

    def set_editor_theme(self, theme_name: str, text_edit: QTextEdit) -> None:
        """Установить тему редактора и применить стиль к QTextEdit."""
        if theme_name in self.EDITOR_STYLES:
            self.editor_theme = theme_name
            text_edit.setStyleSheet(self.EDITOR_STYLES[theme_name])
