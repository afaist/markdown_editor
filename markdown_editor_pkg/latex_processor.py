"""Обработка LaTeX-формул в Markdown-тексте."""

import re


class LaTeXProcessor:
    """Извлекает LaTeX-формулы из текста и заменяет их на плейсхолдеры."""

    def __init__(self):
        self.display_math_cache: list[str] = []
        self.inline_math_cache: list[str] = []

    def reset(self) -> None:
        """Очистить кэш формул."""
        self.display_math_cache = []
        self.inline_math_cache = []

    def process(self, text: str) -> str:
        """
        Заменяет $$...$$ и $...$ на плейсхолдеры, сохраняя формулы в кэше.
        """
        self.reset()

        def store_display(match: re.Match) -> str:
            formula = match.group(1)
            placeholder = f"<!-- display-math-{len(self.display_math_cache)} -->"
            self.display_math_cache.append(formula)
            return placeholder

        def store_inline(match: re.Match) -> str:
            formula = match.group(1)
            placeholder = f"<!-- inline-math-{len(self.inline_math_cache)} -->"
            self.inline_math_cache.append(formula)
            return placeholder

        # Сначала блочные формулы $$...$$
        result = re.sub(r"\$\$(.+?)\$\$", store_display, text, flags=re.DOTALL)
        # Затем встроенные $...$
        result = re.sub(r"(?<!\$)\$(.+?)\$(?!\$)", store_inline, result)

        return result

    def restore_display(self, html: str) -> str:
        """Восстанавливает блочные формулы из плейсхолдеров в HTML."""
        def restore(match: re.Match) -> str:
            idx = int(match.group(1))
            if idx < len(self.display_math_cache):
                return f"$${self.display_math_cache[idx]}$$"
            return match.group(0)
        html = re.sub(r"<!--\s*display-math-(\d+)\s*-->", restore, html)
        html = re.sub(r"&lt;!--\s*display-math-(\d+)\s*--&gt;", restore, html)
        return html

    def restore_inline(self, html: str) -> str:
        """Восстанавливает встроенные формулы из плейсхолдеров в HTML."""
        def restore(match: re.Match) -> str:
            idx = int(match.group(1))
            if idx < len(self.inline_math_cache):
                return f"${self.inline_math_cache[idx]}$"
            return match.group(0)
        html = re.sub(r"<!--\s*inline-math-(\d+)\s*-->", restore, html)
        html = re.sub(r"&lt;!--\s*inline-math-(\d+)\s*--&gt;", restore, html)
        return html


class StrikethroughProcessor:
    """Безопасно заменяет ~~text~~ на <del>text</del>, не затрагивая блоки кода."""

    CODE_PATTERN = re.compile(r'(<pre>.*?</pre>|<code>.*?</code>)', re.DOTALL)
    STRIKE_PATTERN = re.compile(r'~~(.+?)~~')

    def apply(self, html: str) -> str:
        """Применяет зачёркивание, защищая содержимое блоков кода."""
        code_blocks: list[str] = []

        def save_code(match: re.Match) -> str:
            code_blocks.append(match.group(0))
            return f"\x00CODE_BLOCK_{len(code_blocks) - 1}\x00"

        processed = self.CODE_PATTERN.sub(save_code, html)
        processed = self.STRIKE_PATTERN.sub(r'<del>\1</del>', processed)

        def restore_code(match: re.Match) -> str:
            idx = int(match.group(1))
            return code_blocks[idx]

        restore_pattern = re.compile(r'\x00CODE_BLOCK_(\d+)\x00')
        return restore_pattern.sub(restore_code, processed)
