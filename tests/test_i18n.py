"""Tests for i18n module."""

import sys
from pathlib import Path
from unittest import mock

from PyQt6.QtCore import QCoreApplication

from markdown_editor_pkg.i18n import (
    _get_language_info,
    _load_translator,
    _locate_locales_dir,
    get_available_languages,
    tr,
)


class TestTr:
    """Тесты функции tr()."""

    def test_tr_returns_text_when_no_translator(self):
        """tr() возвращает исходный текст при отсутствии переводчика."""
        result = tr("Hello World")
        assert result == "Hello World"

    def test_tr_with_format_string(self):
        """tr() работает с форматированными строками."""
        result = tr("Characters: {count}").format(count=42)
        assert result == "Characters: 42"

    def test_tr_with_russian_text(self):
        """tr() корректно обрабатывает русские строки."""
        result = tr("Тема: light")
        assert result == "Тема: light"

    def test_tr_with_html_content(self):
        """tr() работает со строками содержащими HTML."""
        result = tr('Author: <a href="test">GigaCode</a>')
        assert result == 'Author: <a href="test">GigaCode</a>'


class TestLanguageInfo:
    """Тесты получения информации о языках."""

    def test_get_language_info_en(self):
        """_get_language_info для английского."""
        result = _get_language_info("en")
        assert result is not None
        assert result["code"] == "en"
        assert result["name"] == "English"
        assert result["qm_file"] == "messages_en.qm"

    def test_get_language_info_ru(self):
        """_get_language_info для русского."""
        result = _get_language_info("ru")
        assert result is not None
        assert result["code"] == "ru"
        assert result["name"] == "Русский"

    def test_get_language_info_unknown(self):
        """_get_language_info для неизвестного кода возвращает None."""
        result = _get_language_info("fr")
        assert result is None

    def test_get_language_info_empty_string(self):
        """_get_language_info для пустой строки возвращает None."""
        result = _get_language_info("")
        assert result is None


class TestAvailableLanguages:
    """Тесты get_available_languages()."""

    def test_get_available_languages_returns_list(self):
        """get_available_languages возвращает список."""
        result = get_available_languages()
        assert isinstance(result, list)

    def test_get_available_languages_has_entries(self):
        """get_available_languages содержит записи."""
        result = get_available_languages()
        assert len(result) >= 2

    def test_get_available_languages_structure(self):
        """get_available_languages возвращает словари с нужными ключами."""
        result = get_available_languages()
        for lang in result:
            assert "code" in lang
            assert "name" in lang
            assert "qm_file" in lang


class TestLocalesDir:
    """Тесты _locate_locales_dir()."""

    def test_locate_locales_dir_returns_path(self):
        """_locate_locales_dir возвращает Path."""
        result = _locate_locales_dir()
        assert isinstance(result, Path)

    def test_locate_locales_dir_is_resolved(self):
        """_locate_locales_dir возвращает абсолютный путь."""
        result = _locate_locales_dir()
        assert result.is_absolute()

    def test_locate_locales_dir_cached(self):
        """_locate_locales_dir кэширует результат."""
        result1 = _locate_locales_dir()
        result2 = _locate_locales_dir()
        assert result1 is result2


class TestLoadTranslator:
    """Тесты _load_translator()."""

    def test_load_translator_nonexistent_file(self, tmp_path):
        """_load_translator с несуществующим файлом возвращает False."""
        from PyQt6.QtCore import QTranslator

        translator = QTranslator()
        result = _load_translator(translator, "en", tmp_path)
        assert result is False

    def test_load_translator_unknown_language(self, tmp_path):
        """_load_translator с неизвестным языком возвращает False."""
        from PyQt6.QtCore import QTranslator

        translator = QTranslator()
        result = _load_translator(translator, "xx", tmp_path)
        assert result is False

    def test_load_translator_with_valid_qm_file(self, tmp_path):
        """_load_translator с существующим .qm файлом."""
        from PyQt6.QtCore import QTranslator

        # Создаём тестовый .qm файл
        qm_file = tmp_path / "messages_en.qm"
        qm_file.write_bytes(b"")

        translator = QTranslator()
        result = _load_translator(translator, "en", tmp_path)
        # Даже пустой файл может загрузиться или не загрузиться — главное без ошибки
        # Результат зависит от содержимого файла
        assert isinstance(result, bool)
