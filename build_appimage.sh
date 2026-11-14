#!/usr/bin/env bash
# build_appimage.sh — Скрипт сборки AppImage для Markdown Editor
#
# Использование:
#   ./build_appimage.sh              # Сборка AppImage (по умолчанию)
#   ./build_appimage.sh clean        # Очистка артефактов сборки
#
# Требования:
#   pip install pyinstaller PyQt6 PyQt6-WebEngine markdown
#   sudo apt-get install -y linuxdeploy linuxdeploy-plugin-qt
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
        log_error ""
        log_error "  wget -O linuxdeploy-plugin-qt https://github.com/linuxdeploy/linuxdeploy-plugin-qt/releases/latest/download/linuxdeploy-plugin-qt-x86_64.AppImage"
        log_error "  chmod +x linuxdeploy-plugin-qt"
        log_error "  sudo mv linuxdeploy-plugin-qt /usr/local/bin/"
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
    app_version=$(python3 -c "
try:
    from importlib.metadata import version
    print(version('markdown-editor'))
except Exception:
    try:
        from setuptools_scm import get_version
        print(get_version())
    except Exception:
        print('0.0.0')
" 2>/dev/null || echo "dev")

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

    # Создаём .desktop файл
    cp markdown-editor.desktop "$appimage_dir/${app_name}.appdir/usr/share/applications/${app_name}.desktop"
    sed -i 's|Exec=/opt/markdown-editor/markdown-editor|Exec=markdown-editor|' \
        "$appimage_dir/${app_name}.appdir/usr/share/applications/${app_name}.desktop"

    # Копируем иконку
    if [ -f "icon.png" ]; then
        cp icon.png "$appimage_dir/${app_name}.appdir/usr/share/icons/hicolor/256x256/apps/${app_name}.png"
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

    export APPIMAGE_EXTRACT_AND_RUN=1

    linuxdeploy \
        --appdir "$appimage_dir/${app_name}.appdir" \
        --desktop-file "$appimage_dir/${app_name}.appdir/usr/share/applications/${app_name}.desktop" \
        --icon-file "$appimage_dir/${app_name}.appdir/usr/share/icons/hicolor/256x256/apps/${app_name}.png" \
        --executable "$appimage_dir/${app_name}.appdir/usr/bin/${app_name}" \
        --plugin qt \
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
