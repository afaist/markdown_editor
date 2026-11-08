"""download_mathjax.py — Загрузка библиотеки MathJax в папку markdown_editor_pkg/mathjax/.

Эквивалент скрипта для KaTeX, но для MathJax 3 (поддерживает TikZ и полный LaTeX).
Запускается из корня проекта:
    python markdown_editor_pkg/download_mathjax.py
"""

import io
import os
import sys
import urllib.error
import urllib.request

# Fix console encoding on Windows (cp1252/cp1251 -> UTF-8)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Версия MathJax
MATHJAX_VERSION = "3.2.2"
MATHJAX_URL_BASE = f"https://cdn.jsdelivr.net/npm/mathjax@{MATHJAX_VERSION}/es5"

FILES = [
    ("tex-mml-chtml.js", f"{MATHJAX_URL_BASE}/tex-mml-chtml.js"),
]


def download_file(url: str, destination: str) -> None:
    """Скачать файл по URL в указанное место назначения."""
    try:
        dir_name = os.path.dirname(destination)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

        print(f"Скачивание: {url} ...")
        urllib.request.urlretrieve(url, destination)
        print(f"✓ Успешно сохранено: {destination}")
    except (OSError, urllib.error.URLError) as e:
        print(f"✗ Ошибка при скачивании {url}: {e}")


def main():
    """Загрузить ресурсы MathJax из CDN в локальную папку mathjax/."""
    # Путь к папке mathjax внутри пакета
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mathjax_dir = os.path.join(script_dir, "mathjax")

    # Создаём папку, если нет
    if not os.path.exists(mathjax_dir):
        os.makedirs(mathjax_dir)
        print(f"Создана директория: {mathjax_dir}")

    for filename, url in FILES:
        dest_path = os.path.join(mathjax_dir, filename)
        download_file(url, dest_path)

    print("\n✅ Загрузка ресурсов MathJax завершена.")


if __name__ == "__main__":
    main()
