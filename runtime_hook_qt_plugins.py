"""Runtime hook: set Qt platform plugin path for PyInstaller bundles."""

import os
import sys

# In PyInstaller bundle, plugins are in the same directory as the executable
# or in the bundled PyQt6/Qt6/plugins path
if getattr(sys, "frozen", False):
    # sys._MEIPASS is for the temp extract dir during onefile mode
    # For onefile mode, extract the bundle dir
    if hasattr(sys, "_MEIPASS"):
        plugin_path = os.path.join(sys._MEIPASS, "PyQt6", "Qt6", "plugins")
    else:
        # COLLECT mode (onedir): the exe is inside dist/markdown-editor/
        # and PyQt6/Qt6/plugins/ is a sibling directory
        bundle_dir = os.path.dirname(sys.executable)
        plugin_path = os.path.join(bundle_dir, "PyQt6", "Qt6", "plugins")

    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
