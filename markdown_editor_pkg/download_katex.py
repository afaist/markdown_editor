"""download_katex.py — Загрузка библиотеки KaTeX в папку markdown_editor_pkg/katex/.

Эквивалент bash-скрипта get_katex.sh, но на Python (без зависимости от wget).
Запускается из корня проекта:
    python markdown_editor_pkg/download_katex.py
"""

import os
import urllib.error
import urllib.request

# Версия KaTeX
KATEX_VERSION = "0.16.9"
KATEX_URL_BASE = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist"

FILES = [
    ("katex.min.css", f"{KATEX_URL_BASE}/katex.min.css"),
    ("katex.min.js", f"{KATEX_URL_BASE}/katex.min.js"),
    ("auto-render.min.js", f"{KATEX_URL_BASE}/contrib/auto-render.min.js"),
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
    # Путь к папке katex внутри пакета
    script_dir = os.path.dirname(os.path.abspath(__file__))
    katex_dir = os.path.join(script_dir, "katex")

    # Создаём папку, если нет
    if not os.path.exists(katex_dir):
        os.makedirs(katex_dir)
        print(f"Создана директория: {katex_dir}")

    for filename, url in FILES:
        dest_path = os.path.join(katex_dir, filename)
        download_file(url, dest_path)

    print("\n✅ Загрузка ресурсов KaTeX завершена.")


if __name__ == "__main__":
    main()
