# markdown_editor_pyqt.py
# Markdown Editor (PyQt6 Version)
# Основной модуль приложения

import sys
import re
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path

# Сначала идутQtCore, потом QtGui, а QtWidgets — последними
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QFont, QFontDatabase, QTextCharFormat, QTextCursor, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QSplitter,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QToolBar,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QLabel,
    QTabWidget,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from PyQt6.QtGui import QKeySequence, QAction


class MarkdownEditorPyQt(QMainWindow):
    """Основной класс редактора Markdown с предпросмотром на PyQt6"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Editor (PyQt6)")
        self.resize(1200, 800)

        # Переменные состояния
        self.current_file = None
        self.is_dirty = False
        self.auto_save_enabled = True
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.save_file)
        self.auto_save_timer.setSingleShot(True)
        self.preview_html = ""

        # Кэш для LaTeX формул
        self.display_math_cache = []
        self.inline_math_cache = []

        # Темы предпросмотра
        self.theme_name = "light"
        self.themes = {
            "light": self._get_light_css(),
            "dark": self._get_dark_css(),
            "contrast": self._get_contrast_css(),
        }

        # Темы редактора
        self.editor_theme = "light"

        # Инициализация интерфейса
        self.init_ui()
        self.setup_toolbar()
        self.setup_menu()
        self.setup_bindings()

        # Таймер для предпросмотра (должен быть ДО load_last_session)
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)

        # Загрузка последней сессии
        self.load_last_session()


    def _get_light_css(self):
        return """
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
        """

    def _get_dark_css(self):
        return """
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
        """

    def _get_contrast_css(self):
        return """
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
        """


    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Центральный виджет с разделенным окном
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        # Панель редактора
        self.editor_frame = QFrame()
        editor_layout = QVBoxLayout()
        editor_layout.setSpacing(0)  # Убираем отступы между элементами
        editor_layout.setContentsMargins(0, 0, 0, 0)  # Убираем внутренние отступы
        self.editor_frame.setLayout(editor_layout)

        # Метка редактора
        editor_label = QLabel("Редактор Markdown")
        editor_label.setStyleSheet("background-color: #f0f0f0; color: #333333;")
        editor_label.setMinimumHeight(25)  # Фиксируем минимальную высоту
        editor_label.setMaximumHeight(25)  # Фиксируем максимальную высоту
        editor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем текст
        editor_layout.addWidget(editor_label)

        # Текстовое поле редактора
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 11))
        self.set_editor_theme("light")  # ✅ Устанавливаем стиль
        editor_layout.addWidget(self.editor)

        self.splitter.addWidget(self.editor_frame)

        # Панель предпросмотра
        self.preview_frame = QFrame()
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(0)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_frame.setLayout(preview_layout)

        # Метка предпросмотра
        preview_label = QLabel("Предпросмотр")
        preview_label.setStyleSheet("background-color: #f0f0f0; color: #333333;")
        preview_label.setMinimumHeight(25)
        preview_label.setMaximumHeight(25)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_label)

        # WebEngineView для предпросмотра
        self.preview = QWebEngineView()
        preview_layout.addWidget(self.preview)

        self.splitter.addWidget(self.preview_frame)

        # Установка начального положения разделителя
        self.splitter.setSizes([600, 600])

        # Строка состояния
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Счётчики
        self.char_count_label = QLabel("Символов: 0")
        self.word_count_label = QLabel("Слов: 0")
        self.statusbar.addPermanentWidget(self.char_count_label)
        self.statusbar.addPermanentWidget(self.word_count_label)

    def setup_toolbar(self):
        """Настройка панели инструментов"""
        toolbar = QToolBar("Форматирование")
        self.addToolBar(toolbar)

        # Кнопки форматирования
        actions = [
            ("Заголовок 1", lambda: self.insert_text("# ")),
            ("Заголовок 2", lambda: self.insert_text("## ")),
            ("Жирный", self.insert_bold),
            ("Курсив", self.insert_italic),
            ("Список", self.insert_unordered_list),
            ("Цитата", lambda: self.insert_text("> ")),
            ("Код", lambda: self.insert_text("```\n```")),
            ("LaTeX inline", lambda: self.insert_text("$")),
            ("LaTeX block", lambda: self.insert_text("$$\n$$")),
            ("Ссылка", self.insert_link),
            ("Изображение", self.insert_image),  # ✅ Добавлена кнопка
            ("Тема", self.toggle_theme),
            ("Тема редактора", self.toggle_editor_theme),  # ✅ Добавим кнопку
        ]

        for text, callback in actions:
            action = QAction(text, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)

        toolbar.addSeparator()

        # Кнопки файлов
        file_actions = [
            ("Открыть", self.open_file),
            ("Сохранить", self.save_file),
            ("Экспорт в PDF", self.export_to_pdf),
        ]

        for text, callback in file_actions:
            action = QAction(text, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)

    def setup_menu(self):
        """Настройка меню"""

        menubar = self.menuBar()
        if menubar is not None:
            # Файл
            file_menu = menubar.addMenu("Файл")
            if file_menu is not None:
                file_menu.addAction(
                    QAction(
                        "Новый",
                        self,
                        triggered=self.new_file,
                        shortcut=QKeySequence.StandardKey.New,
                    )
                )
                file_menu.addAction(
                    QAction(
                        "Открыть",
                        self,
                        triggered=self.open_file,
                        shortcut=QKeySequence.StandardKey.Open,
                    )
                )
                file_menu.addAction(
                    QAction(
                        "Сохранить",
                        self,
                        triggered=self.save_file,
                        shortcut=QKeySequence.StandardKey.Save,
                    )
                )
                file_menu.addAction(
                    QAction("Сохранить как...", self, triggered=self.save_file_as)
                )
                file_menu.addSeparator()
                file_menu.addAction(
                    QAction(
                        "Закрыть",
                        self,
                        triggered=self.close,
                        shortcut=QKeySequence.StandardKey.Close,
                    )
                )
                file_menu.addSeparator()
                file_menu.addAction(
                    QAction("Экспорт в HTML", self, triggered=self.export_to_html)
                )
                file_menu.addAction(
                    QAction("Экспорт в PDF", self, triggered=self.export_to_pdf)
                )
                file_menu.addSeparator()
                file_menu.addAction(
                    QAction(
                        "Выход",
                        self,
                        triggered=self.close,
                        shortcut=QKeySequence.StandardKey.Quit,
                    )
                )

            # Правка
            edit_menu = menubar.addMenu("Правка")
            if edit_menu is None:
                return
            edit_menu.addAction(
                QAction(
                    "Отменить",
                    self,
                    triggered=self.editor.undo,
                    shortcut=QKeySequence.StandardKey.Undo,
                )
            )
            edit_menu.addAction(
                QAction(
                    "Повторить",
                    self,
                    triggered=self.editor.redo,
                    shortcut=QKeySequence.StandardKey.Redo,
                )
            )
            edit_menu.addSeparator()
            edit_menu.addAction(
                QAction(
                    "Вырезать",
                    self,
                    triggered=self.editor.cut,
                    shortcut=QKeySequence.StandardKey.Cut,
                )
            )
            edit_menu.addAction(
                QAction(
                    "Копировать",
                    self,
                    triggered=self.editor.copy,
                    shortcut=QKeySequence.StandardKey.Copy,
                )
            )
            edit_menu.addAction(
                QAction(
                    "Вставить",
                    self,
                    triggered=self.editor.paste,
                    shortcut=QKeySequence.StandardKey.Paste,
                )
            )
            edit_menu.addSeparator()
            edit_menu.addAction(
                QAction(
                    "Найти и заменить",
                    self,
                    triggered=self.find_replace,
                    shortcut=QKeySequence.StandardKey.Find,
                )
            )
            # ✅ Добавляем пункт в меню Правка
            edit_menu.addSeparator()
            edit_menu.addAction(
                QAction("Вставить изображение...", self, triggered=self.insert_image)
            )

            # Вид
            view_menu = menubar.addMenu("Вид")
            if view_menu is None:
                return
            view_menu.addAction(
                QAction("Обновить предпросмотр", self, triggered=self.update_preview)
            )
            # В setup_menu():
            view_menu.addAction(
                QAction(
                    "Тема: светлая", self, triggered=lambda: self.set_theme("light")
                )
            )
            view_menu.addAction(
                QAction("Тема: тёмная", self, triggered=lambda: self.set_theme("dark"))
            )
            view_menu.addAction(
                QAction(
                    "Тема: контрастная",
                    self,
                    triggered=lambda: self.set_theme("contrast"),
                )
            )

            # Или в setup_menu():
            view_menu.addAction(
                QAction(
                    "Тема редактора: светлая",
                    self,
                    triggered=lambda: self.set_editor_theme("light"),
                )
            )
            view_menu.addAction(
                QAction(
                    "Тема редактора: тёмная",
                    self,
                    triggered=lambda: self.set_editor_theme("dark"),
                )
            )
            view_menu.addAction(
                QAction(
                    "Тема редактора: контрастная",
                    self,
                    triggered=lambda: self.set_editor_theme("contrast"),
                )
            )

            # Справка
            help_menu = menubar.addMenu("Справка")
            if help_menu is None:
                return
            help_menu.addAction(QAction("О программе", self, triggered=self.show_about))

    def setup_bindings(self):
        """Настройка обработчиков событий"""
        # Автосохранение при изменении текста
        self.editor.textChanged.connect(self.on_text_change)

        # Обновление счётчиков
        self.editor.textChanged.connect(self.update_char_count)

    def on_text_change(self):
        """Обработка изменения текста для автосохранения и обновления предпросмотра"""

        self.is_dirty = True
        self.update_char_count()

        # Перезапуск таймера автосохранения
        if self.auto_save_enabled and self.current_file:
            self.auto_save_timer.start(3000)  # 3 секунды

        # Перезапуск таймера предпросмотра
        self.preview_timer.stop()
        self.preview_timer.start(300)  # 300 мс

    def update_preview(self):
        markdown_text = self.editor.toPlainText()
        html = self.render_markdown(markdown_text, theme_name=self.theme_name)
        self.preview_html = html

        base_url = QUrl.fromLocalFile(os.path.dirname(__file__))
        self.preview.setHtml(html, base_url)

        self.statusbar.showMessage("Предпросмотр обновлён")

# ... existing code ...
    def render_markdown(self, text, theme_name="light"):
        """Рендеринг Markdown в HTML с поддержкой LaTeX (включая блоки кода)"""
        # Сброс кэша формул
        self.display_math_cache = []
        self.inline_math_cache = []

        # Обработка LaTeX-формул до конвертации Markdown
        processed_text = self.process_latex_before_markdown(text)

        # Конвертация Markdown в HTML
        import markdown

        md = markdown.Markdown(
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.codehilite",
                "markdown.extensions.tables",
                "markdown.extensions.toc",
            ]
        )

        html_content = md.convert(processed_text)

        # Функция восстановления для обычных случаев
        def restore_normal(match):
            index = int(match.group(1))
            if index < len(self.display_math_cache):
                return f"$${self.display_math_cache[index]}$$"
            return match.group(0)

        def restore_inline_normal(match):
            index = int(match.group(1))
            if index < len(self.inline_math_cache):
                return f"${self.inline_math_cache[index]}$"
            return match.group(0)

        # Функция восстановления для экранированных случаев (внутри codehilite)
        def restore_escaped(match):
            index = int(match.group(1))
            if index < len(self.display_math_cache):
                return f"$${self.display_math_cache[index]}$$"
            return match.group(0)

        def restore_inline_escaped(match):
            index = int(match.group(1))
            if index < len(self.inline_math_cache):
                return f"${self.inline_math_cache[index]}$"
            return match.group(0)

        # 1. Сначала восстанавливаем обычные комментарии (если они не внутри codehilite или если кодихайт не экранировал)
        html_content = re.sub(
            r"<!--\s*display-math-(\d+)\s*-->", restore_normal, html_content
        )
        html_content = re.sub(
            r"<!--\s*inline-math-(\d+)\s*-->", restore_inline_normal, html_content
        )

        # 2. Затем восстанавливаем экранированные комментарии (которые остались внутри <code>)
        html_content = re.sub(
            r"&lt;!--\s*display-math-(\d+)\s*--&gt;", restore_escaped, html_content
        )
        html_content = re.sub(
            r"&lt;!--\s*inline-math-(\d+)\s*--&gt;",
            restore_inline_escaped,
            html_content,
        )

        # Локальные пути к файлам KaTeX
        base_dir = os.path.dirname(__file__)
        katex_css = os.path.join(base_dir, "katex", "katex.min.css")
        katex_js = os.path.join(base_dir, "katex", "katex.min.js")
        auto_render_js = os.path.join(base_dir, "katex", "auto-render.min.js")

        # Получаем CSS-стили (теперь они без тегов <style>)
        theme_css = self.themes.get(theme_name, self.themes["light"])

        # Стили для печати и колонтитулов
        # Теперь весь CSS будет обернут в ОДИН тег <style> в конце
        print_styles = f"""
        <style>
            /* Базовые стили */
            {theme_css}

            /* Стили для печати/PDF */
            @media print {{
                @page {{
                    size: A4;
                    margin: 2cm 2.5cm 2cm 2.5cm;
                    
                    /* Попытка явного задания колонтитулов */
                    @top-center {{
                        content: string(title);
                        font-size: 9px;
                        color: #888;
                    }}
                    @bottom-center {{
                        content: "Страница " counter(page) " из " counter(pages);
                        font-size: 9px;
                        color: #888;
                    }}
                }}
                
                /* Заголовки не должны разрываться от текста */
                h1, h2, h3, h4, h5, h6 {{
                    page-break-after: avoid;
                    orphans: 2;
                    widows: 2;
                }}
                
                /* Новая страница перед каждым h1 */
                h1 {{
                    page-break-before: always;
                }}
                /* Исключаем первую страницу */
                body > h1:first-child {{
                    page-break-before: auto;
                }}
                
                /* Элементы не должны разрываться */
                table, img, pre {{
                    page-break-inside: avoid;
                }}
                
                /* Принудительная печать фонов и цветов */
                body {{
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
                
                /* Убираем все лишнее */
                body {{
                    margin: 0;
                    padding: 0;
                }}
            }}
        </style>
        """

        # Важно: добавляем мету для заголовка, если мы используем string(title)
        # Но проще использовать простой текст в @page, как было.
        # В QtWebEngine string() может не поддерживаться в @page.
        # Вернемся к простому тексту, но убедимся, что нет конфликтов.

        # Исправленная версия print_styles для максимальной совместимости с QtWebEngine:
        print_styles = f"""
        <style>
            /* Базовые стили */
            {theme_css}

            /* Стили для печати/PDF */
            @media print {{
                @page {{
                    size: A4;
                    margin: 2cm 2.5cm 2cm 2.5cm;
                    
                    /* Попытка явного задания колонтитулов */
                    @top-center {{
                        content: string(title);
                        font-size: 9px;
                        color: #888;
                    }}
                    @bottom-center {{
                        content: "Страница " counter(page) " из " counter(pages);
                        font-size: 9px;
                        color: #888;
                    }}
                }}
                
                /* Заголовки не должны разрываться от текста */
                h1, h2, h3, h4, h5, h6 {{
                    page-break-after: avoid;
                    orphans: 2;
                    widows: 2;
                }}
                
                /* Новая страница перед каждым h1 */
                h1 {{
                    page-break-before: always;
                }}
                /* Исключаем первую страницу */
                body > h1:first-child {{
                    page-break-before: auto;
                }}
                
                /* Элементы не должны разрываться */
                table, img, pre {{
                    page-break-inside: avoid;
                }}
                
                /* Принудительная печать фонов и цветов */
                body {{
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
                
                /* Убираем все лишнее */
                body {{
                    margin: 0;
                    padding: 0;
                }}
            }}
        </style>
        """


        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Preview — {theme_name}</title>
    <link rel="stylesheet" href="file://{katex_css}">
    {print_styles}
</head>
<body>
{html_content}

<script src="file://{katex_js}"></script>
<script src="file://{auto_render_js}"></script>
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        if (typeof renderMathInElement !== 'undefined') {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: "$$", right: "$$", display: true}},
                    {{left: "$", right: "$", display: false}}
                ]
            }});
        }}
    }});
</script>
</body>
</html>"""
        return full_html


    def render_markdown(self, text, theme_name="light"):
        """Рендеринг Markdown в HTML с поддержкой LaTeX (включая блоки кода)"""
        # Сброс кэша формул
        self.display_math_cache = []
        self.inline_math_cache = []

        # Обработка LaTeX-формул до конвертации Markdown
        processed_text = self.process_latex_before_markdown(text)

        # Конвертация Markdown в HTML
        import markdown

        md = markdown.Markdown(
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.codehilite",
                "markdown.extensions.tables",
                "markdown.extensions.toc",
            ]
        )

        html_content = md.convert(processed_text)

        # Функция восстановления для обычных случаев
        def restore_normal(match):
            index = int(match.group(1))
            if index < len(self.display_math_cache):
                return f"$${self.display_math_cache[index]}$$"
            return match.group(0)

        def restore_inline_normal(match):
            index = int(match.group(1))
            if index < len(self.inline_math_cache):
                return f"${self.inline_math_cache[index]}$"
            return match.group(0)

        # Функция восстановления для экранированных случаев (внутри codehilite)
        def restore_escaped(match):
            index = int(match.group(1))
            if index < len(self.display_math_cache):
                return f"$${self.display_math_cache[index]}$$"
            return match.group(0)

        def restore_inline_escaped(match):
            index = int(match.group(1))
            if index < len(self.inline_math_cache):
                return f"${self.inline_math_cache[index]}$"
            return match.group(0)

        # 1. Сначала восстанавливаем обычные комментарии (если они не внутри codehilite или если кодихайт не экранировал)
        html_content = re.sub(
            r"<!--\s*display-math-(\d+)\s*-->", restore_normal, html_content
        )
        html_content = re.sub(
            r"<!--\s*inline-math-(\d+)\s*-->", restore_inline_normal, html_content
        )

        # 2. Затем восстанавливаем экранированные комментарии (которые остались внутри <code>)
        html_content = re.sub(
            r"&lt;!--\s*display-math-(\d+)\s*--&gt;", restore_escaped, html_content
        )
        html_content = re.sub(
            r"&lt;!--\s*inline-math-(\d+)\s*--&gt;",
            restore_inline_escaped,
            html_content,
        )

        # Локальные пути к файлам KaTeX
        base_dir = os.path.dirname(__file__)
        katex_css = os.path.join(base_dir, "katex", "katex.min.css")
        katex_js = os.path.join(base_dir, "katex", "katex.min.js")
        auto_render_js = os.path.join(base_dir, "katex", "auto-render.min.js")

        # Получаем CSS-стили (теперь они без тегов <style>)
        theme_css = self.themes.get(theme_name, self.themes["light"])

        # Стили для печати и колонтитулов
        # Теперь весь CSS будет обернут в ОДИН тег <style> в конце
        print_styles = f"""
<style>
            {theme_css}
            @media print {{
                @page {{
                    size: A4 portrait;
                    margin: 2cm 2cm 2cm 2cm;
                    @top-center {{
                        content: "Markdown Editor";
                        font-size: 8pt;
                        color: #999;
                    }}
                    @bottom-center {{
                        content: counter(page) " / " counter(pages);
                        font-size: 8pt;
                        color: #999;
                    }}
                }}
                h1, h2, h3, h4, h5, h6 {{
                    page-break-after: avoid;
                }}
                h1 {{
                    page-break-before: always;
                }}
                body > h1:first-child {{
                    page-break-before: auto;
                }}
                table, img, pre {{
                    page-break-inside: avoid;
                }}
                body {{
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
            }}
        </style>
        """
        
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Preview — {theme_name}</title>
    <link rel="stylesheet" href="file://{katex_css}">
    {print_styles}
</head>
<body>
{html_content}

<script src="file://{katex_js}"></script>
<script src="file://{auto_render_js}"></script>
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        if (typeof renderMathInElement !== 'undefined') {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: "$$", right: "$$", display: true}},
                    {{left: "$", right: "$", display: false}}
                ]
            }});
        }}
    }});
</script>
</body>
</html>"""
        return full_html
# ... existing code ...



    def process_latex_before_markdown(self, text):
        """Обработка LaTeX-формул в Markdown-тексте (до конвертации в HTML)"""

        # Store display math formulas $$...$$
        def store_display(match):
            formula = match.group(1)
            placeholder = f"<!-- display-math-{len(self.display_math_cache)} -->"
            self.display_math_cache.append(formula)
            return placeholder

        # Store inline math formulas $...$
        def store_inline(match):
            formula = match.group(1)
            placeholder = f"<!-- inline-math-{len(self.inline_math_cache)} -->"
            self.inline_math_cache.append(formula)
            return placeholder

        # First, protect display math $$...$$ (multiline)
        markdown_text = re.sub(r"\$\$(.+?)\$\$", store_display, text, flags=re.DOTALL)

        # Then protect inline math $...$
        markdown_text = re.sub(r"(?<!\$)\$(.+?)\$(?!\$)", store_inline, markdown_text)

        return markdown_text

    def insert_text(self, text):
        """Вставка текста в текущую позицию"""
        cursor = self.editor.textCursor()
        selection = cursor.selectedText()
        if (
            "$" in text and text.count("$") == 1
        ):  # For single $ insertion (LaTeX inline)
            cursor.insertText(text)
        else:
            cursor.insertText(text + selection)
        self.editor.setTextCursor(cursor)
        self.update_preview()

    def insert_bold(self):
        """Вставка жирного текста"""
        cursor = self.editor.textCursor()
        selection = cursor.selectedText()
        if not selection:
            selection = "текст"
        cursor.insertText(f"**{selection}**")
        self.editor.setTextCursor(cursor)
        self.update_preview()

    def insert_italic(self):
        """Вставка курсива"""
        cursor = self.editor.textCursor()
        selection = cursor.selectedText()
        if not selection:
            selection = "текст"
        cursor.insertText(f"*{selection}*")
        self.editor.setTextCursor(cursor)
        self.update_preview()

    def insert_unordered_list(self):
        """Вставка ненумерованного списка"""
        cursor = self.editor.textCursor()
        selection = cursor.selectedText()
        if not selection:
            cursor.insertText("- элемент списка")
        else:
            lines = selection.split("\n")
            list_items = "\n".join(f"- {line}" for line in lines if line.strip())
            cursor.insertText(list_items)
        self.editor.setTextCursor(cursor)
        self.update_preview()

    def insert_link(self):
        """Вставка ссылки"""
        from PyQt6.QtWidgets import QInputDialog

        url, ok1 = QInputDialog.getText(self, "Вставить ссылку", "URL:")
        if ok1 and url:
            text, ok2 = QInputDialog.getText(self, "Вставить ссылку", "Текст ссылки:")
            if ok2:
                cursor = self.editor.textCursor()
                cursor.insertText(f"[{text or url}]({url})")
                self.editor.setTextCursor(cursor)
                self.update_preview()

    def insert_image(self):
        """Вставка изображения"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Вставить изображение",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All files (*)",
        )
        if filepath:
            # Формируем относительный путь к изображению, если файл рядом с документом
            # Или используем абсолютный путь, если файл где-то еще.
            # Для надежности в Markdown лучше использовать относительный путь или url-encoded путь.
            # Здесь используем абсолютный путь, но экранируем пробелы для совместимости.

            # Простой вариант: вставляем абсолютный путь в скобках
            # Вариант 2: вставляем относительный путь, если файл лежит в той же папке что и .md
            # (Требует логики определения текущей директории документа, что сложнее)

            # Пока используем абсолютный путь, но заменяем обратные слеши на прямые (для Windows)
            display_path = filepath.replace("\\", "/")

            cursor = self.editor.textCursor()
            # Markdown синтаксис: ![Описание](путь)
            image_markdown = f"![изображение]({display_path})"
            cursor.insertText(image_markdown)
            self.editor.setTextCursor(cursor)
            self.update_preview()

    def toggle_theme(self):
        """Переключение темы предпросмотра"""
        theme_order = ["light", "dark", "contrast"]
        current_idx = theme_order.index(self.theme_name)
        self.theme_name = theme_order[(current_idx + 1) % len(theme_order)]

        # Обновляем превью с новой темой
        self.update_preview()
        self.statusbar.showMessage(f"Тема: {self.theme_name.capitalize()}")

    def set_theme(self, theme_name):
        self.theme_name = theme_name
        self.update_preview()
        self.statusbar.showMessage(f"Тема: {theme_name.capitalize()}")

    def set_editor_theme(self, theme_name):
        """Установка темы редактора"""
        if theme_name == "dark":
            self.editor.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    selection-background-color: #404040;
                    selection-color: #ffffff;
                }
            """)
        elif theme_name == "contrast":
            self.editor.setStyleSheet("""
                QTextEdit {
                    background-color: #000000;
                    color: #ffffff;
                    selection-background-color: #666666;
                    selection-color: #ffffff;
                }
            """)
        else:  # light
            self.editor.setStyleSheet("""
                            QTextEdit {
                                font-family: Arial, sans-serif;
                                background-color: #ffffff;
                                color: #000000;
                                selection-background-color: #666666;
                                selection-color: #ffffff;
                            }
                        """)
        self.editor_theme = theme_name

    def toggle_editor_theme(self):
        """Переключение темы редактора"""
        theme_order = ["light", "dark", "contrast"]
        current_idx = theme_order.index(self.editor_theme)
        new_theme = theme_order[(current_idx + 1) % len(theme_order)]
        self.set_editor_theme(new_theme)
        self.statusbar.showMessage(f"Тема редактора: {new_theme.capitalize()}")

    def update_char_count(self):
        """Обновление счётчика символов и слов"""
        text = self.editor.toPlainText()
        char_count = len(text)
        word_count = len(text.split())

        self.char_count_label.setText(f"Символов: {char_count}")
        self.word_count_label.setText(f"Слов: {word_count}")

    def _set_editor_text_without_dirty(self, text):
        """Установка текста без изменения is_dirty"""
        self.editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.editor.blockSignals(False)

    def new_file(self):
        """Создание нового файла"""
        if self.is_dirty:
            result = QMessageBox.question(self, "Сохранить?", "Сохранить текущий файл?")
            if result == QMessageBox.StandardButton.Yes:
                self.save_file()
                if self.current_file is None:  # если отменили сохранение
                    return
            elif result == QMessageBox.StandardButton.Cancel:
                return

        # 🟢 Очищаем без срабатывания textChanged
        self._set_editor_text_without_dirty("")
        self.current_file = None
        self.is_dirty = False
        self.update_preview()
        self.statusbar.showMessage("Новый файл создан")

    def open_file(self):
        """Открытие файла"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл",
            "",
            "Markdown files (*.md);;Text files (*.txt);;All files (*)",
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor.setPlainText(content)
                self.current_file = filepath
                self.is_dirty = False
                self.update_preview()
                self.statusbar.showMessage(f"Файл открыт: {filepath}")
                self.save_last_session(filepath)
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось открыть файл:\n{str(e)}"
                )

    def save_file(self):
        """Сохранение файла"""
        if not self.current_file:
            self.save_file_as()
            return

        try:
            content = self.editor.toPlainText()
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.is_dirty = False
            self.statusbar.showMessage(f"Файл сохранен: {self.current_file}")
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}"
            )

    def save_file_as(self):
        """Сохранение файла как..."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить как...",
            "",
            "Markdown files (*.md);;Text files (*.txt);;All files (*)",
        )
        if filepath:
            self.current_file = filepath
            self.save_file()

    def export_to_html(self):
        """Экспорт в HTML"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в HTML", "", "HTML files (*.html);;All files (*)"
        )
        if filepath:
            try:
                html = self.render_markdown(self.editor.toPlainText())
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html)
                self.statusbar.showMessage(f"Экспорт в HTML завершен: {filepath}")
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось экспортировать в HTML:\n{str(e)}"
                )

    
    # Исправленная версия export_to_pdf с замыканием:
    def export_to_pdf(self):
        """Экспорт в PDF (с использованием отрендеренного HTML)"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в PDF", "", "PDF files (*.pdf);;All files (*)"
        )
        if not filepath:
            return

        if not filepath.lower().endswith(".pdf"):
            filepath += ".pdf"

        # Показываем сообщение о начале экспорта
        self.statusbar.showMessage("Экспорт в PDF... Генерация PDF")

        try:
            # Создаём временный HTML-файл
            tmp_path = None
            with tempfile.NamedTemporaryFile(
                suffix=".html", delete=False, mode="w", encoding="utf-8"
            ) as tmp:
                html_content = self.render_markdown(self.editor.toPlainText(), theme_name=self.theme_name)
                tmp.write(html_content)
                tmp_path = tmp.name

            # Загружаем временный HTML-файл в предпросмотр
            self.preview.setUrl(QUrl.fromLocalFile(tmp_path))

            # Обработчик завершения загрузки страницы
            def on_load_finished(ok):
                if not ok:
                    QMessageBox.critical(self, "Ошибка", "Не удалось загрузить HTML для экспорта.")
                    self.statusbar.showMessage("")
                    self._cleanup_temp_file(tmp_path)
                    return

                # Отключаем обработчик загрузки, чтобы не вызывать его повторно
                try:
                    self.preview.page().loadFinished.disconnect(on_load_finished)
                except TypeError:
                    pass

                page = self.preview.page()
                if page is None:
                    QMessageBox.critical(self, "Ошибка", "Страница предпросмотра не инициализирована.")
                    self.statusbar.showMessage("")
                    self._cleanup_temp_file(tmp_path)
                    return

                # Функция попытки записи PDF
                def attempt_pdf_write():
                    try:
                        # Используем колбэк. Мы не можем передать аргументы напрямую,
                        # поэтому используем замыкание внутри attempt_pdf_write
                        def callback(pdf_data):
                            try:
                                # pdf_data - это QByteArray
                                with open(filepath, 'wb') as f:
                                    f.write(bytes(pdf_data))
                                
                                self.statusbar.showMessage(f"Экспорт в PDF завершен: {filepath}")
                            except Exception as e:
                                QMessageBox.critical(self, "Ошибка", f"Не удалось записать PDF файл: {str(e)}")
                                self.statusbar.showMessage("")
                            finally:
                                self._cleanup_temp_file(tmp_path)

                        page.printToPdf(callback)

                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", f"Ошибка печати: {str(e)}")
                        self.statusbar.showMessage("")
                        self._cleanup_temp_file(tmp_path)

                # Даем браузеру время обработать загруженный HTML и отрендерить KaTeX
                QTimer.singleShot(500, attempt_pdf_write)

            # Подключаем обработчик загрузки
            self.preview.page().loadFinished.connect(on_load_finished)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать экспорт в PDF:\n{str(e)}")
            self.statusbar.showMessage("")
            if tmp_path and os.path.exists(tmp_path):
                self._cleanup_temp_file(tmp_path)

    def _cleanup_temp_file(self, path):
        try:
            if path and os.path.exists(path):
                os.unlink(path)
        except Exception:
            pass

    def _on_pdf_ready(self, pdf_bytes, filepath, tmp_path):
        """
        Этот метод больше не используется напрямую printToPdf,
        но может быть полезен, если вы решите использовать Future API иначе.
        """
        pass


    def save_last_session(self, filepath):
        """Сохранение последней сессии"""
        try:
            config_path = Path.home() / ".markdown_editor_config.json"
            config = {"last_file": filepath}
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f)
        except Exception as e:
            pass  # Игнорируем ошибки сохранения сессии

    def load_last_session(self):
        """Загрузка последней сессии"""
        config_path = Path.home() / ".markdown_editor_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                last_file = config.get("last_file")
                if last_file and os.path.exists(last_file):
                    # Отключаем таймеры во время загрузки
                    self.preview_timer.stop()

                    with open(last_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.editor.setPlainText(content)
                    self.current_file = last_file
                    self.is_dirty = False

                    # Обновляем предпросмотр вручную после загрузки
                    self.update_preview()
            except Exception as e:
                pass  # Игнорируем ошибки загрузки сессии

    def find_replace(self):
        """Найти и заменить"""
        from PyQt6.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QLineEdit,
            QPushButton,
            QLabel,
            QHBoxLayout,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Найти и заменить")
        layout = QVBoxLayout()

        find_label = QLabel("Найти:")
        find_input = QLineEdit()
        replace_label = QLabel("Заменить на:")
        replace_input = QLineEdit()

        layout.addWidget(find_label)
        layout.addWidget(find_input)
        layout.addWidget(replace_label)
        layout.addWidget(replace_input)

        button_layout = QHBoxLayout()
        find_button = QPushButton("Найти следующее")
        replace_button = QPushButton("Заменить")
        cancel_button = QPushButton("Отмена")

        def find_next():
            text = find_input.text()
            if not text:
                return
            cursor = self.editor.textCursor()
            found = self.editor.find(text)
            if not found:
                cursor.setPosition(0)
                self.editor.setTextCursor(cursor)
                self.editor.find(text)

        def replace():
            text = find_input.text()
            replacement = replace_input.text()
            if not text:
                return
            cursor = self.editor.textCursor()
            if cursor.selectedText() == text:
                cursor.insertText(replacement)
            self.editor.find(text)

        find_button.clicked.connect(find_next)
        replace_button.clicked.connect(replace)
        cancel_button.clicked.connect(dialog.close)

        button_layout.addWidget(find_button)
        button_layout.addWidget(replace_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(
            self,
            "О программе",
            "Markdown Editor (PyQt6)\n\n"
            "Версия: 1.0\n"
            "Разработано с использованием Python 3.8+, PyQt6, QtWebEngine\n"
            "Поддержка LaTeX и Markdown.",
        )

    def closeEvent(self, event):
        """Обработка события закрытия окна"""
        if self.is_dirty:
            # Создаем диалог с вопросом о сохранении
            msg = QMessageBox(self)
            msg.setWindowTitle("Подтверждение выхода")
            msg.setText("Вы собираетесь выйти. Сохранить текущий файл?")
            msg.setStandardButtons(
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel
            )
            
            # Устанавливаем текст для кнопок (опционально, стандартные слова "Сохранить", "Отказаться", "Отмена")
            save_btn = msg.button(QMessageBox.StandardButton.Save)
            save_btn.setText("Сохранить")
            discard_btn = msg.button(QMessageBox.StandardButton.Discard)
            discard_btn.setText("Без сохранения")
            cancel_btn = msg.button(QMessageBox.StandardButton.Cancel)
            cancel_btn.setText("Отмена")

            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
                if self.is_dirty:
                    # Если сохранение не удалось (например, пользователь отменил "Сохранить как")
                    event.ignore()
                    return
            
            elif reply == QMessageBox.StandardButton.Cancel:
                # Отменяем закрытие
                event.ignore()
                return
            
            else:
                # Discard changes - продолжаем закрытие
                event.accept()
        else:
            # Если изменений нет, закрываем сразу
            event.accept()