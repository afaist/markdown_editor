"""Pytest configuration for markdown_editor tests."""

import os
import sys

# Set environment BEFORE importing anything else
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-gpu --disable-gpu-compositing --disable-software-rasterizer"
    " --disable-gpu-info-update"
)
os.environ["QTWEBENGINE_SETTINGS"] = '{"enable_gpu": "false"}'
os.environ["QT_LOGGING_RULES"] = "qt.webengine.*=false"

# Import QtWebEngineWidgets first to satisfy Qt requirements
# Import QApplication after QtWebEngineWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
from PyQt6.QtWidgets import QApplication

# Create a single QApplication instance for all tests
qt_app = QApplication.instance()
if qt_app is None:
    qt_app = QApplication(sys.argv)


import pytest


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QApplication instance."""
    yield qt_app


@pytest.fixture
def markdown_editor():
    """Create a MarkdownEditorPyQt instance, yield it, then close."""
    from markdown_editor_pkg.editor import MarkdownEditorPyQt

    editor = MarkdownEditorPyQt()
    editor.setWindowTitle("Test Editor")
    # Stop auto_save_timer to prevent it from triggering during tests
    editor.auto_save_timer.stop()
    yield editor
    # Stop all timers before cleanup
    editor.auto_save_timer.stop()
    editor.preview_timer.stop()


@pytest.fixture
def tmp_md(tmp_path):
    """Create a temporary .md file path."""
    return tmp_path / "test.md"
