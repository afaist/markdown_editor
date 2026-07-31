"""Главный класс MarkdownEditorPyQt — собирает все подмодули в одно целое."""

import os
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QFont, QAction, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QSplitter,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QToolBar,
    QMessageBox,
    QStatusBar,
    QLabel,
    QComboBox,
    QPushButton,
)

from markdown_editor_pkg.themes import ThemesManager
from markdown_editor_pkg.markdown_renderer import MarkdownRenderer
from markdown_editor_pkg.file_operations import FileOperations
from markdown_editor_pkg.text_insertions import TextInsertions
from markdown_editor_pkg.find_replace import FindReplaceDialog
from markdown_editor_pkg.session_manager import SessionManager

from markdown_editor_pkg.latex_processor import LaTeXProcessor
from PyQt6.QtWebEngineWidgets import QWebEngineView


class MarkdownEditorPyQt(QMainWindow):
    """Основной класс редактора Markdown с предпросмотром на PyQt6."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Editor (PyQt6)")
        self.resize(1200, 800)

        # Переменные состояния
        self.current_file = None
        self.is_dirty = False

        # Подмодули
        self.theme_manager = ThemesManager()
        self.renderer = MarkdownRenderer(themes=self.theme_manager)
        self.latex_processor = LaTeXProcessor()
        self.file_ops = FileOperations(editor=self, statusbar=None, renderer=self.renderer)
        self.text_insertions = TextInsertions(editor=self)

        # Настройка строки состояния (нужна для FileOperations до init_ui)
        self._statusbar_ref: QStatusBar | None = None

        # Таймеры
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.file_ops.save_file)
        self.auto_save_timer.setSingleShot(True)

        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)

        # Ссылки на виджеты шрифта
        self.font_combo: QComboBox | None = None
        self.font_size_label: QLabel | None = None
        self.font_increase_btn: QPushButton | None = None
        self.font_decrease_btn: QPushButton | None = None

        # Инициализация
        self.init_ui()

        # Подменяю ссылку на statusbar в file_ops
        self.file_ops.statusbar = self._statusbar_ref

        # Загрузка последней сессии
        self.load_last_session()

    # ─── UI ──────────────────────────────────────────────────────────────

    def init_ui(self) -> None:
        """Инициализация интерфейса."""
        # Разделитель
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        # — Редактор —
        self.editor_frame = QFrame()
        editor_layout = QVBoxLayout()
        editor_layout.setSpacing(0)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_frame.setLayout(editor_layout)

        editor_label = QLabel("Редактор Markdown")
        editor_label.setStyleSheet("background-color: #f0f0f0; color: #333333;")
        editor_label.setMinimumHeight(25)
        editor_label.setMaximumHeight(25)
        editor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor_layout.addWidget(editor_label)

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 11))
        self.theme_manager.set_editor_theme("light", self.editor)
        editor_layout.addWidget(self.editor)

        self.splitter.addWidget(self.editor_frame)

        # — Предпросмотр —
        self.preview_frame = QFrame()
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(0)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_frame.setLayout(preview_layout)

        preview_label = QLabel("Предпросмотр")
        preview_label.setStyleSheet("background-color: #f0f0f0; color: #333333;")
        preview_label.setMinimumHeight(25)
        preview_label.setMaximumHeight(25)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_label)

        self.preview = QWebEngineView()
        preview_layout.addWidget(self.preview)

        self.splitter.addWidget(self.preview_frame)
        self.splitter.setSizes([600, 600])

        # — Строка состояния —
        self._statusbar_ref = QStatusBar()
        self.setStatusBar(self._statusbar_ref)

        self.char_count_label = QLabel("Символов: 0")
        self.word_count_label = QLabel("Слов: 0")
        self._statusbar_ref.addPermanentWidget(self.char_count_label)
        self._statusbar_ref.addPermanentWidget(self.word_count_label)

        # — Связи —
        self.editor.textChanged.connect(self.on_text_change)
        self.editor.textChanged.connect(self.update_char_count)

        # — Панели —
        self.setup_toolbar()
        self.setup_menu()

    def setup_toolbar(self) -> None:
        """Настройка панели инструментов."""
        toolbar = QToolBar("Форматирование")
        self.addToolBar(toolbar)

        actions = [
            ("Заголовок 1", lambda: self.text_insertions.insert_text("# ")),
            ("Заголовок 2", lambda: self.text_insertions.insert_text("## ")),
            ("Жирный", self.text_insertions.insert_bold),
            ("Курсив", self.text_insertions.insert_italic),
            ("Список", self.text_insertions.insert_unordered_list),
            ("Цитата", lambda: self.text_insertions.insert_text("> ")),
            ("Код", lambda: self.text_insertions.insert_text("```\n```")),
            ("LaTeX inline", lambda: self.text_insertions.insert_text("$")),
            ("LaTeX block", lambda: self.text_insertions.insert_text("$$\n$$")),
            ("Ссылка", self.text_insertions.insert_link),
            ("Изображение", self.text_insertions.insert_image),
            ("Тема", self._toggle_theme),
            ("Тема редактора", self._toggle_editor_theme),
        ]

        for text, callback in actions:
            action = QAction(text, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)

        toolbar.addSeparator()

        file_actions = [
            ("Открыть", self.file_ops.open_file),
            ("Сохранить", self.file_ops.save_file),
            ("Экспорт в PDF", self.file_ops.export_to_pdf),
        ]

        for text, callback in file_actions:
            action = QAction(text, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)

        toolbar.addSeparator()

        # ─── Выбор шрифта ───
        self.font_combo = QComboBox()
        available_fonts = self.theme_manager.get_available_fonts()
        self.font_combo.addItems(available_fonts)
        
        # Гарантируем, что текущий шрифт в ThemesManager выбран
        current_family = self.theme_manager.font_family
        
        # Пробуем найти и установить шрифт
        # Используем findText для проверки наличия, а затем setCurrentIndex для точности
        font_idx = self.font_combo.findText(current_family, Qt.MatchFlag.MatchExactly)
        
        if font_idx >= 0:
            self.font_combo.setCurrentIndex(font_idx)
        elif available_fonts:
            # Если текущего шрифта нет в списке (редкий случай), ищем "Consolas" принудительно
            # если он есть в списке, иначе берем первый доступный
            consolas_idx = self.font_combo.findText("Consolas", Qt.MatchFlag.MatchExactly)
            if consolas_idx >= 0:
                self.font_combo.setCurrentIndex(consolas_idx)
            else:
                self.font_combo.setCurrentIndex(0)
        
        # Связываем изменение шрифта
        self.font_combo.currentTextChanged.connect(self._on_font_changed)

        self.font_combo.setMinimumWidth(160)
        toolbar.addWidget(self.font_combo)
        
        # ─── Размер шрифта: + ───
        self.font_increase_btn = QPushButton("+")
        self.font_increase_btn.setToolTip("Увеличить шрифт")
        self.font_increase_btn.setFixedWidth(32)
        self.font_increase_btn.clicked.connect(self._increase_font)
        toolbar.addWidget(self.font_increase_btn)

        # ─── Отображение размера шрифта ───
        self.font_size_label = QLabel("11")
        self.font_size_label.setToolTip("Размер шрифта")
        self.font_size_label.setFixedWidth(30)
        self.font_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar.addWidget(self.font_size_label)

        # ─── Размер шрифта: − ───
        self.font_decrease_btn = QPushButton("−")
        self.font_decrease_btn.setToolTip("Уменьшить шрифт")
        self.font_decrease_btn.setFixedWidth(32)
        self.font_decrease_btn.clicked.connect(self._decrease_font)
        toolbar.addWidget(self.font_decrease_btn)

        # ─── Сброс шрифта ───
        toolbar.addSeparator()
        reset_action = QAction("Сбросить шрифт", self)
        reset_action.setToolTip("Сбросить шрифт и размер к значениям по умолчанию")
        reset_action.triggered.connect(self._reset_font)
        toolbar.addAction(reset_action)

    def setup_menu(self) -> None:
        """Настройка меню."""
        menubar = self.menuBar()
        if menubar is None:
            return

        # Файл
        file_menu = menubar.addMenu("Файл")
        if file_menu is not None:
            file_menu.addAction(QAction("Новый", self, triggered=self.file_ops.new_file,
                                        shortcut=QKeySequence.StandardKey.New))
            file_menu.addAction(QAction("Открыть", self, triggered=self.file_ops.open_file,
                                        shortcut=QKeySequence.StandardKey.Open))
            file_menu.addAction(QAction("Сохранить", self, triggered=self.file_ops.save_file,
                                        shortcut=QKeySequence.StandardKey.Save))
            file_menu.addAction(QAction("Сохранить как...", self, triggered=self.file_ops.save_file_as))
            file_menu.addSeparator()
            file_menu.addAction(QAction("Закрыть", self, triggered=self.close,
                                        shortcut=QKeySequence.StandardKey.Close))
            file_menu.addSeparator()
            file_menu.addAction(QAction("Экспорт в HTML", self, triggered=self.file_ops.export_to_html))
            file_menu.addAction(QAction("Экспорт в PDF", self, triggered=self.file_ops.export_to_pdf))
            file_menu.addSeparator()
            file_menu.addAction(QAction("Выход", self, triggered=self.close,
                                        shortcut=QKeySequence.StandardKey.Quit))

        # Правка
        edit_menu = menubar.addMenu("Правка")
        if edit_menu is not None:
            edit_menu.addAction(QAction("Отменить", self, triggered=self.editor.undo,
                                        shortcut=QKeySequence.StandardKey.Undo))
            edit_menu.addAction(QAction("Повторить", self, triggered=self.editor.redo,
                                        shortcut=QKeySequence.StandardKey.Redo))
            edit_menu.addSeparator()
            edit_menu.addAction(QAction("Вырезать", self, triggered=self.editor.cut,
                                        shortcut=QKeySequence.StandardKey.Cut))
            edit_menu.addAction(QAction("Копировать", self, triggered=self.editor.copy,
                                        shortcut=QKeySequence.StandardKey.Copy))
            edit_menu.addAction(QAction("Вставить", self, triggered=self.editor.paste,
                                        shortcut=QKeySequence.StandardKey.Paste))
            edit_menu.addSeparator()
            edit_menu.addAction(QAction("Найти и заменить", self, triggered=self._find_replace,
                                        shortcut=QKeySequence.StandardKey.Find))
            edit_menu.addSeparator()
            edit_menu.addAction(QAction("Вставить изображение...", self, triggered=self.text_insertions.insert_image))

        # Вид
        view_menu = menubar.addMenu("Вид")
        if view_menu is not None:
            view_menu.addAction(QAction("Обновить предпросмотр", self, triggered=self.update_preview))
            view_menu.addSeparator()

            # Темы предпросмотра
            view_menu.addAction(QAction("Тема: светлая", self,
                                        triggered=lambda: self.set_theme("light")))
            view_menu.addAction(QAction("Тема: тёмная", self,
                                        triggered=lambda: self.set_theme("dark")))
            view_menu.addAction(QAction("Тема: контрастная", self,
                                        triggered=lambda: self.set_theme("contrast")))
            view_menu.addSeparator()

            # Темы редактора
            view_menu.addAction(QAction("Тема редактора: светлая", self,
                                        triggered=lambda: self.set_editor_theme("light")))
            view_menu.addAction(QAction("Тема редактора: тёмная", self,
                                        triggered=lambda: self.set_editor_theme("dark")))
            view_menu.addAction(QAction("Тема редактора: контрастная", self,
                                        triggered=lambda: self.set_editor_theme("contrast")))
            view_menu.addSeparator()

            # Шрифт
            view_menu.addAction(QAction("Увеличить шрифт", self,
                                        triggered=self._increase_font,
                                        shortcut=QKeySequence.StandardKey.ZoomIn))
            view_menu.addAction(QAction("Уменьшить шрифт", self,
                                        triggered=self._decrease_font,
                                        shortcut=QKeySequence.StandardKey.ZoomOut))
            view_menu.addAction(QAction("Сбросить шрифт", self,
                                        triggered=self._reset_font,
                                        shortcut=QKeySequence("Ctrl+0")))

        # Справка
        help_menu = menubar.addMenu("Справка")
        if help_menu is not None:
            help_menu.addAction(QAction("О программе", self, triggered=self._show_about))

    # ─── Обработчики шрифта ──────────────────────────────────────────────

    def _on_font_changed(self, family: str) -> None:
        """Обработка изменения шрифта из комбобокса."""
        self.theme_manager.set_font(family, self.theme_manager.font_size, self.editor)
        self._update_font_size_label()
        if self._statusbar_ref:
            self._statusbar_ref.showMessage(f"Шрифт: {family}, размер: {self.theme_manager.font_size}")

    def _increase_font(self) -> None:
        """Увеличить размер шрифта."""
        new_size = self.theme_manager.increase_font(self.editor)
        self._update_font_size_label()
        if self._statusbar_ref:
            self._statusbar_ref.showMessage(f"Размер шрифта: {new_size}")

    def _decrease_font(self) -> None:
        """Уменьшить размер шрифта."""
        new_size = self.theme_manager.decrease_font(self.editor)
        self._update_font_size_label()
        if self._statusbar_ref:
            self._statusbar_ref.showMessage(f"Размер шрифта: {new_size}")

    def _reset_font(self) -> None:
        """Сбросить шрифт к значениям по умолчанию."""
        self.theme_manager.reset_font_to_default(self.editor)
        if self.font_combo:
            # Ищем Consolas в комбобоксе
            font_idx = self.font_combo.findText("Consolas", Qt.MatchFlag.MatchExactly)
            if font_idx >= 0:
                self.font_combo.setCurrentIndex(font_idx)
            else:
                # Consolas нет в системе — ищем первый шрифт из DEFAULT_FONTS,
                # который есть в комбобоксе, либо берём первый доступный
                for default_font in self.theme_manager.DEFAULT_FONTS:
                    idx = self.font_combo.findText(default_font, Qt.MatchFlag.MatchExactly)
                    if idx >= 0:
                        self.font_combo.setCurrentIndex(idx)
                        break
                else:
                    # Fallback: первый доступный шрифт
                    if self.font_combo.count() > 0:
                        self.font_combo.setCurrentIndex(0)
                        # Синхронизируем theme_manager с тем, что реально выбрано в комбобоксе
                        self.theme_manager._font_family = self.font_combo.currentText()
                        self._update_font_size_label()
        if self._statusbar_ref:
            self._statusbar_ref.showMessage(
                f"Шрифт сброшен: {self.theme_manager.font_family}, размер: {self.theme_manager.font_size}")
                        
    def _update_font_size_label(self) -> None:
        """Обновить метку с размером шрифта."""
        if self.font_size_label:
            self.font_size_label.setText(str(self.theme_manager.font_size))

    # ─── Обработчики событий ─────────────────────────────────────────────

    def on_text_change(self) -> None:
        """Обработка изменения текста."""
        self.is_dirty = True
        self.update_char_count()

        if self.current_file:
            self.auto_save_timer.start(3000)

        self.preview_timer.stop()
        self.preview_timer.start(300)

    def update_preview(self) -> None:
        """Обновить предпросмотр."""
        markdown_text = self.editor.toPlainText()
        html = self.renderer.render(
            markdown_text,
            theme_name=self.theme_manager.theme_name,
            base_dir=os.path.dirname(os.path.abspath(__file__)),
        )
        base_url = QUrl.fromLocalFile(os.path.dirname(os.path.abspath(__file__)) or ".")
        self.preview.setHtml(html, base_url)
        if self._statusbar_ref:
            self._statusbar_ref.showMessage("Предпросмотр обновлён")

    def update_char_count(self) -> None:
        """Обновить счётчики символов и слов."""
        text = self.editor.toPlainText()
        if self._statusbar_ref:
            self.char_count_label.setText(f"Символов: {len(text)}")
            self.word_count_label.setText(f"Слов: {len(text.split())}")

    def _set_editor_text_without_dirty(self, text: str) -> None:
        """Установка текста без is_dirty."""
        self.editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.editor.blockSignals(False)

    # ─── Обратная совместимость (для старых тестов) ─────────────────────

    @property
    def theme_name(self) -> str:
        """Для совместимости: имя текущей темы предпросмотра."""
        return self.theme_manager.theme_name

    @property
    def editor_theme(self) -> str:
        """Для совместимости: имя текущей темы редактора."""
        return self.theme_manager.editor_theme

    @property
    def themes(self) -> dict:
        """Для совместимости: словарь CSS-тем."""
        return self.theme_manager.THEMES_CSS

    @property
    def display_math_cache(self) -> list:
        """Для совместимости: кэш блочных формул."""
        return self.latex_processor.display_math_cache

    @display_math_cache.setter
    def display_math_cache(self, value: list) -> None:
        self.latex_processor.display_math_cache = value

    @property
    def inline_math_cache(self) -> list:
        """Для совместимости: кэш встроенных формул."""
        return self.latex_processor.inline_math_cache

    @inline_math_cache.setter
    def inline_math_cache(self, value: list) -> None:
        self.latex_processor.inline_math_cache = value

    def process_latex_before_markdown(self, text: str) -> str:
        """Для совместимости: обработка LaTeX перед конвертацией Markdown."""
        return self.latex_processor.process(text)

    def render_markdown(self, text: str, theme_name: str = "light") -> str:
        """Для совместимости: рендеринг Markdown в HTML."""
        return self.renderer.render(text, theme_name=theme_name,
                                     base_dir=os.path.dirname(os.path.abspath(__file__)))

    def toggle_theme(self) -> None:
        """Для совместимости: переключить тему предпросмотра."""
        self._toggle_theme()

    def set_theme(self, theme_name: str) -> None:
        """Для совместимости: установить тему предпросмотра."""
        self._set_theme(theme_name)

    def set_editor_theme(self, theme_name: str) -> None:
        """Для совместимости: установить тему редактора."""
        self._set_editor_theme(theme_name)

    # ─── Темы (внутренние) ───────────────────────────────────────────────

    def _toggle_theme(self) -> None:
        new_theme = self.theme_manager.toggle_preview_theme()
        self.update_preview()
        if self._statusbar_ref:
            self._statusbar_ref.showMessage(f"Тема: {new_theme.capitalize()}")

    def _set_theme(self, theme_name: str) -> None:
        self.theme_manager.set_preview_theme(theme_name)
        self.update_preview()
        if self._statusbar_ref:
            self._statusbar_ref.showMessage(f"Тема: {theme_name.capitalize()}")

    def _toggle_editor_theme(self) -> None:
        new_theme = self.theme_manager.toggle_editor_theme()
        self.theme_manager.set_editor_theme(new_theme, self.editor)
        if self._statusbar_ref:
            self._statusbar_ref.showMessage(f"Тема редактора: {new_theme.capitalize()}")

    def _set_editor_theme(self, theme_name: str) -> None:
        self.theme_manager.set_editor_theme(theme_name, self.editor)
        if self._statusbar_ref:
            self._statusbar_ref.showMessage(f"Тема редактора: {theme_name.capitalize()}")

    # ─── Поиск ───────────────────────────────────────────────────────────

    def _find_replace(self) -> None:
        dialog = FindReplaceDialog(self)
        dialog.exec_dialog()

    # ─── Сессия ──────────────────────────────────────────────────────────

    def save_last_session(self, filepath: str) -> None:
        SessionManager.save(filepath)

    def load_last_session(self) -> None:
        last_file = SessionManager.load()
        if last_file and os.path.exists(last_file):
            self.preview_timer.stop()
            try:
                with open(last_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self._set_editor_text_without_dirty(content)
                self.current_file = last_file
                self.is_dirty = False
                self.update_preview()
                self.update_char_count()
            except Exception:
                pass

    # ─── Справка ─────────────────────────────────────────────────────────

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "О программе",
            "Markdown Editor (PyQt6)\n\n"
            "Версия: 1.0\n"
            "Разработано с использованием Python 3.8+, PyQt6, QtWebEngine\n"
            "Поддержка LaTeX и Markdown.",
        )

    # ─── Закрытие ────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:  # noqa: N802
        """Обработка события закрытия окна."""
        if self.is_dirty:
            msg = QMessageBox(self)
            msg.setWindowTitle("Подтверждение выхода")
            msg.setText("Вы собираетесь выйти. Сохранить текущий файл?")
            msg.setStandardButtons(
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel
            )

            save_btn = msg.button(QMessageBox.StandardButton.Save)
            save_btn.setText("Сохранить")
            discard_btn = msg.button(QMessageBox.StandardButton.Discard)
            discard_btn.setText("Без сохранения")
            cancel_btn = msg.button(QMessageBox.StandardButton.Cancel)
            cancel_btn.setText("Отмена")

            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Save:
                self.file_ops.save_file()
                if self.is_dirty:
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            else:
                event.accept()
        else:
            event.accept()
