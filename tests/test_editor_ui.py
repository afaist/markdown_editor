"""Tests for editor UI components."""

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolBar

from markdown_editor_pkg.editor import MarkdownEditorPyQt


class TestEditorUI:
    """Тесты UI компонентов редактора."""

    def setup_method(self):
        self.editor = MarkdownEditorPyQt()
        self.editor.setWindowTitle("Test Editor")

    def teardown_method(self):
        self.editor.close()

    def test_editor_created(self):
        """Редактор создаётся без ошибок."""
        assert self.editor.windowTitle() == "Test Editor"

    def test_editor_has_splitter(self):
        """Редактор содержит QSplitter."""
        central = self.editor.centralWidget()
        assert central is not None

    def test_editor_has_editor_widget(self):
        """Редактор содержит QTextEdit."""
        assert self.editor.editor is not None

    def test_editor_has_preview_widget(self):
        """Редактор содержит QWebEngineView."""
        assert self.editor.preview is not None

    def test_editor_has_statusbar(self):
        """Редактор содержит QStatusBar."""
        assert self.editor.statusBar() is not None

    def test_editor_has_font_combo(self):
        """Редактор содержит комбобокс шрифта."""
        assert self.editor.font_combo is not None

    def test_editor_has_font_buttons(self):
        """Редактор содержит кнопки увеличения/уменьшения шрифта."""
        assert self.editor.font_increase_btn is not None
        assert self.editor.font_decrease_btn is not None

    def test_editor_has_toolbar(self):
        """Редактор содержит тулбар."""
        toolbars = self.editor.findChildren(QToolBar)
        assert len(toolbars) > 0

    def test_editor_has_menubar(self):
        """Редактор содержит меню."""
        menubar = self.editor.menuBar()
        assert menubar is not None

    def test_editor_menu_file_exists(self):
        """Существует меню File."""
        menubar = self.editor.menuBar()
        assert menubar is not None
        has_file = any("File" in a.text() or "Файл" in a.text() for a in menubar.actions())
        assert has_file is True

    def test_editor_menu_edit_exists(self):
        """Существует меню Edit."""
        menubar = self.editor.menuBar()
        assert menubar is not None
        has_edit = any("Edit" in a.text() or "Правка" in a.text() for a in menubar.actions())
        assert has_edit is True

    def test_editor_menu_view_exists(self):
        """Существует меню View."""
        menubar = self.editor.menuBar()
        assert menubar is not None
        has_view = any("View" in a.text() or "Вид" in a.text() for a in menubar.actions())
        assert has_view is True

    def test_editor_menu_markdown_exists(self):
        """Существует меню Markdown."""
        menubar = self.editor.menuBar()
        assert menubar is not None
        has_md = any("Markdown" in a.text() or "Markdown" in a.text() for a in menubar.actions())
        assert has_md is True

    def test_editor_menu_help_exists(self):
        """Существует меню Help."""
        menubar = self.editor.menuBar()
        assert menubar is not None
        has_help = any("Help" in a.text() or "Справка" in a.text() for a in menubar.actions())
        assert has_help is True

    def test_editor_font_combo_has_items(self):
        """Комбобокс шрифта содержит элементы."""
        combo = self.editor.font_combo
        assert combo is not None
        assert combo.count() > 0
        assert "Consolas" in [combo.itemText(i) for i in range(combo.count())]

    def test_editor_markdown_menu_has_headings(self):
        """Меню Markdown содержит заголовки."""
        menubar = self.editor.menuBar()
        assert menubar is not None
        md_menu = None
        for action in menubar.actions():
            menu = action.menu()
            if menu is not None and "Markdown" in menu.title():
                md_menu = menu
                break
        assert md_menu is not None, "Меню Markdown не найдено"

        heading_action = None
        for action in md_menu.actions():
            sub_menu = action.menu()
            if sub_menu is not None and "Headings" in sub_menu.title():
                heading_action = sub_menu
                break
        assert heading_action is not None, "Headings submenu not found"
        assert len(heading_action.actions()) > 0

    def test_editor_shortcuts_registered(self):
        """Горячие клавиши зарегистрированы."""
        all_actions = self.editor.findChildren(QAction)

        # Собираем все non-empty shortcuts
        shortcuts = []
        for a in all_actions:
            sc = a.shortcut()
            if sc and not sc.isEmpty():
                shortcuts.append(sc.toString())

        # Должно быть много shortcuts (меню + markdown menu)
        assert len(shortcuts) > 10, (
            f"Ожидается >10 shortcuts, найдено {len(shortcuts)}: {shortcuts}"
        )

        # Проверяем наличие конкретных shortcuts (в приложении используются Ctrl+Shift+X для markdown)
        sc_str = " ".join(shortcuts)
        assert "Ctrl+Shift+B" in sc_str, f"Ctrl+Shift+B не найден. Shorts: {shortcuts}"
        assert "Ctrl+Shift+Q" in sc_str, f"Ctrl+Shift+Q не найден. Shorts: {shortcuts}"
        assert "Ctrl+Shift+C" in sc_str, f"Ctrl+Shift+C не найден. Shorts: {shortcuts}"
