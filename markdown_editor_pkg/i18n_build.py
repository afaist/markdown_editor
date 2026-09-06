#!/usr/bin/env python3
"""Build scripts for i18n translation files.

Usage:
    python -m markdown_editor_pkg.i18n_build lupdate
    python -m markdown_editor_pkg.i18n_build lrelease
    python -m markdown_editor_pkg.i18n_build all
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
LOCALES_DIR = PROJECT_ROOT / "locales"
TS_FILES = list(LOCALES_DIR.glob("*.ts"))


def lupdate() -> int:
    """Run lupdate to extract translatable strings from Python files."""
    pkg_dir = PROJECT_ROOT / "markdown_editor_pkg"
    py_files = list(pkg_dir.glob("*.py"))

    if not py_files:
        print("No Python files found in markdown_editor_pkg/")
        return 1

    cmd = [
        "/usr/lib/qt6/bin/lupdate",
        *map(str, py_files),
        "-ts",
        str(LOCALES_DIR / "messages.ts"),
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("lupdate completed successfully!")
    else:
        print("lupdate failed!")

    return result.returncode


def lrelease() -> int:
    """Run lrelease to compile .ts files to .qm files."""
    if not TS_FILES:
        print("No .ts files found in locales/")
        return 1

    for ts_file in TS_FILES:
        qm_file = ts_file.with_suffix(".qm")
        cmd = ["/usr/lib/qt6/bin/lrelease", str(ts_file), "-qm", str(qm_file)]

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print(f"lrelease failed for {ts_file}!")
            return result.returncode

    print("lrelease completed successfully!")
    return 0


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m markdown_editor_pkg.i18n_build [lupdate|lrelease|all]")
        return 1

    command = sys.argv[1].lower()

    if command == "lupdate":
        return lupdate()
    elif command == "lrelease":
        return lrelease()
    elif command == "all":
        lupdate_result = lupdate()
        if lupdate_result != 0:
            return lupdate_result
        return lrelease()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python -m markdown_editor_pkg.i18n_build [lupdate|lrelease|all]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
