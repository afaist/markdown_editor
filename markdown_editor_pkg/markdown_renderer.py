"""Рендеринг Markdown в HTML с поддержкой LaTeX, тем и GitHub Callouts."""

from __future__ import annotations

import importlib.resources
import os

import markdown

from markdown_editor_pkg.callout_processor import CalloutProcessor
from markdown_editor_pkg.latex_processor import LaTeXProcessor, StrikethroughProcessor
from markdown_editor_pkg.prism_processor import PrismJSProcessor
from markdown_editor_pkg.themes import ThemesManager

# ─── Шаблоны из файлов ────────────────────────────────────────────────────


def _read_template(filename: str) -> str:
    """Read a template file from the templates package."""
    try:
        with (
            importlib.resources.files("markdown_editor_pkg.templates")
            .joinpath(filename)
            .open(encoding="utf-8") as f
        ):
            return f.read()
    except FileNotFoundError:
        return ""


_PRINT_STYLES_TEMPLATE: str = ""
_KATEX_SETUP_JS: str = ""
_PAGE_NUMBERING_JS: str = ""

try:
    _PRINT_STYLES_TEMPLATE = _read_template("print_styles.css")
    _KATEX_SETUP_JS = _read_template("katex_setup.js")
    _PAGE_NUMBERING_JS = _read_template("page_numbering.js")
except Exception:
    pass


class MarkdownRenderer:
    """Конвертирует Markdown-текст в полный HTML-документ с LaTeX и темами."""

    # Шаблоны путей к KaTeX
    KATEX_CSS = "katex/katex.min.css"
    KATEX_JS = "katex/katex.min.js"
    KATEX_AUTO_RENDER_JS = "katex/auto-render.min.js"

    def __init__(self, themes: ThemesManager):
        """Инициализация рендерера Markdown.

        Args:
            themes: Экземпляр ThemesManager для управления темами.
        """
        self.themes = themes
        self.latex_processor = LaTeXProcessor()
        self.strikethrough_processor = StrikethroughProcessor()
        self.callout_processor = CalloutProcessor()
        self.prism_processor = PrismJSProcessor()

    # ─── Публичный API ─────────────────────────────────────────────────

    def render(
        self,
        text: str,
        theme_name: str = "light",
        base_dir: str = "",
        headers: dict | None = None,
    ) -> str:
        """Рендерит Markdown в полный HTML-документ."""
        # Pipeline: Markdown → HTML
        processed_text = self._extract_latex(text)
        html_content = self._markdown_to_html(processed_text)
        html_content = self._restore_latex(html_content)
        html_content = self._apply_strikethrough(html_content)
        html_content = self._apply_callouts(html_content)

        # Сборка полного HTML-документа
        theme_css = self.themes.get_preview_css()
        print_styles = _PRINT_STYLES_TEMPLATE.format(theme_css=theme_css)

        katex_css = self._resolve_path(base_dir, self.KATEX_CSS)
        katex_js = self._resolve_path(base_dir, self.KATEX_JS)
        auto_render_js = self._resolve_path(base_dir, self.KATEX_AUTO_RENDER_JS)

        show_headers, header_text, footer_text = self._parse_headers(headers)
        header_html, footer_html = self._build_header_footer(show_headers, header_text, footer_text)

        katex_js_code = _KATEX_SETUP_JS.format(katex_js=katex_js, auto_render_js=auto_render_js)
        page_numbering_js = self._build_page_numbering_js(show_headers)

        full_html = self._build_html_document(
            html_content,
            theme_name,
            print_styles,
            katex_css,
            header_html,
            footer_html,
            katex_js_code,
            page_numbering_js,
        )

        # Встраиваем Prism.js
        full_html = self.prism_processor.inject_prism(full_html, theme_name, base_dir)

        return full_html

    # ─── Pipeline stages ────────────────────────────────────────────────

    def _extract_latex(self, text: str) -> str:
        """Stage 1: Извлекаем LaTeX-формулы, заменяем плейсхолдерами."""
        self.latex_processor.reset()
        return self.latex_processor.process(text)

    def _markdown_to_html(self, text: str) -> str:
        """Stage 2: Конвертируем Markdown → HTML."""
        md = markdown.Markdown(
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.tables",
                "markdown.extensions.toc",
            ]
        )
        return str(md.convert(text))

    def _restore_latex(self, html: str) -> str:
        """Stage 3: Восстанавливаем LaTeX-формулы из плейсхолдеров."""
        html = self.latex_processor.restore_display(html)
        return self.latex_processor.restore_inline(html)

    def _apply_strikethrough(self, html: str) -> str:
        """Stage 4: Применяем зачёркивание."""
        return self.strikethrough_processor.apply(html)

    def _apply_callouts(self, html: str) -> str:
        """Stage 5: Применяем GitHub Callouts."""
        return self.callout_processor.process(html)

    # ─── Сборка HTML ────────────────────────────────────────────────────

    @staticmethod
    def _resolve_path(base_dir: str, rel_path: str) -> str:
        """Резолвит относительный путь относительно base_dir."""
        if base_dir:
            return os.path.join(base_dir, rel_path)
        return rel_path

    @staticmethod
    def _parse_headers(headers: dict | None) -> tuple[bool, str, str]:
        """Парсит настройки колонтитулов."""
        if not headers:
            return False, "", ""
        return (
            headers.get("show_headers", False),
            headers.get("header_text", ""),
            headers.get("footer_text", ""),
        )

    @staticmethod
    def _build_header_footer(show: bool, header_text: str, footer_text: str) -> tuple[str, str]:
        """Создаёт HTML колонтитулов."""
        if not show:
            return "", ""
        resolved_footer = footer_text.replace("{page}", "{PAGE_NUM}")
        header_html = f'<div class="page-header">{header_text}</div>\n'
        footer_html = f'<div class="page-footer">{resolved_footer}</div>\n'
        return header_html, footer_html

    @staticmethod
    def _build_page_numbering_js(enabled: bool) -> str:
        """Создаёт JavaScript для нумерации страниц (только при включённых колонтитулах).

        Использует CSS @media print для разбивки — безопаснее и проще, чем
        JS-бинарный поиск, который может разорвать HTML-теги.
        """
        if not enabled:
            return ""

        return _PAGE_NUMBERING_JS

    def _build_html_document(
        self,
        html_content: str,
        theme_name: str,
        print_styles: str,
        katex_css: str,
        header_html: str,
        footer_html: str,
        katex_js_code: str,
        page_numbering_js: str,
    ) -> str:
        """Собирает полный HTML-документ."""
        return f"""<!DOCTYPE html>
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
{page_numbering_js}
</body>
</html>"""
