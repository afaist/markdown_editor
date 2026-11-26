"""download_mathjax.py — Загрузка MathJax из CDN."""

import io
import os
import sys
import urllib.error
import urllib.request

# Fix console encoding on Windows (cp1252/cp1251 -> UTF-8)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Fix console encoding on Windows (cp1252/cp1251 -> UTF-8)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


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
    """Загрузить MathJax из CDN в локальную папку mathjax/."""
    version = "3"
    base_url = f"https://cdn.jsdelivr.net/npm/mathjax@{version}/es5"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    mathjax_dir = os.path.join(script_dir, "mathjax")

    if not os.path.exists(mathjax_dir):
        os.makedirs(mathjax_dir)
        print(f"Создана директория: {mathjax_dir}")

    files_to_download = [
        ("tex-mml-chtml.js", f"{base_url}/tex-mml-chtml.js"),
    ]

    for filename, url in files_to_download:
        dest_path = os.path.join(mathjax_dir, filename)
        download_file(url, dest_path)

    print("\n✅ Загрузка MathJax завершена.")


if __name__ == "__main__":
    main()
