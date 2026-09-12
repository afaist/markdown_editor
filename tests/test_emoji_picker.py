"""Tests for EmojiPicker and insert_emoji functionality."""


class TestEmojiPicker:
    """Тесты диалога выбора emoji."""

    def _create_mock_editor(self):
        """Создаёт mock-объект editor с QTextEdit."""
        from PyQt6.QtWidgets import QTextEdit

        text_edit = QTextEdit()
        text_edit.setPlainText("Test text")

        class MockEditor:
            def __init__(self, te):
                self.editor = te
                self.current_file = None
                self.is_dirty = False

            def update_preview(self):
                pass

        return MockEditor(text_edit)

    def test_emoji_picker_dialog_creation(self):
        """Тест создания диалога выбора emoji."""
        from markdown_editor_pkg.emoji_picker import EmojiPickerDialog

        dialog = EmojiPickerDialog()

        # Проверяем, что комбобокс категорий заполнен
        assert dialog.category_combo.count() > 0

        # Проверяем, что список emoji не пустой
        assert dialog.list_widget.count() > 0

    def test_emoji_picker_has_categories(self):
        """Тест наличия категорий в диалоге."""
        from markdown_editor_pkg.emoji_picker import EmojiPickerDialog

        dialog = EmojiPickerDialog()

        # Проверяем, что категории существуют
        categories = [
            dialog.category_combo.itemText(i) for i in range(dialog.category_combo.count())
        ]
        assert len(categories) > 0

    def test_emoji_picker_category_switching(self):
        """Тест переключения категорий."""
        from markdown_editor_pkg.emoji_picker import EmojiPickerDialog

        dialog = EmojiPickerDialog()

        # Запоминаем количество emoji в первой категории
        first_count = dialog.list_widget.count()
        assert first_count > 0

        # Переключаем на другую категорию
        if dialog.category_combo.count() > 1:
            dialog.category_combo.setCurrentIndex(1)

            second_count = dialog.list_widget.count()
            # Вторая категория может иметь другое количество emoji
            assert second_count >= 0

    def test_emoji_picker_search(self):
        """Тест поиска по emoji."""
        from markdown_editor_pkg.emoji_picker import EmojiPickerDialog

        dialog = EmojiPickerDialog()

        # Получаем исходное количество emoji
        original_count = dialog.list_widget.count()
        assert original_count > 0

        # Вводим поиск
        dialog.search_input.setText("smile")

        # Фильтрация должна сработать
        filtered_count = dialog.list_widget.count()
        assert filtered_count >= 0
        assert filtered_count <= original_count

        # Очищаем поиск
        dialog.search_input.clear()

        # После очистки должно вернуться исходное количество
        assert dialog.list_widget.count() == original_count

    def test_emoji_picker_search_emoji_char(self):
        """Тест поиска по символу emoji."""
        from markdown_editor_pkg.emoji_picker import EmojiPickerDialog

        dialog = EmojiPickerDialog()

        # Ищем по символу 😀
        dialog.search_input.setText("😀")

        # Должен найтись хотя бы один emoji
        assert dialog.list_widget.count() >= 1

    def test_emoji_picker_insert_emoji(self):
        """Тест вставки emoji через TextInsertions."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        ti.insert_emoji("😀")
        text = mock.editor.toPlainText()
        assert "😀" in text

    def test_emoji_picker_insert_emoji_with_selection(self):
        """Тест вставки emoji — выделение не должно влиять."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        # Выделяем весь текст
        cursor = mock.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        mock.editor.setTextCursor(cursor)

        ti.insert_emoji("❤️")
        text = mock.editor.toPlainText()
        assert "❤️" in text

    def test_emoji_picker_multiple_emojis(self):
        """Тест вставки нескольких emoji."""
        from markdown_editor_pkg.text_insertions import TextInsertions

        mock = self._create_mock_editor()
        ti = TextInsertions(mock)

        ti.insert_emoji("😀")
        ti.insert_emoji("❤️")
        ti.insert_emoji("🎉")

        text = mock.editor.toPlainText()
        assert "😀" in text
        assert "❤️" in text
        assert "🎉" in text

    def test_emoji_picker_data_structure(self):
        """Тест структуры данных emoji."""
        from markdown_editor_pkg.emoji_picker import EMOJI_DATA

        # Проверяем, что данные не пустые
        assert len(EMOJI_DATA) > 0

        # Проверяем, что каждая категория содержит emoji
        for category, emojis in EMOJI_DATA.items():
            assert len(emojis) > 0, f"Category {category} is empty"
            for emoji, name in emojis:
                assert isinstance(emoji, str)
                assert isinstance(name, str)
                assert len(emoji) > 0
                assert len(name) > 0

    def test_emoji_picker_total_count(self):
        """Тест общего количества emoji."""
        from markdown_editor_pkg.emoji_picker import EMOJI_DATA

        total = sum(len(emojis) for emojis in EMOJI_DATA.values())
        assert total > 150  # Должно быть больше 150 emoji
