"""
Markdown Editor (PyQt6) — рефакторинг
=====================================

Файл markdown_editor.py теперь является обёрткой, импортирующей
код из пакета markdown_editor_pkg.

Структура пакета:
-----------------
markdown_editor_pkg/
├── __init__.py           # Экспорт MarkdownEditorPyQt
├── editor.py             # Главный класс MarkdownEditorPyQt (собирает всё)
├── themes.py             # CSS-темы предпросмотра и QSS-темы редактора
├── latex_processor.py    # Извлечение LaTeX и обработка зачёркивания
├── callout_processor.py  # GitHub Callouts из blockquote
├── markdown_renderer.py  # Конвертация Markdown → HTML с LaTeX + темами
├── file_operations.py    # Открытие, сохранение, экспорт HTML/PDF
├── text_insertions.py    # Вставка форматированного текста
├── find_replace.py       # Диалог «Найти и заменить»
└── session_manager.py    # Сохранение/загрузка последней сессии

Запуск:
-------
    python main.py

Тесты:
------
    pytest test_markdown_editor.py -v
"""

# Обратная совместимость: импорт из нового пакета
from markdown_editor_pkg.editor import MarkdownEditorPyQt

__all__ = ["MarkdownEditorPyQt"]
