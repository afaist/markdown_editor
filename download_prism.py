# download_prism.py
import os
import urllib.request

def download_file(url, destination):
    """Скачивает файл по URL в указанное место назначения"""
    try:
        # Создаем директорию назначения, если её нет
        dir_name = os.path.dirname(destination)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
            
        print(f"Скачивание: {url} ...")
        urllib.request.urlretrieve(url, destination)
        print(f"✓ Успешно сохранено: {destination}")
    except Exception as e:
        print(f"✗ Ошибка при скачивании {url}: {e}")

def main():
    version = "1.29.0"
    base_url = f"https://cdnjs.cloudflare.com/ajax/libs/prism/{version}"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prism_dir = os.path.join(script_dir, "prism")
    
    # Создаем папку prism
    if not os.path.exists(prism_dir):
        os.makedirs(prism_dir)
        print(f"Создана директория: {prism_dir}")

    files_to_download = [
        # Основной JS
        ("prism.min.js", f"{base_url}/prism.min.js"),
        
        # Основные языки (Python, Java, C, C++, JS, TS, Bash, SQL, CSS, HTML)
        ("components/prism-python.min.js", f"{base_url}/components/prism-python.min.js"),
        ("components/prism-java.min.js", f"{base_url}/components/prism-java.min.js"),
        ("components/prism-c.min.js", f"{base_url}/components/prism-c.min.js"),
        ("components/prism-cpp.min.js", f"{base_url}/components/prism-cpp.min.js"),
        ("components/prism-javascript.min.js", f"{base_url}/components/prism-javascript.min.js"),
        ("components/prism-typescript.min.js", f"{base_url}/components/prism-typescript.min.js"),
        ("components/prism-bash.min.js", f"{base_url}/components/prism-bash.min.js"),
        ("components/prism-sql.min.js", f"{base_url}/components/prism-sql.min.js"),
        ("components/prism-css.min.js", f"{base_url}/components/prism-css.min.js"),
        ("components/prism-markup.min.js", f"{base_url}/components/prism-markup.min.js"),
        
        # CSS Тема Okaidia
        ("themes/prism-okaidia.min.css", f"{base_url}/themes/prism-okaidia.min.css"),
        
        # Дополнительные CSS темы для поддержки тем редактора (опционально, но полезно)
        # Если вы хотите использовать другие темы, добавьте их здесь.
    ]

    for filename, url in files_to_download:
        dest_path = os.path.join(prism_dir, filename)
        download_file(url, dest_path)

    print("\n✅ Загрузка ресурсов Prism завершена.")

if __name__ == "__main__":
    main()