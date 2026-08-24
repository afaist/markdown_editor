# markdown_editor_pkg/markdown_renderer.py
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
                break-inside: avoid;
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

            /* Общие стили для колонтитулов (скрыты на экране) */
            .page-header {{
                display: none;
            }}
            .page-footer {{
                display: none;
            }}

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
                table, img, pre, .callout {{
                    page-break-inside: avoid;
                }}
                body {{
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}

                @page {{
                    margin: 2cm;
                }}

                /* Показываем колонтитулы только при печати */
                .page-header {{
                    display: block !important;
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    padding: 1cm;
                    text-align: center;
                    font-size: 9px;
                    color: #888;
                    border-bottom: 1px solid #ddd;
                    background: white;
                    z-index: 1000;
                }}
                .page-footer {{
                    display: block !important;
                    position: fixed;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    padding: 1cm;
                    text-align: center;
                    font-size: 9px;
                    color: #888;
                    border-top: 1px solid #ddd;
                    background: white;
                    z-index: 1000;
                }}

                /* Настройка отступов тела документа */
                body {{
                    padding-top: 1.5cm;
                    padding-bottom: 1.5cm;
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
        self.prism_processor = PrismJSProcessor()

    def render(
        self,
        text: str,
        theme_name: str = "light",
        base_dir: str = "",
        headers: dict | None = None,
    ) -> str:
        """
        Рендерит Markdown в полный HTML-документ.
        """
        # 1. Извлекаем LaTeX-формулы
        self.latex_processor.reset()
        processed_text = self.latex_processor.process(text)

        # 2. Конвертируем Markdown → HTML
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

        katex_css = (
            os.path.join(base_dir, self.KATEX_CSS) if base_dir else self.KATEX_CSS
        )
        katex_js = os.path.join(base_dir, self.KATEX_JS) if base_dir else self.KATEX_JS
        auto_render_js = (
            os.path.join(base_dir, self.KATEX_AUTO_RENDER_JS)
            if base_dir
            else self.KATEX_AUTO_RENDER_JS
        )

        # Формируем колонтитулы
        show_headers = headers.get("show_headers", False) if headers else False
        header_text = headers.get("header_text", "") if headers else ""
        footer_text = headers.get("footer_text", "") if headers else ""

        header_html = ""
        footer_html = ""
        if show_headers:
            # {PAGE_NUM} — placeholder, который JS заменит на реальный номер страницы
            resolved_footer = footer_text.replace("{page}", "{PAGE_NUM}")
            header_html = f'<div class="page-header">{header_text}</div>\n'
            footer_html = f'<div class="page-footer">{resolved_footer}</div>\n'

        # JavaScript для KaTeX + нумерации страниц
        katex_js_code = f"""
<script src="file://{katex_js}"></script>
<script src="file://{auto_render_js}"></script>
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        if (typeof renderMathInElement === 'undefined') {{
            console.error("KaTeX auto-render not loaded");
            return;
        }}
        const container = document.body;
        function cleanMathElements() {{
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

        // === Нумерация страниц для PDF-экорта ===
        // Разбиваем body на страницы, подставляя номера
        function addPageNumbers() {{
            var footers = document.querySelectorAll('.page-footer');
            if (footers.length === 0) return;

            var originalFooter = footers[0];
            var footerTemplate = originalFooter.outerHTML;

            // Создаём контейнер-обёртку для контента
            var content = document.body.innerHTML;

            // Удаляем header/footer из body
            var cleanContent = content
                .replace(/<div class="page-header"[^>]*>.*?<\\/div>/gi, '')
                .replace(/<div class="page-footer"[^>]*>.*?<\\/div>/gi, '');

            // Шаг 1: Вычисляем количество страниц через скрытую превью-раскладку
            var preview = document.createElement('div');
            preview.style.cssText = 'position:absolute;visibility:hidden;top:-9999px;left:-9999px;'
                + 'width:1920px;padding:2cm;';
            preview.innerHTML = cleanContent;
            document.body.appendChild(preview);

            // Ждём загрузки шрифтов/KaTeX
            setTimeout(function() {{
                var previewHeight = preview.scrollHeight;
                var pageHeight = preview.clientHeight;
                document.body.removeChild(preview);

                if (pageHeight <= 0) pageHeight = 1056; // ~29.7cm at 96dpi

                var totalPages = Math.ceil(previewHeight / pageHeight);
                if (totalPages < 1) totalPages = 1;

                // Шаг 2: Генерируем HTML с разбивкой по страницам
                var pages = [];
                var chars = cleanContent;
                var pagePositions = [];

                // Создаём временный измеритель
                var measurer = document.createElement('div');
                measurer.style.cssText = 'position:absolute;visibility:hidden;top:-9999px;left:-9999px;'
                    + 'width:1920px;padding:2cm;overflow:hidden;';
                document.body.appendChild(measurer);

                // Используем бинарный поиск по char positions
                var contentLen = chars.length;
                var pos = 0;

                for (var p = 0; p < totalPages; p++) {{
                    var pageContent = '';
                    var startIdx = pos;

                    // Ищем позицию разрыва страницы
                    var lo = pos;
                    var hi = Math.min(contentLen, pos + Math.floor((contentLen - pos) * 0.5) + 100);
                    if (hi > contentLen) hi = contentLen;
                    if (lo >= hi) {{
                        pageContent = chars.substring(pos, hi);
                        pos = hi;
                    }} else {{
                        // Бинарный поиск точки разрыва
                        while (lo < hi - 1) {{
                            var mid = Math.floor((lo + hi) / 2);
                            measurer.innerHTML = chars.substring(startIdx, mid);
                            if (measurer.scrollHeight > pageHeight) {{
                                hi = mid;
                            }} else {{
                                lo = mid;
                            }}
                        }}

                        // Ищем разрыв слова после lo
                        var breakPos = lo;
                        var rest = chars.substring(startIdx, lo);
                        var lastSpace = rest.lastIndexOf(' ');
                        var lastBreak = rest.lastIndexOf('</p>');
                        var lastBreak2 = rest.lastIndexOf('</div>');
                        var lastBreak3 = rest.lastIndexOf('</table>');

                        var bestBreak = lastSpace;
                        if (lastBreak > bestBreak) bestBreak = lastBreak;
                        if (lastBreak2 > bestBreak) bestBreak = lastBreak2;
                        if (lastBreak3 > bestBreak) bestBreak = lastBreak3;

                        if (bestBreak > 0) {{
                            breakPos = startIdx + bestBreak;
                        }} else {{
                            breakPos = startIdx + Math.min(lo, contentLen - startIdx);
                        }}

                        pageContent = chars.substring(startIdx, breakPos);
                        pos = breakPos;
                    }}

                    pages.push(pageContent);
                }}

                // Если что-то осталось
                if (pos < contentLen) {{
                    pages.push(chars.substring(pos));
                    totalPages = pages.length;
                }}

                document.body.removeChild(measurer);

                // Шаг 3: Заменяем body на страницы
                var newBody = document.createElement('div');
                newBody.style.cssText = 'width:100%;';

                for (var i = 0; i < pages.length; i++) {{
                    var pageNum = i + 1;
                    var pageDiv = document.createElement('div');
                    pageDiv.className = 'print-page';
                    pageDiv.style.cssText = 'page-break-after: always; position: relative; min-height: 1056px;';
                    if (i === pages.length - 1) {{
                        pageDiv.style.pageBreakAfter = 'avoid;';
                    }}

                    pageDiv.innerHTML = pages[i];

                    // Клонируем footer и подставляем номер
                    var footerClone = document.createElement('div');
                    footerClone.className = 'page-footer';
                    footerClone.style.cssText = originalFooter.style.cssText || '';
                    // Вставляем номер страницы
                    var resolved = footerTemplate.replace('{{PAGE_NUM}}', pageNum + '/' + pages.length);
                    footerClone.outerHTML = resolved;

                    // Вставляем footer через innerHTML после создания pageDiv
                    var temp = document.createElement('div');
                    temp.innerHTML = resolved;
                    var footerEl = temp.firstChild;
                    pageDiv.appendChild(footerEl);

                    newBody.appendChild(pageDiv);
                }}

                document.body.innerHTML = '';
                document.body.appendChild(newBody);

                // Повторный рендер KaTeX (разбивка могла повлиять)
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
                    console.error("KaTeX re-render error:", e);
                }}

            }}, 800); // Ждём KaTeX
        }}

        addPageNumbers();
    }});
</script>
"""

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
{katex_js_code}
</body>
</html>"""

        # 7. Встраиваем Prism.js
        full_html = self.prism_processor.inject_prism(full_html, theme_name, base_dir)

        return full_html

    def get_preview_url(self, html: str, base_dir: str) -> QUrl:
        """Создаёт QUrl для загрузки HTML в QWebEngineView."""
        return QUrl.fromLocalFile(base_dir)
