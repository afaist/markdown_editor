"""GitHub Callouts — парсинг blockquote с маркировкой [!TYPE]."""

from __future__ import annotations

import re
from typing import ClassVar


class CalloutProcessor:
    """
    Преобразует blockquote с [!NOTE], [!TIP], [!IMPORTANT], [!WARNING], [!CAUTION]
    в отдельные <div class="callout callout-...">.
    """

    # Типы callout
    CALLOUT_TYPES: ClassVar[set[str]] = {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}

    BLOCKQUOTE_PATTERN = re.compile(
        r"<blockquote>(.*?)</blockquote>",
        flags=re.DOTALL | re.IGNORECASE,
    )

    PARAGRAPH_PATTERN = re.compile(
        r"<p>(.*?)</p>",
        flags=re.DOTALL | re.IGNORECASE,
    )

    TYPE_PATTERN = re.compile(
        r"\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]",
        flags=re.IGNORECASE,
    )

    def process(self, html: str) -> str:
        """Заменить blockquote с callout-маркерами на стилизованные div'ы.

        Преобразует <blockquote> с [!NOTE], [!TIP], [!IMPORTANT], [!WARNING],
        [!CAUTION] в <div class="callout callout-{type}">.

        Args:
            html: HTML-текст с blockquote.

        Returns:
            HTML с заменёнными blockquote на callout div'ы.
        """
        return self.BLOCKQUOTE_PATTERN.sub(self._process_blockquote, html)

    def _process_blockquote(self, match: re.Match) -> str:
        blockquote_content = match.group(1)
        paragraphs = self.PARAGRAPH_PATTERN.findall(blockquote_content)

        if not paragraphs:
            return str(match.group(0))

        callouts_html: list[str] = []
        current_type: str | None = None
        current_paragraphs: list[str] = []

        def flush() -> None:
            nonlocal current_type, current_paragraphs
            if current_type and current_paragraphs:
                content = "\n".join(current_paragraphs)
                callouts_html.append(
                    f'<div class="callout callout-{current_type}">\n{content}\n</div>'
                )
            current_type = None
            current_paragraphs = []

        for p in paragraphs:
            type_match = self.TYPE_PATTERN.match(p)
            if type_match:
                flush()
                current_type = type_match.group(1).lower()
                body_text = p[type_match.end() :].strip()
                if body_text:
                    current_paragraphs.append(body_text)
            else:
                if current_type:
                    current_paragraphs.append(p)

        flush()

        if callouts_html:
            return "\n".join(callouts_html)
        return str(match.group(0))
