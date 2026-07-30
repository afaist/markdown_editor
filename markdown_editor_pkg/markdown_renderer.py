# markdown_editor_pkg/markdown_renderer.py
"""Рендеринг Markdown в HTML с поддержкой LaTeX, тем и GitHub Callouts."""

import os
import re
import markdown
from PyQt6.QtCore import QUrl

from markdown_editor_pkg.latex_processor import LaTeXProcessor, StrikethroughProcessor
from markdown_editor_pkg.callout_processor import CalloutProcessor
from markdown_editor_pkg.themes import ThemesManager


class MarkdownRenderer:
    """Конвертирует Markdown-текст в полный HTML-документ с LaTeX и темами."""

    # Стили для печати/PDF
    PRINT_STYLES_TEMPLATE = """
        <style>
            {theme_css}

            /* Стили для Callouts */
            .callout {{
                padding: 1em;
                margin: 1em 0;
                border-left: 4px solid;
                background-color: var(--callout-bg, transparent);
            }}
            .callout-note {{ border-color: #0969da; background-color: #ddf4ff; color: #1a1a1a; }}
            .callout-note.dark {{ background-color: #1a1a1a; color: #ffffff; }}
            
            .callout-tip {{ border-color: #1a7f37; background-color: #dafbe1; color: #1a1a1a; }}
            .callout-tip.dark {{ background-color: #1a1a1a; color: #ffffff; }}

            .callout-important {{ border-color: #8250df; background-color: #eae6ff; color: #1a1a1a; }}
            .callout-important.dark {{ background-color: #1a1a1a; color: #ffffff; }}

            .callout-warning {{ border-color: #9a6700; background-color: #fff8c5; color: #1a1a1a; }}
            .callout-warning.dark {{ background-color: #1a1a1a; color: #ffffff; }}

            .callout-caution {{ border-color: #cf222e; background-color: #ffebe9; color: #1a1a1a; }}
            .callout-caution.dark {{ background-color: #1a1a1a; color: #ffffff; }}

            /* Стили для печати/PDF */
            @media print {{
                @page {{
                    size: A4;
                    margin: 2cm 2.5cm 2cm 2.5cm;
                    @top-center {{
                        content: "Markdown Editor";
                        font-size: 9px;
                        color: #888;
                    }}
                    @bottom-center {{
                        content: "Страница " counter(page) " из " counter(pages);
                        font-size: 9px;
                        color: #888;
                    }}
                }}
                h1, h2, h3, h4, h5, h6 {{
                    page-break-after: avoid;
                    orphans: 2;
                    widows: 2;
                }}
                h1 {{
                    page-break-before: always;
                }}
                body > h1:first-child {{
                    page-break-before: auto;
                }}
                table, img, pre {{
                    page-break-inside: avoid;
                }}
                body {{
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
                .callout {{
                    break-inside: avoid;
                }}
            }}
        </style>
    """

    # Шаблоны путей к KaTeX
    KATEX_CSS = "katex/katex.min.css"
    KATEX_JS = "katex/katex.min.js"
    KATEX_AUTO_RENDER_JS = "katex/auto-render.min.js"

    def __init__(self, themes: ThemesManager):
        self.themes = themes
        self.latex_processor = LaTeXProcessor()
        self.strikethrough_processor = StrikethroughProcessor()
        self.callout_processor = CalloutProcessor()

    def render(self, text: str, theme_name: str = "light", base_dir: str = "") -> str:
        """
        Рендерит Markdown в полный HTML-документ.
        
        Args:
            text: Markdown-текст.
            theme_name: Имя темы ("light", "dark", "contrast").
            base_dir: Директория для относительных путей к ресурсам.
        """
        # 1. Извлекаем LaTeX-формулы
        self.latex_processor.reset()
        processed_text = self.latex_processor.process(text)

        # 2. Конвертируем Markdown → HTML
        md = markdown.Markdown(
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.codehilite",
                "markdown.extensions.tables",
                "markdown.extensions.toc",
            ]
        )
        html_content = md.convert(processed_text)

        # 3. Восстанавливаем LaTeX-формулы
        html_content = self.latex_processor.restore_display(html_content)
        html_content = self.latex_processor.restore_inline(html_content)

        # 4. Зачёркивание
        html_content = self.strikethrough_processor.apply(html_content)

        # 5. GitHub Callouts
        html_content = self.callout_processor.process(html_content)

        # 6. Собираем полный HTML-документ
        theme_css = self.themes.get_preview_css()
        print_styles = self.PRINT_STYLES_TEMPLATE.format(theme_css=theme_css)

        katex_css = os.path.join(base_dir, self.KATEX_CSS) if base_dir else self.KATEX_CSS
        katex_js = os.path.join(base_dir, self.KATEX_JS) if base_dir else self.KATEX_JS
        auto_render_js = os.path.join(base_dir, self.KATEX_AUTO_RENDER_JS) if base_dir else self.KATEX_AUTO_RENDER_JS

        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Preview — {theme_name}</title>
    <link rel="stylesheet" href="file://{katex_css}">
    {print_styles}
</head>
<body>
{html_content}

<script src="file://{katex_js}"></script>
<script src="file://{auto_render_js}"></script>
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        // Проверяем, загружен ли KaTeX
        if (typeof renderMathInElement === 'undefined') {{
            console.error("KaTeX auto-render not loaded");
            return;
        }}

        // Убираем скрытые символы и нормализуем пробелы вокруг формул
        const container = document.body;
        
        // Функция для очистки содержимого
        function cleanMathElements() {{
            // Удаляем нулевые пробелы и другие скрытые символы
            container.innerHTML = container.innerHTML.replace(/[\u200B-\u200D\uFEFF]/g, '');
            
            // Иногда markdown добавляет переносы строк или пробелы, которые мешают
            // Попробуем найти все $$ ... $$ и $ ... $ и убедиться, что вокруг нет лишних символов
            // Но лучше довериться auto-render, если он настроен правильно.
        }}

        cleanMathElements();

        try {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: "$$", right: "$$", display: true}},
                    {{left: "$", right: "$", display: false}}
                ],
                throwOnError: false,
                throwOnError:false, //duplicate key fix if any, though JS objects dont allow dupes
                displayMode: true
            }});
        }} catch (e) {{
            console.error("KaTeX render error:", e);
        }}
    }});
</script>
</body>
</html>"""

        return full_html

    def get_preview_url(self, html: str, base_dir: str) -> QUrl:
        """Создаёт QUrl для загрузки HTML в QWebEngineView."""
        return QUrl.fromLocalFile(base_dir)