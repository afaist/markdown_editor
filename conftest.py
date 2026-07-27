"""Pytest configuration for markdown_editor tests"""

import sys
import os

# Set environment BEFORE importing anything else
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Import QtWebEngineWidgets first to satisfy Qt requirements
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication

# Create a single QApplication instance for all tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)
