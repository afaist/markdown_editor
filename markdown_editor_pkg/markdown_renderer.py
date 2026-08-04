"""Рендеринг Markdown в HTML с поддержкой LaTeX, тем и GitHub Callouts."""

import os
import markdown
from PyQt6.QtCore import QUrl

from markdown_editor_pkg.latex_processor import LaTeXProcessor, StrikethroughProcessor
from markdown_editor_pkg.callout_processor import CalloutProcessor
from markdown_editor_pkg.themes import ThemesManager
from markdown_editor_pkg.prism_processor import PrismJSProcessor


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

                /* Колонтитулы — видны при печати */
                .page-header {{
                    display: block !important;
                }}
                .page-footer {{
                    display: block !important;
                }}
                body {{
                    padding-top: 1.5cm;
                    padding-bottom: 1.5cm;
                }}
            }}

            /* Колонтитулы - скрыты на экране, фиксированные при печати */
            .page-header {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                padding: 1.2cm 2.5cm 0.5cm 2.5cm;
                text-align: center;
                font-size: 9px;
                color: #888;
                border-bottom: 1px solid #ddd;
                z-index: 1000;
            }}
            .page-footer {{
                display: none;
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                padding: 0.5cm 2.5cm 1.2cm 2.5cm;
                text-align: center;
                font-size: 9px;
                color: #888;
                border-top: 1px solid #ddd;
                z-index: 1000;
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
        self.prism_processor = PrismJSProcessor()

    def render(self, text: str, theme_name: str = "light", base_dir: str = "", headers: dict = None) -> str:
        """
        Рендерит Markdown в полный HTML-документ.

        Args:
            text: Markdown-текст.
            theme_name: Имя темы ("light", "dark", "contrast").
            base_dir: Директория для относительных путей к ресурсам.
            headers: Словарь с настройками колонтитулов.
        """
        # 1. Извлекаем LaTeX-формулы
        self.latex_processor.reset()
        processed_text = self.latex_processor.process(text)

        # 2. Конвертируем Markdown → HTML (codehilite удалён, используется Prism.js)
        md = markdown.Markdown(
            extensions=[
                "markdown.extensions.fenced_code",
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

        # Формируем колонтитулы
        show_headers = headers.get("show_headers", False) if headers else False
        header_text = headers.get("header_text", "") if headers else ""
        footer_text = headers.get("footer_text", "") if headers else ""

        header_html = ""
        footer_html = ""
        if show_headers:
            header_html = f'<div class="page-header">{header_text}</div>\n'
            footer_html = f'<div class="page-footer">{footer_text}</div>\n'

        # JS для замены placeholder {page} на реальное число страниц
        page_count_js = ""
        if show_headers and "{page}" in footer_text:
            page_count_js = f"""
    document.addEventListener("DOMContentLoaded", function() {{
        // Оценка числа страниц: делим высоту контента на высоту видимой области
        const contentHeight = document.body.scrollHeight;
        const viewHeight = window.innerHeight || document.documentElement.clientHeight;
        const pageCount = Math.max(1, Math.ceil(contentHeight / viewHeight));
    
        const footer = document.querySelector('.page-footer');
        if (footer) {{
            footer.textContent = footer.textContent.replace('{{page}}', String(pageCount));
        }}
    }});"""
    
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Preview — {theme_name}</title>
    <link rel="stylesheet" href="file://{katex_css}">
    {print_styles}
</head>
<body>
{header_html}
{html_content}
{footer_html}

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
            container.innerHTML = container.innerHTML.replace(/[\\u200B-\\u200D\\uFEFF]/g, '');
        }}

        cleanMathElements();

        try {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: "$$", right: "$$", display: true}},
                    {{left: "$", right: "$", display: false}}
                ],
                throwOnError: false,
                displayMode: true
            }});
        }} catch (e) {{
            console.error("KaTeX render error:", e);
        }}
    }});
</script>
{page_count_js}
</body>
</html>"""

        # 7. Встраиваем Prism.js
        full_html = self.prism_processor.inject_prism(full_html, theme_name, base_dir)

        return full_html

    def get_preview_url(self, html: str, base_dir: str) -> QUrl:
        """Создаёт QUrl для загрузки HTML в QWebEngineView."""
        return QUrl.fromLocalFile(base_dir)
