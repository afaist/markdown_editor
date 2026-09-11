"""Tests for resource_path module."""

import sys

from markdown_editor_pkg.resource_path import get_base_dir, get_package_dir, resource_path


class TestResourcePath:
    """Тесты resource_path() в режиме разработки."""

    def test_resource_path_returns_absolute_path(self):
        """resource_path возвращает абсолютный путь в режиме разработки."""
        result = resource_path("katex/katex.min.css")
        assert result.startswith("/")

    def test_resource_path_contains_relative(self):
        """resource_path включает относительный путь."""
        result = resource_path("katex/katex.min.css")
        assert "katex" in result

    def test_resource_path_simple_name(self):
        """resource_path с простым именем файла."""
        result = resource_path("test.txt")
        assert "test.txt" in result


class TestGetPackageDir:
    """Тесты get_package_dir()."""

    def test_get_package_dir_returns_string(self):
        """get_package_dir возвращает строку."""
        result = get_package_dir()
        assert isinstance(result, str)

    def test_get_package_dir_is_absolute(self):
        """get_package_dir возвращает абсолютный путь."""
        result = get_package_dir()
        assert result.startswith("/")

    def test_get_package_dir_contains_package_name(self):
        """get_package_dir содержит имя пакета."""
        result = get_package_dir()
        assert "markdown_editor_pkg" in result

    def test_get_package_dir_frozen_mode(self):
        """get_package_dir в режиме PyInstaller возвращает _MEIPASS."""
        # В режиме разработки _MEIPASS отсутствует, поэтому патчим через setattr
        original_frozen = getattr(sys, "frozen", False)
        original_meipass = getattr(sys, "_MEIPASS", None)

        sys.frozen = True
        sys._MEIPASS = "/tmp/pyinstaller"

        import importlib

        import markdown_editor_pkg.resource_path as rp

        importlib.reload(rp)
        result = rp.get_package_dir()
        assert result == "/tmp/pyinstaller"

        # Восстанавливаем
        sys.frozen = original_frozen
        if original_meipass is None:
            delattr(sys, "_MEIPASS")
        else:
            sys._MEIPASS = original_meipass


class TestGetBaseDir:
    """Тесты get_base_dir()."""

    def test_get_base_dir_returns_string(self):
        """get_base_dir возвращает строку."""
        result = get_base_dir()
        assert isinstance(result, str)

    def test_get_base_dir_same_as_package_dir(self):
        """get_base_dir эквивалентен get_package_dir."""
        assert get_base_dir() == get_package_dir()

    def test_get_base_dir_frozen_mode(self):
        """get_base_dir в режиме PyInstaller."""
        original_frozen = getattr(sys, "frozen", False)
        original_meipass = getattr(sys, "_MEIPASS", None)

        sys.frozen = True
        sys._MEIPASS = "/tmp/pyinstaller"

        import importlib

        import markdown_editor_pkg.resource_path as rp

        importlib.reload(rp)
        result = rp.get_base_dir()
        assert result == "/tmp/pyinstaller"

        sys.frozen = original_frozen
        if original_meipass is None:
            delattr(sys, "_MEIPASS")
        else:
            sys._MEIPASS = original_meipass
