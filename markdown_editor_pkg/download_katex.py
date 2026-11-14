"""download_katex.py — Загрузка ресурсов KaTeX."""

import io
import os
import sys
import urllib.error
import urllib.request


def download_file(url: str, destination: str) -> None:
    """Скачать файл по URL в указанное место назначения.

    Args:
        url: URL файла для загрузки.
        destination: Локальный путь для сохранения файла.
    """
    try:
        dir_name = os.path.dirname(destination)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

        print(f"Скачивание: {url} ...")
        urllib.request.urlretrieve(url, destination)
        print(f"✓ Успешно сохранено: {destination}")
    except (OSError, urllib.error.URLError) as e:
        print(f"✗ Ошибка при скачивании {url}: {e}")


def main() -> None:
    """Загрузить ресурсы KaTeX из CDN в локальную папку katex/."""
    version = "0.16.21"
    base_url = f"https://cdnjs.cloudflare.com/ajax/libs/KaTeX/{version}"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    katex_dir = os.path.join(script_dir, "katex")

    if not os.path.exists(katex_dir):
        os.makedirs(katex_dir)
        print(f"Создана директория: {katex_dir}")

    files_to_download = [
        # Основной JS
        ("katex.min.js", f"{base_url}/katex.min.js"),
        # Auto-render (авто-рендеринг формул в тексте)
        ("contrib/auto-render.min.js", f"{base_url}/contrib/auto-render.min.js"),
        # CSS
        ("katex.min.css", f"{base_url}/katex.min.css"),
        # Fonts — скачиваем все ttf из папки fonts
    ]

    for filename, url in files_to_download:
        dest_path = os.path.join(katex_dir, filename)
        download_file(url, dest_path)

    # Скачиваем шрифты
    fonts_dir = os.path.join(katex_dir, "fonts")
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
        print(f"Создана директория: {fonts_dir}")

    font_files = [
        "KaTeX_Main-Regular.woff2",
        "KaTeX_Main-Bold.woff2",
        "KaTeX_Main-Italic.woff2",
        "KaTeX_Main-BoldItalic.woff2",
        "KaTeX_SansSerif-Regular.woff2",
        "KaTeX_SansSerif-Bold.woff2",
        "KaTeX_SansSerif-Italic.woff2",
        "KaTeX_Fraktur-Regular.woff2",
        "KaTeX_Fraktur-Bold.woff2",
        "KaTeX_Script-Regular.woff2",
        "KaTeX_Script-Bold.woff2",
        "KaTeX_Size1-Regular.woff2",
        "KaTeX_Size2-Regular.woff2",
        "KaTeX_Size3-Regular.woff2",
        "KaTeX_Size4-Regular.woff2",
        "KaTeX_Math-Italic.woff2",
        "KaTeX_Math-BoldItalic.woff2",
        "KaTeX_Main-Regular.woff",
        "KaTeX_Main-Bold.woff",
        "KaTeX_Main-Italic.woff",
        "KaTeX_Main-BoldItalic.woff",
        "KaTeX_SansSerif-Regular.woff",
        "KaTeX_SansSerif-Bold.woff",
        "KaTeX_SansSerif-Italic.woff",
        "KaTeX_Fraktur-Regular.woff",
        "KaTeX_Fraktur-Bold.woff",
        "KaTeX_Script-Regular.woff",
        "KaTeX_Script-Bold.woff",
        "KaTeX_Size1-Regular.woff",
        "KaTeX_Size2-Regular.woff",
        "KaTeX_Size3-Regular.woff",
        "KaTeX_Size4-Regular.woff",
        "KaTeX_Math-Italic.woff",
        "KaTeX_Math-BoldItalic.woff",
        "KaTeX_Caligraphic-Regular.woff2",
        "KaTeX_Caligraphic-Bold.woff2",
        "KaTeX_Caligraphic-Regular.woff",
        "KaTeX_Caligraphic-Bold.woff",
        "KaTeX_Main-Regular.ttf",
        "KaTeX_Main-Bold.ttf",
        "KaTeX_Main-Italic.ttf",
        "KaTeX_Main-BoldItalic.ttf",
        "KaTeX_SansSerif-Regular.ttf",
        "KaTeX_SansSerif-Bold.ttf",
        "KaTeX_SansSerif-Italic.ttf",
        "KaTeX_Fraktur-Regular.ttf",
        "KaTeX_Fraktur-Bold.ttf",
        "KaTeX_Script-Regular.ttf",
        "KaTeX_Script-Bold.ttf",
        "KaTeX_Size1-Regular.ttf",
        "KaTeX_Size2-Regular.ttf",
        "KaTeX_Size3-Regular.ttf",
        "KaTeX_Size4-Regular.ttf",
        "KaTeX_Math-Italic.ttf",
        "KaTeX_Math-BoldItalic.ttf",
        "KaTeX_Caligraphic-Regular.ttf",
        "KaTeX_Caligraphic-Bold.ttf",
    ]

    for font in font_files:
        url = f"{base_url}/fonts/{font}"
        dest_path = os.path.join(fonts_dir, font)
        download_file(url, dest_path)

    print("\n✅ Загрузка ресурсов KaTeX завершена.")


if __name__ == "__main__":
    main()
