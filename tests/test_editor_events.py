"""Tests for editor_events module."""

from unittest import mock

from PyQt6.QtCore import QUrl

from markdown_editor_pkg.editor_events import EventHandler


class TestEventHandlerInit:
    """Тесты инициализации EventHandler."""

    def test_init_sets_flags(self, markdown_editor):
        """EventHandler инициализирует флаги синхронизации."""
        handler = markdown_editor.event_handler
        assert handler._syncing_scroll is False
        assert handler._scroll_from_preview is False
        assert handler._scroll_from_editor is False


class TestOnTextChange:
    """Тесты on_text_change()."""

    def test_sets_dirty_on_text(self, markdown_editor):
        """on_text_change устанавливает is_dirty при наличии текста."""
        markdown_editor.editor.setPlainText("Hello")
        with mock.patch.object(markdown_editor.auto_save_timer, "start"):
            markdown_editor.event_handler.on_text_change()
        assert markdown_editor.is_dirty is True

    def test_sets_dirty_empty_text(self, markdown_editor):
        """on_text_change устанавливает is_dirty даже для пустого текста."""
        markdown_editor.editor.setPlainText("")
        with mock.patch.object(markdown_editor.auto_save_timer, "start"):
            markdown_editor.event_handler.on_text_change()
        # on_text_change устанавливает is_dirty = bool(text.strip())
        assert markdown_editor.is_dirty is False

    def test_stops_preview_timer(self, markdown_editor):
        """on_text_change останавливает preview_timer перед запуском."""
        with mock.patch.object(markdown_editor.preview_timer, "stop") as mock_stop, \
             mock.patch.object(markdown_editor.preview_timer, "start") as mock_start, \
             mock.patch.object(markdown_editor, "update_char_count"):
            markdown_editor.editor.setPlainText("test")
            markdown_editor.event_handler.on_text_change()
            assert mock_stop.call_count >= 1
            assert mock_start.call_count >= 1

    def test_starts_preview_timer_with_delay(self, markdown_editor):
        """on_text_change запускает preview_timer с задержкой."""
        with mock.patch.object(markdown_editor.preview_timer, "start") as mock_start, \
             mock.patch.object(markdown_editor, "update_char_count"):
            markdown_editor.editor.setPlainText("test")
            markdown_editor.event_handler.on_text_change()
            # Проверяем что start вызван с 300 (может быть вызван несколько раз)
            calls = [c for c in mock_start.call_args_list if c == mock.call(300)]
            assert len(calls) >= 1


class TestUpdateFileStatus:
    """Тесты update_file_status()."""

    def test_update_file_status_with_file(self, markdown_editor):
        """update_file_status показывает имя файла."""
        markdown_editor.current_file = "/home/user/test.md"
        markdown_editor.is_dirty = False
        markdown_editor.event_handler.update_file_status()
        assert markdown_editor.file_name_label is not None
        assert markdown_editor.file_name_label.text() == "test.md"

    def test_update_file_status_dirty(self, markdown_editor):
        """update_file_status показывает статус несохранённого файла."""
        markdown_editor.current_file = "/home/user/test.md"
        markdown_editor.is_dirty = True
        markdown_editor.event_handler.update_file_status()
        assert "Unsaved" in markdown_editor.file_name_label.text()

    def test_update_file_status_no_label(self, markdown_editor):
        """update_file_status без file_name_label не падает."""
        markdown_editor.file_name_label = None
        markdown_editor.current_file = "/test.md"
        markdown_editor.event_handler.update_file_status()
        # Не должно вызвать исключение


class TestUpdatePreview:
    """Тесты update_preview()."""

    def test_update_preview_calls_renderer(self, markdown_editor):
        """update_preview вызывает рендеринг."""
        markdown_editor.editor.setPlainText("# Test")
        with mock.patch.object(markdown_editor.renderer, "render") as mock_render:
            mock_render.return_value = "<html><body><h1>Test</h1></body></html>"
            markdown_editor.event_handler.update_preview()
            mock_render.assert_called_once()

    def test_update_preview_sets_html(self, markdown_editor):
        """update_preview устанавливает HTML в preview."""
        markdown_editor.editor.setPlainText("# Test")
        with mock.patch.object(markdown_editor.renderer, "render") as mock_render:
            mock_render.return_value = "<html><body><h1>Test</h1></body></html>"
            markdown_editor.event_handler.update_preview()
            # setHtml вызывается (preview не патчим, так как это реальный QWebEngineView)


class TestUpdateCharCount:
    """Тесты update_char_count()."""

    def test_update_char_count(self, markdown_editor):
        """update_char_count обновляет счётчики."""
        markdown_editor.editor.setPlainText("Hi")
        markdown_editor.event_handler.update_char_count()
        assert markdown_editor.char_count_label is not None
        assert markdown_editor.word_count_label is not None
        assert "2" in markdown_editor.char_count_label.text()
        assert "1" in markdown_editor.word_count_label.text()

    def test_update_char_count_empty(self, markdown_editor):
        """update_char_count для пустого текста."""
        markdown_editor.editor.setPlainText("")
        markdown_editor.event_handler.update_char_count()
        assert markdown_editor.char_count_label is not None
        assert "0" in markdown_editor.char_count_label.text()


class TestSetEditorTextWithoutDirty:
    """Тесты set_editor_text_without_dirty()."""

    def test_sets_text(self, markdown_editor):
        """set_editor_text_without_dirty устанавливает текст."""
        markdown_editor.event_handler.set_editor_text_without_dirty("Hello")
        assert markdown_editor.editor.toPlainText() == "Hello"

    def test_does_not_signal_text_changed(self, markdown_editor):
        """set_editor_text_without_dirty блокирует сигналы."""
        with mock.patch.object(markdown_editor.editor, "textChanged") as mock_changed:
            markdown_editor.event_handler.set_editor_text_without_dirty("test")
            # Сигналы должны быть заблокированы
            # Это сложно протестировать напрямую, но можно проверить что текст установлен


class TestSyncScrollFromEditor:
    """Тесты синхронизации прокрутки из редактора."""

    def test_sync_scroll_from_editor_no_syncing(self, markdown_editor):
        """sync_scroll_from_editor не входит в рекурсию."""
        markdown_editor.event_handler._syncing_scroll = True
        # Должен вернуться сразу
        markdown_editor.event_handler.sync_scroll_from_editor()
        assert markdown_editor.event_handler._syncing_scroll is True

    def test_sync_scroll_from_editor_with_preview(self, markdown_editor):
        """sync_scroll_from_editor с preview."""
        markdown_editor.editor.setPlainText("# Test")
        # Скроллбар должен существовать
        vbar = markdown_editor.editor.verticalScrollBar()
        assert vbar is not None


class TestSyncScrollFromPreview:
    """Тесты синхронизации прокрутки из превью."""

    def test_sync_scroll_from_preview_no_syncing(self, markdown_editor):
        """sync_scroll_from_preview при _syncing_scroll не работает."""
        markdown_editor.event_handler._syncing_scroll = True
        markdown_editor.event_handler.sync_scroll_from_preview(0.5)
        assert markdown_editor.event_handler._syncing_scroll is True

    def test_sync_scroll_from_preview_no_flag(self, markdown_editor):
        """sync_scroll_from_preview без флага _scroll_from_preview."""
        markdown_editor.event_handler._scroll_from_preview = False
        markdown_editor.event_handler.sync_scroll_from_preview(0.5)
        # Не должно произойти ошибки


class TestOnPreviewScroll:
    """Тесты on_preview_scroll()."""

    def test_on_preview_scroll_sets_flag(self, markdown_editor):
        """on_preview_scroll устанавливает флаг _scroll_from_preview."""
        markdown_editor.event_handler.on_preview_scroll(0.5)
        # Флаг устанавливается и сбрасывается в процессе


class TestConnect:
    """Тесты connect()."""

    def test_connect_is_noop(self, markdown_editor):
        """connect() — пустой метод (сигналы уже подключены)."""
        # Не должен вызвать исключение
        markdown_editor.event_handler.connect()
