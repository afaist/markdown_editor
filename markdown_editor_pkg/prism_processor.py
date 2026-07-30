"""PrismJSProcessor — управление ресурсами и интеграцией Prism.js для подсветки кода."""

import os


class PrismJSProcessor:
    """Управление ресурсами и интеграцией Prism.js."""

    # Константы путей (относительно base_dir, где находится markdown_editor_pkg)
    PRISM_JS = "prism/prism.min.js"
    PRISM_CSS = "prism/themes/prism-okaidia.min.css"

    # Список поддерживаемых языков (соответствуют файлам в components/)
    PRISM_LANGUAGES = [
        "python",
        "java",
        "c",
        "cpp",
        "javascript",
        "typescript",
        "bash",
        "sql",
        "css",
        "markup",  # markup = HTML в Prism.js
    ]

    # Маппинг тем предпросмотра -> темы Prism.js
    PRISM_THEME_MAP = {
        "light": "prism-okaidia.min.css",
        "dark": "prism-tomorrow.min.css",
        "contrast": "prism-okaidia.min.css",  # fallback для контрастной
    }

    def __init__(self):
        pass

    def get_prism_css_path(self, theme_name: str) -> str:
        """Получить путь к CSS Prism.js в зависимости от темы."""
        filename = self.PRISM_THEME_MAP.get(theme_name, self.PRISM_THEME_MAP["light"])
        return f"prism/themes/{filename}"

    def get_prism_js_components(self) -> list:
        """Получить список путей к компонентам Prism.js."""
        return [f"prism/components/prism-{lang}.min.js" for lang in self.PRISM_LANGUAGES]

    def inject_prism(self, html: str, theme_name: str, base_dir: str) -> str:
        """Встроить Prism.js CSS и JS в HTML-документ."""
        prism_css = self.get_prism_css_path(theme_name)
        prism_css_path = os.path.join(base_dir, prism_css) if base_dir else prism_css
        prism_js_path = os.path.join(base_dir, self.PRISM_JS) if base_dir else self.PRISM_JS

        # Собираем пути к компонентам
        components_paths = []
        for comp in self.get_prism_js_components():
            comp_path = os.path.join(base_dir, comp) if base_dir else comp
            components_paths.append(comp_path)

        # Генерируем скрипты компонентов
        component_scripts = "\n".join(
            f"<script src=\"file://{path}\"></script>" for path in components_paths
        )

        # Вставляем CSS перед закрывающим </head>
        head_css = f'<link rel="stylesheet" href="file://{prism_css_path}">'
        if "<head>" in html:
            html = html.replace("<head>", f"<head>\n    {head_css}", 1)
        elif "<head>" in html:
            html = html.replace("<head>", f"<head>\n    {head_css}", 1)

        # Вставляем JS перед закрывающим </body>
        prism_inject = f"""
<script src="file://{prism_js_path}"></script>
{component_scripts}
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        Prism.highlightAll();
    }});
</script>"""

        if "</body>" in html:
            html = html.replace("</body>", f"{prism_inject}\n</body>", 1)

        return html
