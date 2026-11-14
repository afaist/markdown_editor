#!/usr/bin/env bash
# package_deb.sh — Сборка .deb пакета для Markdown Editor
#
# Использование:
#   ./scripts/package_deb.sh <source_dir> <output_dir> <version>
#
# Пример:
#   ./scripts/package_deb.sh dist/markdown-editor dist/deb 1.1.0

set -euo pipefail

SOURCE_DIR="${1:?Usage: $0 <source_dir> <output_dir> <version>}"
OUTPUT_DIR="${2:?Usage: $0 <source_dir> <output_dir> <version>}"
VERSION="${3:?Usage: $0 <source_dir> <output_dir> <version>}"

ARCH="$(dpkg --print-architecture)"
DEB_NAME="markdown-editor_${VERSION}_${ARCH}.deb"

echo "[INFO] Сборка .deb пакета v${VERSION} (${ARCH})..."

# Очистка
rm -rf deb-build
mkdir -p deb-build/markdown-editor/DEBIAN
mkdir -p deb-build/markdown-editor/opt/markdown-editor
mkdir -p deb-build/markdown-editor/usr/share/applications
mkdir -p deb-build/markdown-editor/usr/share/pixmaps

# Копируем файлы
cp -r "$SOURCE_DIR"/* deb-build/markdown-editor/opt/markdown-editor/

# Создаём control файл
cat > deb-build/markdown-editor/DEBIAN/control <<EOF
Package: markdown-editor
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: libgl1, libxkbcommon-x11-0, libegl1, libxcb-cursor0, libfontconfig1, libfreetype6
Maintainer: afaist <afaist@github.com>
Description: Простой редактор Markdown с предпросмотром и поддержкой LaTeX
  Markdown-редактор с live-предпросмотром, поддержкой LaTeX-формул (KaTeX),
  синтаксическим выделением (Prism.js) и экспортом в PDF/HTML.
EOF

# Создаём .desktop файл
cp markdown-editor.desktop deb-build/markdown-editor/usr/share/applications/markdown-editor.desktop
sed -i 's|Exec=/opt/markdown-editor/markdown-editor|Exec=/opt/markdown-editor/markdown-editor|' \
    deb-build/markdown-editor/usr/share/applications/markdown-editor.desktop

# Создаём deb
mkdir -p "$OUTPUT_DIR"
dpkg-deb --build \
    --root-owner-group \
    deb-build/markdown-editor \
    "$OUTPUT_DIR/$DEB_NAME"

# Очистка
rm -rf deb-build

echo "[OK] .deb пакет создан: $OUTPUT_DIR/$DEB_NAME"
echo "[INFO] Размер: $(du -sh "$OUTPUT_DIR/$DEB_NAME" 2>/dev/null | cut -f1)"
