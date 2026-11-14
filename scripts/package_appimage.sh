#!/usr/bin/env bash
# package_appimage.sh — Сборка AppImage для Markdown Editor
#
# Использование:
#   ./scripts/package_appimage.sh <source_dir> <output_dir> <version>
#
# Пример:
#   ./scripts/package_appimage.sh dist/markdown-editor dist/appimage 1.1.0

set -euo pipefail

SOURCE_DIR="${1:?Usage: $0 <source_dir> <output_dir> <version>}"
OUTPUT_DIR="${2:?Usage: $0 <source_dir> <output_dir> <version>}"
VERSION="${3:?Usage: $0 <source_dir> <output_dir> <version>}"

APP_NAME="markdown-editor"
APPDIR="appimage-build/${APP_NAME}.appdir"

echo "[INFO] Подготовка AppImage v${VERSION}..."

# Очистка
rm -rf "appimage-build"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/metainfo"

# Копируем собранные файлы
cp -r "$SOURCE_DIR"/* "$APPDIR/usr/bin/"

# Копируем Qt6 библиотеки из pip-пакета
echo "[INFO] Копирование Qt6 библиотек..."
python3 << 'PYEOF'
import os
from pathlib import Path
import shutil
import PyQt6
import PyQt6.QtWebEngineCore

appdir = Path("appimage-build") / "markdown-editor.appdir"

pyqt6_base = Path(PyQt6.__file__).parent
qt_lib_dir = appdir / "usr" / "lib" / "qt6"
qt_lib_dir.mkdir(parents=True, exist_ok=True)

# Qt lib
qt6_lib = pyqt6_base / "Qt" / "lib"
if qt6_lib.exists():
    for item in qt6_lib.iterdir():
        if item.is_dir():
            shutil.copytree(item, qt_lib_dir / item.name, dirs_exist_ok=True)
        else:
            shutil.copy2(item, qt_lib_dir)

# Qt plugins
qt6_plugins = pyqt6_base / "Qt" / "plugins"
if qt6_plugins.exists():
    for plugin_subdir in qt6_plugins.iterdir():
        if plugin_subdir.is_dir():
            target = qt_lib_dir / "plugins" / plugin_subdir.name
            target.mkdir(parents=True, exist_ok=True)
            for pfile in plugin_subdir.iterdir():
                if pfile.is_file():
                    shutil.copy2(pfile, target)

# Qt qml
qt6_qml = pyqt6_base / "Qt" / "qml"
if qt6_qml.exists():
    for item in qt6_qml.iterdir():
        if item.is_dir():
            shutil.copytree(item, qt_lib_dir / "qml" / item.name, dirs_exist_ok=True)
        else:
            shutil.copy2(item, qt_lib_dir / "qml")

# Qt translations
qt6_trans = pyqt6_base / "Qt" / "translations"
if qt6_trans.exists():
    shutil.copytree(qt6_trans, qt_lib_dir / "translations", dirs_exist_ok=True)

# Qt bin (icudtl.dat, etc.)
qt6_bin = pyqt6_base / "Qt" / "bin"
if qt6_bin.exists():
    for item in qt6_bin.iterdir():
        if item.is_file():
            shutil.copy2(item, qt_lib_dir / item.name)

# PyQt6 _internal
pyqt6_internal = pyqt6_base / "_internal"
if pyqt6_internal.exists():
    for item in pyqt6_internal.iterdir():
        if item.is_file():
            shutil.copy2(item, appdir / "usr" / "bin")
PYEOF

# Desktop file
cp markdown-editor.desktop "$APPDIR/usr/share/applications/${APP_NAME}.desktop"
sed -i 's|Exec=/opt/markdown-editor/markdown-editor|Exec=markdown-editor|' \
    "$APPDIR/usr/share/applications/${APP_NAME}.desktop"

# Icon
if [ -f "icon.png" ]; then
    python3 -c '
from PIL import Image
import shutil
src = Image.open("icon.png")
# Resize to 256x256 square
src.thumbnail((256, 256), Image.LANCZOS)
# Ensure square by center-cropping if needed
w, h = src.size
if w != h:
    x = (w - h) // 2 if w > h else 0
    y = (h - w) // 2 if h > w else 0
    src = src.crop((x, y, x + min(w,h), y + min(w,h)))
    src = src.resize((256, 256), Image.LANCZOS)
src.save("appimage-build/markdown-editor.appdir/usr/share/icons/hicolor/256x256/apps/markdown-editor.png")
'
fi

# Metainfo
cat > "$APPDIR/usr/share/metainfo/${APP_NAME}.metainfo.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>${APP_NAME}</id>
  <name>Markdown Editor</name>
  <summary>Простой редактор Markdown с предпросмотром и поддержкой LaTeX</summary>
  <description>
    <p>Markdown-редактор с live-предпросмотром, поддержкой LaTeX-формул (KaTeX),
    синтаксическим выделением (Prism.js) и экспортом в PDF/HTML.</p>
  </description>
  <url type="homepage">https://github.com/afaist/markdown_editor</url>
  <provides>
    <binary>${APP_NAME}</binary>
  </provides>
  <launchable type="desktop-id">${APP_NAME}.desktop</launchable>
</component>
EOF

# Устанавливаем RPATH
patchelf --set-rpath '$ORIGIN/../lib/qt6:$ORIGIN' "$APPDIR/usr/bin/${APP_NAME}"

# Сборка AppImage
echo "[INFO] Сборка AppImage через linuxdeploy..."
export APPIMAGE_EXTRACT_AND_RUN=1

linuxdeploy \
    --appdir "$APPDIR" \
    --desktop-file "$APPDIR/usr/share/applications/${APP_NAME}.desktop" \
    --icon-file "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png" \
    --executable "$APPDIR/usr/bin/${APP_NAME}" \
    --output appimage

# Переименовываем
OUTPUT_FILE="${OUTPUT_DIR}/${APP_NAME}-x86_64.appimage"
if [ -f "${APP_NAME}-${VERSION}-x86_64.AppImage" ]; then
    mv "${APP_NAME}-${VERSION}-x86_64.AppImage" "$OUTPUT_FILE"
elif [ -f "${APP_NAME}-x86_64.AppImage" ]; then
    mv "${APP_NAME}-x86_64.AppImage" "$OUTPUT_FILE"
fi

# Очистка
rm -rf "appimage-build"

echo "[OK] AppImage создана: $OUTPUT_FILE"
echo "[INFO] Размер: $(du -sh "$OUTPUT_FILE" 2>/dev/null | cut -f1)"
