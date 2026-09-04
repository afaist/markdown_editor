"""Pytest configuration for markdown_editor tests."""

import os
import sys

# Set environment BEFORE importing anything else
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Import QtWebEngineWidgets first to satisfy Qt requirements
from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401

# Import QApplication after QtWebEngineWidgets
from PyQt6.QtWidgets import QApplication

# Create a single QApplication instance for all tests
qt_app = QApplication.instance()
if qt_app is None:
    qt_app = QApplication(sys.argv)
