"""Tests for SessionManager."""

import tempfile
from pathlib import Path

from markdown_editor_pkg.session_manager import SessionManager


class TestSessionManager:
    """Тесты SessionManager."""

    def test_save_and_load(self):
        """Сохранение и загрузка сессии."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write("# test")
            test_path = f.name

        try:
            SessionManager.save(test_path)
            loaded = SessionManager.load()
            assert loaded == test_path
        finally:
            # Cleanup
            config = Path.home() / ".markdown_editor_config.json"
            if config.exists():
                config.unlink()

    def test_load_nonexistent_file(self):
        """Загрузка сессии при отсутствии файла конфигурации возвращает None."""
        config = Path.home() / ".markdown_editor_config.json"
        if config.exists():
            config.unlink()
        result = SessionManager.load()
        assert result is None

    def test_load_corrupted_json(self):
        """Загрузка сессии из повреждённого JSON возвращает None."""
        config = Path.home() / ".markdown_editor_config.json"
        try:
            config.write_text("{invalid json", encoding="utf-8")
            result = SessionManager.load()
            assert result is None
        finally:
            if config.exists():
                config.unlink()

    def test_save_overwrites(self):
        """Сохранение перезаписывает предыдущее значение."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write("# test1")
            path1 = f.name
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            f.write("# test2")
            path2 = f.name

        try:
            SessionManager.save(path1)
            assert SessionManager.load() == path1
            SessionManager.save(path2)
            assert SessionManager.load() == path2
        finally:
            config = Path.home() / ".markdown_editor_config.json"
            if config.exists():
                config.unlink()
