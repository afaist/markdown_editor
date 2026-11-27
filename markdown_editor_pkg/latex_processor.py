"""Обработка LaTeX-формул в Markdown-тексте."""

import html
import logging
import os
import re

logger = logging.getLogger(__name__)

LOG_FILE = os.path.join(os.path.expanduser("~"), "latex_debug.log")

# Unicode → LaTeX-команды для математических символов
UNICODE_TO_LATEX: dict[str, str] = {
    "\u2260": r"\neq",  # ≠
    "\u2264": r"\leq",  # ≤
    "\u2265": r"\geq",  # ≥
    "\u2248": r"\approx",  # ≈
    "\u221e": r"\infty",  # ∞
    "\u00d7": r"\times",  # ×
    "\u00f7": r"\div",  # ÷
    "\u2212": r"-",  # − (minus, не дефис)
    "\u2208": r"\in",  # ∈
    "\u2209": r"\notin",  # ∉
    "\u2282": r"\subset",  # ⊂
    "\u2283": r"\supset",  # ⊃
    "\u222a": r"\cup",  # ∪
    "\u222b": r"\int",  # ∫
    "\u222f": r"\oint",  # ∮
    "\u2211": r"\sum",  # ∑
    "\u2210": r"\prod",  # ∏
    "\u03b1": r"\alpha",  # α
    "\u03b2": r"\beta",  # β
    "\u03b3": r"\gamma",  # γ
    "\u03b4": r"\delta",  # δ
    "\u03b5": r"\varepsilon",  # ε
    "\u03b8": r"\theta",  # θ
    "\u03bb": r"\lambda",  # λ
    "\u03bc": r"\mu",  # μ
    "\u03c0": r"\pi",  # π
    "\u03c1": r"\rho",  # ρ
    "\u03c3": r"\sigma",  # σ
    "\u03c6": r"\phi",  # φ
    "\u03c9": r"\omega",  # ω
    "\u0393": r"\Gamma",  # Γ
    "\u0394": r"\Delta",  # Δ
    "\u0398": r"\Theta",  # Θ
    "\u039b": r"\Lambda",  # Λ
    "\u03a0": r"\Pi",  # Π
    "\u03a3": r"\Sigma",  # Σ
    "\u03a6": r"\Phi",  # Φ
    "\u03a9": r"\Omega",  # Ω
    "\u2192": r"\rightarrow",  # →
    "\u2190": r"\leftarrow",  # ←
    "\u21d2": r"\Rightarrow",  # ⇒
    "\u21d0": r"\Leftarrow",  # ⇐
    "\u2261": r"\equiv",  # ≡
    "\u2267": r"\leqq",  # ≦
    "\u2268": r"\geqq",  # ≧
    "\u2245": r"\cong",  # ≅
    "\u223c": r"\sim",  # ∼
    "\u2234": r"\therefore",  # ∴
    "\u2200": r"\forall",  # ∀
    "\u2203": r"\exists",  # ∃
    "\u2205": r"\emptyset",  # ∅
    "\u2207": r"\nabla",  # ∇
    "\u25b3": r"\triangle",  # △
    "\u25cb": r"\circ",  # ○
    "\u00b2": r"^2",  # ²
    "\u00b3": r"^3",  # ³
    "\u2070": r"^0",  # ⁰
    "\u2074": r"^4",  # ⁴
    "\u2075": r"^5",  # ⁵
    "\u2076": r"^6",  # ⁶
    "\u2077": r"^7",  # ⁷
    "\u2078": r"^8",  # ⁸
    "\u2079": r"^9",  # ⁹
}


def _unicode_to_latex(text: str) -> str:
    """Преобразует Unicode-математические символы в LaTeX-команды."""
    result = []
    for ch in text:
        if ch in UNICODE_TO_LATEX:
            result.append(UNICODE_TO_LATEX[ch])
        else:
            result.append(ch)
    return "".join(result)


class LaTeXProcessor:
    """Извлекает LaTeX-формлы из текста и заменяет их на плейсхолдеры.

    Поддерживает блочные ($$...$$) и встроенные ($...$) формулы.
    Преобразует Unicode-символы в LaTeX-команды и восстанавливает
    формулы после обработки Markdown.
    """

    def __init__(self) -> None:
        """Инициализация процессора LaTeX-формул."""
        self.display_math_cache: list[str] = []
        self.inline_math_cache: list[str] = []

    def reset(self) -> None:
        """Очистить кэш формул."""
        self.display_math_cache = []
        self.inline_math_cache = []

    def _log(self, msg: str) -> None:
        """Записать сообщение в лог-файл."""
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except Exception:
            pass

    def process(self, text: str) -> str:
        """Заменить LaTeX-формлы на плейсхолдеры, сохранив формулы в кэше.

        Сначала обрабатывает блочные формулы $$...$$, затем встроенные $...$.
        Преобразует Unicode-символы в LaTeX-команды.

        Args:
            text: Исходный Markdown-текст.

        Returns:
            Текст с плейсхолдерами вместо формул.
        """
        self.reset()
        self._log("=== LaTeXProcessor.process START ===")
        self._log(f"Input text (first 500 chars): {text[:500]}")

        def store_display(match: re.Match) -> str:
            formula = match.group(1)
            # Конвертируем Unicode в LaTeX сразу при извлечении
            formula = _unicode_to_latex(formula)
            placeholder = f"<!-- display-math-{len(self.display_math_cache)} -->"
            self.display_math_cache.append(formula)
            self._log(f"  [display] matched: {formula[:100]} -> {placeholder}")
            return placeholder

        def store_inline(match: re.Match) -> str:
            formula = match.group(1)
            # Конвертируем Unicode в LaTeX сразу при извлечении
            formula = _unicode_to_latex(formula)
            placeholder = f"<!-- inline-math-{len(self.inline_math_cache)} -->"
            self.inline_math_cache.append(formula)
            self._log(f"  [inline] matched: {formula[:100]} -> {placeholder}")
            return placeholder

        # Сначала блочные формулы $$...$$
        result = re.sub(r"\$\$(.+?)\$\$", store_display, text, flags=re.DOTALL)
        self._log(f"After display Math: {len(self.display_math_cache)} formulas cached")

        # Затем встроенные $...$
        result = re.sub(r"(?<!\$)\$(.+?)\$(?!\$)", store_inline, result)
        self._log(f"After inline Math: {len(self.inline_math_cache)} formulas cached")
        self._log(f"Processed text (first 500 chars): {result[:500]}")
        self._log("=== LaTeXProcessor.process END ===\n")

        return result

    def restore_display(self, html_text: str) -> str:
        """Восстановить блочные формулы из плейсхолдеров в HTML.

        Args:
            html_text: HTML-текст с плейсхолдерами display-math-N.

        Returns:
            HTML с восстановленными $$...$$ формулами.
        """
        self._log("=== restore_display START ===")
        self._log(f"HTML text (first 500 chars): {html_text[:500]}")

        def restore(match: re.Match) -> str:
            idx = int(match.group(1))
            if idx < len(self.display_math_cache):
                # Декодируем HTML-сущности (markdown экранирует > и <)
                formula = html.unescape(self.display_math_cache[idx])
                result = f"$${formula}$$"
                self._log(f"  Restored display-math-{idx}: {formula[:100]} -> {result[:120]}")
                return result
            self._log(
                f"  display-math-{idx} index out of range (cache size: {len(self.display_math_cache)})"
            )
            return str(match.group(0))

        html_text = re.sub(r"<!--\s*display-math-(\d+)\s*-->", restore, html_text)
        html_text = re.sub(r"&lt;!--\s*display-math-(\d+)\s*--&gt;", restore, html_text)
        self._log("=== restore_display END ===\n")
        return html_text

    def restore_inline(self, html_text: str) -> str:
        """Восстановить встроенные формулы из плейсхолдеров в HTML.

        Args:
            html_text: HTML-текст с плейсхолдерами inline-math-N.

        Returns:
            HTML с восстановленными $...$ формулами.
        """
        self._log("=== restore_inline START ===")
        self._log(f"HTML text (first 500 chars): {html_text[:500]}")

        def restore(match: re.Match) -> str:
            idx = int(match.group(1))
            if idx < len(self.inline_math_cache):
                # Декодируем HTML-сущности (markdown экранирует > и <)
                formula = html.unescape(self.inline_math_cache[idx])
                result = f"${formula}$"
                self._log(f"  Restored inline-math-{idx}: {formula[:100]} -> {result[:120]}")
                return result
            self._log(
                f"  inline-math-{idx} index out of range (cache size: {len(self.inline_math_cache)})"
            )
            return str(match.group(0))

        html_text = re.sub(r"<!--\s*inline-math-(\d+)\s*-->", restore, html_text)
        html_text = re.sub(r"&lt;!--\s*inline-math-(\d+)\s*--&gt;", restore, html_text)
        self._log("=== restore_inline END ===\n")
        return str(html_text)


class StrikethroughProcessor:
    """Безопасно заменяет ~~text~~ на <del>text</del>, не затрагивая блоки кода."""

    CODE_PATTERN = re.compile(r"(<pre>[\s\S]*?</pre>|<code>[\s\S]*?</code>)", re.DOTALL)
    STRIKE_PATTERN = re.compile(r"~~(.+?)~~")

    def apply(self, html: str) -> str:
        """Применить зачёркивание, защищая содержимое блоков кода.

        Args:
            html: HTML-текст для обработки.

        Returns:
            HTML с заменёнными ~~text~~ на <del>text</del>.
        """
        code_blocks: list[str] = []

        def save_code(match: re.Match) -> str:
            code_blocks.append(match.group(0))
            return f"\x00CODE_BLOCK_{len(code_blocks) - 1}\x00"

        processed = self.CODE_PATTERN.sub(save_code, html)
        processed = self.STRIKE_PATTERN.sub(r"<del>\1</del>", processed)

        def restore_code(match: re.Match) -> str:
            idx = int(match.group(1))
            return code_blocks[idx]

        restore_pattern = re.compile(r"\x00CODE_BLOCK_(\d+)\x00")
        return restore_pattern.sub(restore_code, processed)
