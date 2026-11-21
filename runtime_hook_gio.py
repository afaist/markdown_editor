"""Runtime hook to prevent GIO from loading system modules that conflict with bundled GLib."""

import os
import sys

# GIO is a Linux-specific D-Bus/GVfs subsystem. On Windows this is irrelevant
# and may cause unnecessary warnings in Qt's plugin loader.
if sys.platform != "win32":
    os.environ["GIO_EXTRA_MODULES"] = ""
