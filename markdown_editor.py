# Markdown Editor
# Основной модуль приложения

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import markdown
from bs4 import BeautifulSoup
import re
import os
import json
import tempfile
from datetime import datetime
from threading import Timer

try:
    from tkhtmlview import HTMLLabel
except ImportError:
    HTMLLabel = None

try:
    from weasyprint import HTML as WeasyHTML
except ImportError:
    WeasyHTML = None


class MarkdownEditor:
    """Основной класс редактора Markdown с предпросмотром"""

    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Editor")
        self.root.geometry("1200x800")

        # Переменные состояния
        self.current_file = None
        self.is_dirty = False
        self.auto_save_enabled = True
        self.auto_save_timer = None
        self.preview_html = ""

        # Кэш для LaTeX формул
        self.display_math_cache = []
        self.inline_math_cache = []

        # Настройки темы
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "editor_bg": "#ffffff",
                "editor_fg": "#000000",
                "toolbar_bg": "#f0f0f0",
                "preview_bg": "#ffffff",
                "preview_fg": "#000000",
            },
            "dark": {
                "bg": "#1e1e1e",
                "fg": "#e0e0e0",
                "editor_bg": "#2d2d2d",
                "editor_fg": "#d4d4d4",
                "toolbar_bg": "#333333",
                "preview_bg": "#1e1e1e",
                "preview_fg": "#e0e0e0",
            },
        }
        self.current_theme = "light"

        # Инициализация интерфейса
        self.setup_ui()
        self.setup_menu()
        self.setup_bindings()

        # Загрузка последней сессии
        self.load_last_session()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создание панели инструментов
        self.toolbar = tk.Frame(
            self.root, bg=self.themes[self.current_theme]["toolbar_bg"]
        )
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Кнопки форматирования
        self.create_format_buttons()

        # Создание основной области редактора
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Панель редактора
        self.editor_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SUNKEN)
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Метка редактора
        editor_label = tk.Label(
            self.editor_frame,
            text="Редактор Markdown",
            bg=self.themes[self.current_theme]["toolbar_bg"],
            fg=self.themes[self.current_theme]["fg"],
        )
        editor_label.pack(fill=tk.X)

        # Текстовое поле редактора
        self.editor = tk.Text(
            self.editor_frame,
            wrap=tk.WORD,
            bg=self.themes[self.current_theme]["editor_bg"],
            fg=self.themes[self.current_theme]["editor_fg"],
            font=("Consolas", 11),
            undo=True,
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Полоса прокрутки редактора
        editor_scroll = ttk.Scrollbar(self.editor_frame, command=self.editor.yview)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=editor_scroll.set)

        # Панель предпросмотра
        self.preview_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SUNKEN)
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Метка предпросмотра
        preview_label = tk.Label(
            self.preview_frame,
            text="Предпросмотр",
            bg=self.themes[self.current_theme]["toolbar_bg"],
            fg=self.themes[self.current_theme]["fg"],
        )
        preview_label.pack(fill=tk.X)

        # Виджет предпросмотра
        if HTMLLabel:
            self.preview = HTMLLabel(self.preview_frame)
        else:
            self.preview = tk.Text(self.preview_frame, wrap=tk.WORD, state=tk.DISABLED)

        self.preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Полоса прокрутки предпросмотра
        preview_scroll = ttk.Scrollbar(self.preview_frame, command=self.preview.yview)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Строка состояния
        self.statusbar = tk.Frame(
            self.root, bg=self.themes[self.current_theme]["toolbar_bg"], height=25
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(
            self.statusbar,
            text="Готов",
            anchor=tk.W,
            bg=self.themes[self.current_theme]["toolbar_bg"],
            fg=self.themes[self.current_theme]["fg"],
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Счётчик символов
        self.char_count_label = tk.Label(
            self.statusbar,
            text="Символов: 0",
            anchor=tk.E,
            bg=self.themes[self.current_theme]["toolbar_bg"],
            fg=self.themes[self.current_theme]["fg"],
        )
        self.char_count_label.pack(side=tk.RIGHT, padx=10)

        # Счётчик слов
        self.word_count_label = tk.Label(
            self.statusbar,
            text="Слов: 0",
            anchor=tk.E,
            bg=self.themes[self.current_theme]["toolbar_bg"],
            fg=self.themes[self.current_theme]["fg"],
        )
        self.word_count_label.pack(side=tk.RIGHT, padx=10)

    def create_format_buttons(self):
        """Создание кнопок форматирования"""
        buttons = [
            ("Заголовок 1", lambda: self.insert_text("# ")),
            ("Заголовок 2", lambda: self.insert_text("## ")),
            ("Жирный", self.insert_bold),
            ("Курсив", self.insert_italic),
            ("Подчёркнутый", lambda: self.insert_text("<u></u>")),
            ("Список", self.insert_unordered_list),
            ("Нумерованный список", self.insert_ordered_list),
            ("Цитата", lambda: self.insert_text("> ")),
            ("Код", lambda: self.insert_text("```\n```")),
            ("LaTeX inline", lambda: self.insert_text("$")),
            ("LaTeX block", lambda: self.insert_text("$$\n$$")),
            ("Ссылка", self.insert_link),
            ("Изображение", self.insert_image),
        ]

        for text, command in buttons:
            btn = tk.Button(
                self.toolbar,
                text=text,
                command=command,
                bg=self.themes[self.current_theme]["toolbar_bg"],
                fg=self.themes[self.current_theme]["fg"],
                padx=5,
                pady=3,
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Кнопка переключения темы
        theme_btn = tk.Button(
            self.toolbar,
            text="Тема",
            command=self.toggle_theme,
            bg=self.themes[self.current_theme]["toolbar_bg"],
            fg=self.themes[self.current_theme]["fg"],
            padx=5,
            pady=3,
        )
        theme_btn.pack(side=tk.RIGHT, padx=5)

    def setup_menu(self):
        """Настройка меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(
            label="Новый", command=self.new_file, accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label="Открыть", command=self.open_file, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="Сохранить", command=self.save_file, accelerator="Ctrl+S"
        )
        file_menu.add_command(label="Сохранить как...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт в HTML", command=self.export_to_html)
        file_menu.add_command(label="Экспорт в PDF", command=self.export_to_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)

        # Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Отменить", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(
            label="Повторить", command=self.redo, accelerator="Ctrl+Y"
        )
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(
            label="Копировать", command=self.copy, accelerator="Ctrl+C"
        )
        edit_menu.add_command(
            label="Вставить", command=self.paste, accelerator="Ctrl+V"
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Найти и заменить", command=self.find_replace, accelerator="Ctrl+F"
        )

        # Вид
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(
            label="Обновить предпросмотр", command=self.update_preview
        )

        # Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

    def setup_bindings(self):
        """Настройка горячих клавиш"""
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-f>", lambda e: self.find_replace())

        # Автосохранение при изменении текста
        self.editor.bind("<KeyRelease>", self.on_text_change)
        self.editor.bind("<KeyRelease>", lambda e: self.update_char_count(), add="+")

    def on_text_change(self, event=None):
        """Обработка изменения текста для автосохранения и обновления предпросмотра"""
        self.is_dirty = True

        # Отмена предыдущего таймера автосохранения
        if self.auto_save_timer:
            self.auto_save_timer.cancel()

        # Запуск нового таймера автосохранения
        if self.auto_save_enabled and self.current_file:
            self.auto_save_timer = Timer(3.0, self.save_file)
            self.auto_save_timer.start()

        # Обновление предпросмотра с задержкой
        if hasattr(self, "preview_timer"):
            self.preview_timer.cancel()
        self.preview_timer = Timer(0.3, self.update_preview)
        self.preview_timer.start()

    def update_preview(self):
        """Обновление предпросмотра"""
        markdown_text = self.editor.get("1.0", tk.END)
        html = self.render_markdown(markdown_text)
        self.preview_html = html

        

        if HTMLLabel:
            self.preview.set_html(html)
        else:
            # Fallback to displaying as plain text with a helpful message
            self.preview.config(state=tk.NORMAL)
            self.preview.delete("1.0", tk.END)
            message = f"Для корректного отображения предпросмотра установите библиотеку tkhtmlview:\n\npip install tkhtmlview\n\nПредпросмотр недоступен. HTML-код:\n\n{html[:500]}..."
            self.preview.insert("1.0", message)
            self.preview.config(state=tk.DISABLED)

        self.status_label.config(text="Предпросмотр обновлён")

    def render_markdown(self, text):
        """Рендеринг Markdown в HTML с поддержкой LaTeX"""
        # Сброс кэша формул
        self.display_math_cache = []
        self.inline_math_cache = []
        
        # Обработка LaTeX-формул до конвертации Markdown
        processed_text = self.process_latex_before_markdown(text)
        
        # Конвертация Markdown в HTML
        md = markdown.Markdown(extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.toc'
        ])
        
        html = md.convert(processed_text)
        
        # Восстановление LaTeX-формulas as HTML entities (for tkhtmlview)
        html = self.restore_latex_for_tkhtmlview(html)
        
        # Создание полного HTML-документа
        # Упрощаем CSS и убираем всё лишнее для совместимости с tkhtmlview
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 10px;
            color: #000000;
            background-color: #ffffff;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #333333;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }}
        p {{
            margin: 0.5em 0;
        }}
        code {{
            background-color: #f4f4f4;
            color: #d14;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            color: #d14;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        blockquote {{
            border-left: 4px solid #ccc;
            margin: 0;
            padding-left: 16px;
            color: #666;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .math-block {{
            margin: 1em 0;
            text-align: center;
        }}
        .math-inline {{
            display: inline-block;
            vertical-align: middle;
        }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
        
        return full_html

    def restore_latex_for_tkhtmlview(self, html):
        """Восстановление LaTeX-формulas for tkhtmlview compatibility"""
        # Restore display math with escaped HTML
        for i, formula in enumerate(self.display_math_cache):
            placeholder = f"__DISPLAY_MATH_{i}__"
            # Escape special HTML characters to prevent injection
            escaped_formula = (
                formula.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            # Use display:block for proper centering
            replacement = (
                f'<div class="math-block" style="display:block; margin:1em 0; '
                f'text-align:center; white-space:pre-wrap;">{escaped_formula}</div>'
            )
            html = html.replace(placeholder, replacement)

        # Restore inline math with escaped HTML
        for i, formula in enumerate(self.inline_math_cache):
            placeholder = f"__INLINE_MATH_{i}__"
            # Escape special HTML characters to prevent injection
            escaped_formula = (
                formula.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            # Use display:inline-block with vertical-align for proper alignment
            replacement = (
                f'<span class="math-inline" style="display:inline-block; '
                f'vertical-align:middle; white-space:pre-wrap;">{escaped_formula}</span>'
            )
            html = html.replace(placeholder, replacement)

        return html

    def render_latex_simple(self, text):
        """Простое отображение LaTeX как HTML с sub/sup"""
        text = re.sub(r"\$\$(.+?)\$\$", r'<div style="text-align:center; margin:1em 0;">\1</div>', text, flags=re.DOTALL)
        text = re.sub(r"(?<!\$)\$(.+?)\$(?!\$)", r'<span style="font-family: monospace;">\1</span>', text)
        return text

    def process_latex_before_markdown(self, text):
        """Обработка LaTeX-формул в Markdown-тексте (до конвертации в HTML)"""
        import re

        # Store display math formulas $$...$$
        def store_display(match):
            formula = match.group(1)
            placeholder = f"__DISPLAY_MATH_{len(self.display_math_cache)}__"
            self.display_math_cache.append(formula)
            return placeholder

        # Store inline math formulas $...$
        def store_inline(match):
            formula = match.group(1)
            placeholder = f"__INLINE_MATH_{len(self.inline_math_cache)}__"
            self.inline_math_cache.append(formula)
            return placeholder

        # First, protect display math $$...$$ (multiline)
        markdown_text = re.sub(r"\$\$(.+?)\$\$", store_display, text, flags=re.DOTALL)

        # Then protect inline math $...$
        # Use negative lookbehind/lookahead to avoid $$...$$
        markdown_text = re.sub(r"(?<!\$)\$(.+?)\$(?!\$)", store_inline, markdown_text)

        return markdown_text


    def restore_latex_formulas(self, html):
        """Восстановление LaTeX-формул после конвертации в HTML"""
        # Restore display math with MathJax syntax
        for i, formula in enumerate(self.display_math_cache):
            placeholder = f"__DISPLAY_MATH_{i}__"
            # Escape special HTML characters in the formula
            escaped_formula = (
                formula.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            replacement = f'<div class="math-block">\\[{escaped_formula}\\]</div>'
            html = html.replace(placeholder, replacement)

        # Restore inline math with MathJax syntax
        for i, formula in enumerate(self.inline_math_cache):
            placeholder = f"__INLINE_MATH_{i}__"
            # Escape special HTML characters in the formula
            escaped_formula = (
                formula.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            replacement = f'<span class="math-inline">\\({escaped_formula}\\)</span>'
            html = html.replace(placeholder, replacement)

        return html

    def insert_text(self, text):
        """Вставка текста в текущую позицию"""
        try:
            selection = self.editor.selection_get()
            if (
                "$" in text and text.count("$") == 1
            ):  # For single $ insertion (LaTeX inline)
                self.editor.insert(tk.INSERT, text)
            else:
                self.editor.insert(tk.INSERT, text + selection)
        except tk.TclError:
            self.editor.insert(tk.INSERT, text)

        self.editor.focus()
        self.update_preview()

    def insert_bold(self):
        """Вставка жирного текста"""
        try:
            selection = self.editor.selection_get()
            self.editor.insert(tk.INSERT, f"**{selection}**")
        except tk.TclError:
            self.editor.insert(tk.INSERT, "**текст**")

        self.editor.focus()
        self.update_preview()

    def insert_italic(self):
        """Вставка курсива"""
        try:
            selection = self.editor.selection_get()
            self.editor.insert(tk.INSERT, f"*{selection}*")
        except tk.TclError:
            self.editor.insert(tk.INSERT, "*текст*")

        self.editor.focus()
        self.update_preview()

    def insert_unordered_list(self):
        """Вставка ненумерованного списка"""
        try:
            selection = self.editor.selection_get()
            lines = selection.split("\n")
            list_items = "\n".join(f"- {line}" for line in lines if line.strip())
            self.editor.insert(tk.INSERT, list_items)
        except tk.TclError:
            self.editor.insert(tk.INSERT, "- элемент списка")

        self.editor.focus()
        self.update_preview()

    def insert_ordered_list(self):
        """Вставка нумерованного списка"""
        try:
            selection = self.editor.selection_get()
            lines = selection.split("\n")
            list_items = "\n".join(
                f"{i+1}. {line}" for i, line in enumerate(lines) if line.strip()
            )
            self.editor.insert(tk.INSERT, list_items)
        except tk.TclError:
            self.editor.insert(tk.INSERT, "1. элемент списка")

        self.editor.focus()
        self.update_preview()

    def insert_link(self):
        """Вставка ссылки"""
        url = simpledialog.askstring("Вставить ссылку", "URL:")
        if url:
            text = simpledialog.askstring("Вставить ссылку", "Текст ссылки:")
            if text is None:
                text = url
            self.editor.insert(tk.INSERT, f"[{text}]({url})")
            self.update_preview()

    def insert_image(self):
        """Вставка изображения"""
        filepath = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if filepath:
            alt_text = simpledialog.askstring(
                "Вставить изображение", "Альтернативный текст:"
            )
            if alt_text is None:
                alt_text = "изображение"
            self.editor.insert(tk.INSERT, f"![{alt_text}]({filepath})")
            self.update_preview()

    def toggle_theme(self):
        """Переключение темы"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.update_preview()

    def apply_theme(self):
        """Применение текущей темы"""
        theme = self.themes[self.current_theme]

        self.root.configure(bg=theme["bg"])
        self.toolbar.configure(bg=theme["toolbar_bg"])
        self.editor_frame.configure(bg=theme["bg"])
        self.editor.configure(bg=theme["editor_bg"], fg=theme["editor_fg"])
        self.preview_frame.configure(bg=theme["bg"])

        if HTMLLabel:
            self.preview.configure(bg=theme["preview_bg"], fg=theme["preview_fg"])
        else:
            self.preview.configure(bg=theme["preview_bg"], fg=theme["preview_fg"])

        self.statusbar.configure(bg=theme["toolbar_bg"])
        self.status_label.configure(bg=theme["toolbar_bg"], fg=theme["fg"])
        self.char_count_label.configure(bg=theme["toolbar_bg"], fg=theme["fg"])
        self.word_count_label.configure(bg=theme["toolbar_bg"], fg=theme["fg"])

        # Обновление кнопок темы
        for widget in self.toolbar.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg=theme["toolbar_bg"], fg=theme["fg"])

    def update_char_count(self):
        """Обновление счётчика символов и слов"""
        text = self.editor.get("1.0", tk.END)
        char_count = len(text) - 1  # -1 для удаления последнего символа новой строки
        word_count = len(text.split())

        self.char_count_label.config(text=f"Символов: {char_count}")
        self.word_count_label.config(text=f"Слов: {word_count}")

    def new_file(self):
        """Создание нового файла"""
        if self.is_dirty:
            result = messagebox.askyesnocancel("Сохранить?", "Сохранить текущий файл?")
            if result:  # Да
                self.save_file()
            elif result is None:  # Отмена
                return

        self.editor.delete("1.0", tk.END)
        self.current_file = None
        self.is_dirty = False
        self.update_preview()
        self.status_label.config(text="Новый файл создан")

    def open_file(self):
        """Открытие файла"""
        filepath = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", content)
                self.current_file = filepath
                self.is_dirty = False
                self.update_preview()
                self.status_label.config(text=f"Файл открыт: {filepath}")
                self.save_last_session(filepath)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")

    def save_file(self):
        """Сохранение файла"""
        if not self.current_file:
            self.save_file_as()
            return

        try:
            content = self.editor.get("1.0", tk.END)
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.is_dirty = False
            self.status_label.config(text=f"Файл сохранён: {self.current_file}")
            self.save_last_session(self.current_file)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def save_file_as(self):
        """Сохранение файла как"""
        filepath = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".md",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if filepath:
            self.current_file = filepath
            self.save_file()

    def export_to_html(self):
        """Экспорт в HTML"""
        filepath = filedialog.asksaveasfilename(
            title="Экспорт в HTML",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html *.htm"), ("All files", "*.*")],
        )
        if filepath:
            try:
                markdown_text = self.editor.get("1.0", tk.END)
                html = self.render_markdown(markdown_text)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html)

                self.status_label.config(text=f"Экспорт в HTML завершён: {filepath}")
            except Exception as e:
                messagebox.showerror(
                    "Ошибка", f"Не удалось экспортировать в HTML:\n{str(e)}"
                )

    def export_to_pdf(self):
        """Экспорт в PDF"""
        if not WeasyHTML:
            messagebox.showerror(
                "Ошибка",
                "Библиотека weasyprint не установлена.\nУстановите: pip install weasyprint",
            )
            return

        filepath = filedialog.asksaveasfilename(
            title="Экспорт в PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if filepath:
            try:
                markdown_text = self.editor.get("1.0", tk.END)
                html_content = self.render_markdown(markdown_text)

                # Создание PDF
                weasy_html = WeasyHTML(string=html_content, base_url=os.getcwd())
                weasy_html.write_pdf(filepath)

                self.status_label.config(text=f"Экспорт в PDF завершён: {filepath}")
            except Exception as e:
                messagebox.showerror(
                    "Ошибка", f"Не удалось экспортировать в PDF:\n{str(e)}"
                )

    def find_replace(self):
        """Окно поиска и замены"""
        find_window = tk.Toplevel(self.root)
        find_window.title("Найти и заменить")
        find_window.geometry("400x150")
        find_window.transient(self.root)

        # Поле поиска
        tk.Label(find_window, text="Найти:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        find_entry = tk.Entry(find_window, width=30)
        find_entry.grid(row=0, column=1, padx=5, pady=5)

        # Поле замены
        tk.Label(find_window, text="Заменить на:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        replace_entry = tk.Entry(find_window, width=30)
        replace_entry.grid(row=1, column=1, padx=5, pady=5)

        # Кнопки
        def find_next():
            search_text = find_entry.get()
            if search_text:
                start_pos = self.editor.search(search_text, tk.INSERT, tk.END)
                if start_pos:
                    end_pos = f"{start_pos}+{len(search_text)}c"
                    self.editor.tag_remove("search", "1.0", tk.END)
                    self.editor.tag_add("search", start_pos, end_pos)
                    self.editor.tag_config("search", background="yellow")
                    self.editor.mark_set(tk.INSERT, end_pos)
                    self.editor.see(start_pos)
                else:
                    messagebox.showinfo("Поиск", "Текст не найден")

        def replace():
            search_text = find_entry.get()
            replace_text = replace_entry.get()
            if search_text:
                content = self.editor.get("1.0", tk.END)
                new_content = content.replace(search_text, replace_text)
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", new_content)

        def replace_all():
            search_text = find_entry.get()
            replace_text = replace_entry.get()
            if search_text:
                content = self.editor.get("1.0", tk.END)
                new_content = content.replace(search_text, replace_text)
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", new_content)
                messagebox.showinfo(
                    "Замена", f"Заменено {content.count(search_text)} вхождений"
                )

        tk.Button(find_window, text="Найти", command=find_next).grid(
            row=2, column=0, padx=5, pady=5
        )
        tk.Button(find_window, text="Заменить", command=replace).grid(
            row=2, column=1, padx=5, pady=5
        )
        tk.Button(find_window, text="Заменить все", command=replace_all).grid(
            row=2, column=2, padx=5, pady=5
        )

    def undo(self):
        """Отмена последнего действия"""
        try:
            self.editor.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        """Повтор отменённого действия"""
        try:
            self.editor.edit_redo()
        except tk.TclError:
            pass

    def cut(self):
        """Вырезать"""
        try:
            self.editor.event_generate("<<Cut>>")
        except tk.TclError:
            pass

    def copy(self):
        """Копировать"""
        try:
            self.editor.event_generate("<<Copy>>")
        except tk.TclError:
            pass

    def paste(self):
        """Вставить"""
        try:
            self.editor.event_generate("<<Paste>>")
        except tk.TclError:
            pass

    def show_about(self):
        """О программе"""
        about_text = """Markdown Editor v1.0

Редактор Markdown с предпросмотром и поддержкой LaTeX-формул.

Особенности:
- Редактирование Markdown с предпросмотром в реальном времени
- Поддержка встроенных и блочных LaTeX-формул
- Экспорт в HTML и PDF
- Несколько тем оформления
- Автосохранение

Разработано с использованием:
- Python 3.8+
- Tkinter
- Markdown
- BeautifulSoup4
- MathJax
- WeasyPrint"""

        messagebox.showinfo("О программе", about_text)

    def quit(self):
        """Выход из приложения"""
        if self.is_dirty:
            result = messagebox.askyesnocancel(
                "Сохранить?", "Сохранить текущий файл перед выходом?"
            )
            if result:  # Да
                self.save_file()
            elif result is None:  # Отмена
                return

        # Отмена таймеров
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
        if hasattr(self, "preview_timer"):
            self.preview_timer.cancel()

        self.save_last_session()
        self.root.quit()

    def load_last_session(self):
        """Загрузка последней сессии"""
        session_file = os.path.join(
            tempfile.gettempdir(), "markdown_editor_session.json"
        )
        if os.path.exists(session_file):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    session = json.load(f)
                if session.get("last_file") and os.path.exists(session["last_file"]):
                    self.open_file_from_path(session["last_file"])
            except Exception:
                pass

    def open_file_from_path(self, filepath):
        """Открытие файла по пути"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", content)
            self.current_file = filepath
            self.is_dirty = False
            self.update_preview()
            self.status_label.config(text=f"Файл открыт: {filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")

    def save_last_session(self, filepath=None):
        """Сохранение последней сессии"""
        session_file = os.path.join(
            tempfile.gettempdir(), "markdown_editor_session.json"
        )
        session = {
            "last_file": filepath or self.current_file,
            "timestamp": datetime.now().isoformat(),
        }
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session, f)
        except Exception:
            pass


def main():
    """Основная функция"""
    root = tk.Tk()
    app = MarkdownEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
