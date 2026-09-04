#!/usr/bin/env bash
# build.sh — Скрипт сборки Markdown Editor для Linux
#
# Использование:
#   ./build.sh              # Сборка в папку (onedir)
#   ./build.sh onefile      # Сборка в один файл
#   ./build.sh deb          # Сборка .deb пакета
#   ./build.sh clean        # Очистка артефактов сборки
#
# Требования:
#   pip install pyinstaller PyQt6 PyQt6-WebEngine markdown

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ─── Цвета для вывода ──────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# ─── Сборка ────────────────────────────────────────────────────────────
build() {
    local mode="${1:-onedir}"

    log_info "Сборка в режиме: $mode"

    local extra_args=""
    case "$mode" in
        onedir)
            extra_args="--onedir"
            log_info "Режим: одна папка (рекомендуется для PyQt6-WebEngine)"
            ;;
        onefile)
            extra_args="--onefile"
            log_warn "Режим: один файл (медленнее старт, больше размер)"
            ;;
        *)
            log_error "Неизвестный режим: $mode"
            echo "Использование: $0 [onedir|onefile|deb|clean]"
            exit 1
            ;;
    esac

    # Запуск PyInstaller
    log_info "Запуск PyInstaller..."
    pyinstaller --clean --noconfirm markdown-editor.spec

    log_success "Сборка завершена!"
    log_info "Артефакты в: dist/"

    # Показываем размер
    if [ "$mode" = "onedir" ]; then
        local size
        size=$(du -sh "dist/markdown-editor" 2>/dev/null | cut -f1)
        log_info "Размер сборки: $size"
    fi
}

# ─── Сборка .deb пакета ────────────────────────────────────────────────
build_deb() {
    log_info "Сборка .deb пакета..."

    # Сначала собираем in onedir
    build "onedir"

    # Проверяем наличие fpm
    if ! command -v fpm &>/dev/null; then
        log_warn "fpm не найден. Установка через gem..."
        sudo apt-get install -y ruby gem 2>/dev/null || true
        sudo gem install fpm 2>/dev/null || {
            log_error "Не удалось установить fpm. Создаю .deb вручную."
            build_deb_manual
            return
        }
    fi

    # Создаём .deb через fpm
    local version
    version=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || echo "1.0.0")

    fpm --input-type dir \
        --output-type deb \
        --name "markdown-editor" \
        --version "$version" \
        --architecture "$(dpkg --print-architecture)" \
        --description "Простой редактор Markdown с предпросмотром и поддержкой LaTeX" \
        --maintainer "Markdown Editor Authors" \
        --url "https://github.com/USER/markdown_editor" \
        --depends "qtwebengine5-dev" \
        --depends "libgl1-mesa-glx" \
        --depends "libxkbcommon-x11-0" \
        --depends "libegl1" \
        --depends "libxcb-cursor0" \
        --deb-systemd-template "markdown-editor.service" \
        --package "dist/markdown-editor_${version}_$(dpkg --print-architecture).deb" \
        "dist/markdown-editor/=/opt/markdown-editor"

    log_success ".deb пакет создан: dist/markdown-editor_${version}_$(dpkg --print-architecture).deb"
}

# ─── Ручная сборка .deb ────────────────────────────────────────────────
build_deb_manual() {
    log_info "Создание .deb пакета вручную..."

    local version
    version=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || echo "1.0.0")

    local deb_dir="deb-build/markdown-editor/opt/markdown-editor"
    mkdir -p "$deb_dir"

    # Копируем собранные файлы
    cp -r dist/markdown-editor/* "$deb_dir/"

    # Создаём .desktop файл
    mkdir -p "deb-build/markdown-editor/DEBIAN"
    cat > "deb-build/markdown-editor/DEBIAN/control" <<EOF
Package: markdown-editor
Version: $version
Section: utils
Priority: optional
Architecture: $(dpkg --print-architecture)
Depends: qtwebengine5-dev, libgl1-mesa-glx, libxkbcommon-x11-0, libegl1
Maintainer: Markdown Editor Authors
Description: Простой редактор Markdown с предпросмотром и поддержкой LaTeX
EOF

    # Создаём .desktop файл
    mkdir -p "deb-build/markdown-editor/usr/share/applications"
    cat > "deb-build/markdown-editor/usr/share/applications/markdown-editor.desktop" <<EOF
[Desktop Entry]
Name=Markdown Editor
Comment=Простой редактор Markdown с поддержкой LaTeX
Exec=/opt/markdown-editor/markdown-editor
Icon=markdown-editor
Terminal=false
Type=Application
Categories=Utility;TextEditor;
MimeType=text/markdown;text/x-markdown;
EOF

    # Создаём deb
    dpkg-deb --build "deb-build/markdown-editor" "dist/markdown-editor_${version}_$(dpkg --print-architecture).deb"

    log_success ".deb пакет создан: dist/markdown-editor_${version}_$(dpkg --print-architecture).deb"
}

# ─── Очистка ───────────────────────────────────────────────────────────
clean() {
    log_info "Очистка артефактов сборки..."
    rm -rf build dist markdown_editor.spec.spec
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    rm -rf deb-build 2>/dev/null || true
    log_success "Очистка завершена"
}

# ─── Главный скрипт ────────────────────────────────────────────────────
main() {
    local command="${1:-build}"

    case "$command" in
        build|onedir|onefile)
            check_dependencies
            build "$command"
            ;;
        deb)
            check_dependencies
            build_deb
            ;;
        clean)
            clean
            ;;
        *)
            echo "Использование: $0 [build|onedir|onefile|deb|clean]"
            echo ""
            echo "  build    - Сборка в папку (по умолчанию)"
            echo "  onedir   - Сборка в одну папку"
            echo "  onefile  - Сборка в один файл"
            echo "  deb      - Сборка .deb пакета"
            echo "  clean    - Очистка артефактов"
            exit 1
            ;;
    esac
}

main "$@"
