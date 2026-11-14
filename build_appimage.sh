#!/usr/bin/env bash
# build_appimage.sh — Скрипт сборки AppImage для Markdown Editor
#
# Использование:
#   ./build_appimage.sh              # Сборка AppImage (по умолчанию)
#   ./build_appimage.sh clean        # Очистка артефактов сборки
#
# Требования:
#   pip install pyinstaller PyQt6 PyQt6-WebEngine markdown
#   sudo apt-get install -y linuxdeploy patchelf
#
# Ссылки:
#   https://appimage.org/
#   https://github.com/linuxdeploy/linuxdeploy

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ─── Цвета для вывода ──────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── Проверка зависимостей ─────────────────────────────────────────────
check_dependencies() {
    log_info "Проверка зависимостей..."

    if ! command -v python3 &>/dev/null; then
        log_error "python3 не найден. Установите Python 3.12+"
        exit 1
    fi

    if ! command -v pyinstaller &>/dev/null; then
        log_warn "PyInstaller не найден. Устанавливаю..."
        pip3 install --user pyinstaller
    fi

    if ! command -v linuxdeploy &>/dev/null; then
        log_error "linuxdeploy не найден. Установите:"
        log_error "  wget -O linuxdeploy https://github.com/linuxdeploy/linuxdeploy/releases/latest/download/linuxdeploy-x86_64.AppImage"
        log_error "  chmod +x linuxdeploy"
        log_error "  sudo mv linuxdeploy /usr/local/bin/"
        exit 1
    fi

    if ! command -v patchelf &>/dev/null; then
        log_error "patchelf не найден. Установите:"
        log_error "  sudo apt-get install -y patchelf"
        exit 1
    fi

    # Проверяем, что ресурсы katex и prism существуют
    if [ ! -d "markdown_editor_pkg/katex" ]; then
        log_warn "Папка katex не найдена. Скачиваю ресурсы..."
        python3 markdown_editor_pkg/download_katex.py
    fi

    if [ ! -d "markdown_editor_pkg/prism" ]; then
        log_warn "Папка prism не найдена. Скачиваю ресурсы..."
        python3 markdown_editor_pkg/download_prism.py
    fi

    log_success "Зависимости проверены"
}

# ─── Сборка AppImage ───────────────────────────────────────────────────
build_appimage() {
    log_info "Начало сборки AppImage..."

    local app_name="markdown-editor"
    local app_version
    app_version=$(python3 -c '
try:
    from setuptools_scm import get_version
    print(get_version())
except Exception:
    print("0.0.0")
')

    # Шаг 1: Сборка PyInstaller (onedir)
    log_info "Шаг 1/3: Сборка PyInstaller (onedir)..."
    pyinstaller --clean --noconfirm markdown-editor.spec

    # Шаг 2: Подготовка структуры для linuxdeploy
    log_info "Шаг 2/3: Подготовка структуры..."

    local appimage_dir="appimage-build"
    rm -rf "$appimage_dir"
    mkdir -p "$appimage_dir/${app_name}.appdir/usr/bin"
    mkdir -p "$appimage_dir/${app_name}.appdir/usr/lib"
    mkdir -p "$appimage_dir/${app_name}.appdir/usr/share/applications"
    mkdir -p "$appimage_dir/${app_name}.appdir/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "$appimage_dir/${app_name}.appdir/usr/share/metainfo"

    # Копируем собранные файлы
    cp -r dist/${app_name}/* "$appimage_dir/${app_name}.appdir/usr/bin/"

    # Копируем Qt6 библиотеки из pip-пакета
    log_info "Копирование Qt6 библиотек..."
    python3 -c '
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
'

    # Создаём .desktop файл
    cp markdown-editor.desktop "$appimage_dir/${app_name}.appdir/usr/share/applications/${app_name}.desktop"
    sed -i 's|Exec=/opt/markdown-editor/markdown-editor|Exec=markdown-editor|' \
        "$appimage_dir/${app_name}.appdir/usr/share/applications/${app_name}.desktop"

    # Копируем иконку с ресайзом
    if [ -f "icon.png" ]; then
        python3 -c '
from PIL import Image
src = Image.open("icon.png")
w, h = src.size
src.thumbnail((256, 256), Image.LANCZOS)
if w != h:
    x = (w - h) // 2 if w > h else 0
    y = (h - w) // 2 if h > w else 0
    src = src.crop((x, y, x + min(w,h), y + min(w,h)))
    src = src.resize((256, 256), Image.LANCZOS)
src.save("appimage-build/markdown-editor.appdir/usr/share/icons/hicolor/256x256/apps/markdown-editor.png")
'
    elif [ -f "icon.ico" ]; then
        log_warn "icon.ico найден, но для AppImage нужен PNG. Иконка может отсутствовать."
    fi

    # Создаём metainfo (AppStream)
    cat > "$appimage_dir/${app_name}.appdir/usr/share/metainfo/${app_name}.metainfo.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>${app_name}</id>
  <name>Markdown Editor</name>
  <summary>Простой редактор Markdown с предпросмотром и поддержкой LaTeX</summary>
  <description>
    <p>Markdown-редактор с live-предпросмотром, поддержкой LaTeX-формул (KaTeX),
    синтаксическим выделением (Prism.js) и экспортом в PDF/HTML.</p>
  </description>
  <url type="homepage">https://github.com/afaist/markdown_editor</url>
  <provides>
    <binary>${app_name}</binary>
  </provides>
  <launchable type="desktop-id">${app_name}.desktop</launchable>
</component>
EOF

    # Шаг 3: Сборка AppImage через linuxdeploy
    log_info "Шаг 3/3: Сборка AppImage..."

    # Устанавливаем RPATH
    RPATH_VAL='$ORIGIN/../lib/qt6:$ORIGIN'
    patchelf --set-rpath "$RPATH_VAL" "$appimage_dir/${app_name}.appdir/usr/bin/${app_name}" || true

    export APPIMAGE_EXTRACT_AND_RUN=1

    linuxdeploy \
        --appdir "$appimage_dir/${app_name}.appdir" \
        --desktop-file "$appimage_dir/${app_name}.appdir/usr/share/applications/${app_name}.desktop" \
        --icon-file "$appimage_dir/${app_name}.appdir/usr/share/icons/hicolor/256x256/apps/${app_name}.png" \
        --executable "$appimage_dir/${app_name}.appdir/usr/bin/${app_name}" \
        --output appimage

    # Переименовываем в понятное имя
    local output_file="dist/${app_name}-x86_64.appimage"
    if [ -f "${app_name}-${app_version}-x86_64.AppImage" ]; then
        mv "${app_name}-${app_version}-x86_64.AppImage" "$output_file"
    elif [ -f "${app_name}-x86_64.AppImage" ]; then
        mv "${app_name}-x86_64.AppImage" "$output_file"
    fi

    # Очистка временных файлов
    rm -rf "$appimage_dir"

    log_success "AppImage создана: $output_file"
    log_info "Размер: $(du -sh "$output_file" 2>/dev/null | cut -f1)"
}

# ─── Очистка ───────────────────────────────────────────────────────────
clean() {
    log_info "Очистка артефактов сборки..."
    rm -rf build dist appimage-build
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    log_success "Очистка завершена"
}

# ─── Главный скрипт ────────────────────────────────────────────────────
main() {
    local command="${1:-build}"

    case "$command" in
        build|appimage)
            check_dependencies
            build_appimage
            ;;
        clean)
            clean
            ;;
        *)
            echo "Использование: $0 [build|appimage|clean]"
            echo ""
            echo "  build    - Сборка AppImage (по умолчанию)"
            echo "  appimage - Сборка AppImage"
            echo "  clean    - Очистка артефактов"
            exit 1
            ;;
    esac
}

main "$@"
