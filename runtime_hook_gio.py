"""Runtime hook to prevent GIO from loading system modules that conflict with bundled GLib."""
import os

# Prevent GIO from loading system GIO modules (gvfs, etc.) which may have
# incompatible GLib symbols (e.g., g_variant_builder_init_static)
os.environ["GIO_EXTRA_MODULES"] = ""
