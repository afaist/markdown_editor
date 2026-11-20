"""Валидация Markdown-синтаксиса.

Проверяет текст на распространённые ошибки разметки:
- незакрытые теги **/_, ~~/, `
- незакрытые блоки ```
- пустые ссылки и изображения
- несовпадающие маркеры списков
- незакрытые <br> и <hr>
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from markdown_editor_pkg.i18n import tr


@dataclass
class MarkdownIssue:
    """Одна проблема в Markdown-тексте."""

    severity: Literal["error", "warning", "info"]
    message: str
    line: int = 0
    char: int = 0


@dataclass
class ValidationReport:
    """Результат валидации Markdown."""

    issues: list[MarkdownIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True если нет ошибок (severity == 'error")."""
        return not any(i.severity == "error" for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "info")

    @property
    def summary(self) -> str:
        parts: list[str] = []
        if self.error_count:
            parts.append(f"{tr('Errors')}: {self.error_count}")
        if self.warning_count:
            parts.append(f"{tr('Warnings')}: {self.warning_count}")
        if self.info_count:
            parts.append(f"{tr('Info')}: {self.info_count}")
        if not parts:
            return tr("No issues found")
        return ", ".join(parts)

    @property
    def details_text(self) -> str:
        """Форматирует все проблемы в многострочный текст для отображения."""
        if not self.issues:
            return tr("No issues found.")

        lines: list[str] = []
        severity_icon: dict[str, str] = {
            "error": "✕",
            "warning": "⚠",
            "info": "ℹ",
        }
        severity_label: dict[str, str] = {
            "error": tr("Error"),
            "warning": tr("Warning"),
            "info": tr("Info"),
        }

        for issue in self.issues:
            icon = severity_icon.get(issue.severity, "?")
            label = severity_label.get(issue.severity, issue.severity)
            location = ""
            if issue.line > 0:
                location = f" {tr('line')}: {issue.line}"
                if issue.char > 0:
                    location += f", {tr('char')}: {issue.char}"
            lines.append(f"  {icon} [{label}]{location}  {issue.message}")

        return "\n".join(lines)


class MarkdownValidator:
    """Валидатор Markdown-синтаксиса."""

    def validate(self, text: str) -> ValidationReport:
        """Валидирует Markdown-текст и возвращает отчёт.

        Args:
            text: Markdown-текст для проверки.

        Returns:
            ValidationReport с найденными проблемами.
        """
        report = ValidationReport()
        lines = text.splitlines()

        self._check_unclosed_code_blocks(text, lines, report)
        self._check_unclosed_inline_formatting(lines, report)
        self._check_empty_links_and_images(lines, report)
        self._check_unclosed_links(lines, report)
        self._check_list_consistency(lines, report)
        self._check_trailing_whitespace(lines, report)
        self._check_multiple_blank_lines(lines, report)
        self._check_html_tags(lines, report)

        return report

    # ─── Проверки ───────────────────────────────────────────────────────

    def _check_unclosed_code_blocks(
        self, text: str, lines: list[str], report: ValidationReport
    ) -> None:
        """Проверка незакрытых блоков кода ```."""
        in_code_block = False
        code_fence_line = 0

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_fence_line = i
                else:
                    in_code_block = False

        if in_code_block:
            report.issues.append(
                MarkdownIssue(
                    severity="error",
                    message=tr("Unclosed code block starting at line {num}").format(
                        num=code_fence_line
                    ),
                    line=code_fence_line,
                )
            )

    def _is_inside_latex_block(self, lines: list[str], line_index: int) -> bool:
        """Проверяет, находится ли строка внутри блочного LaTeX $$...$$.

        Args:
            lines: Список строк текста.
            line_index: Индекс проверяемой строки (0-based).

        Returns:
            True если строка внутри $$ блока и должна быть пропущена.
        """
        if line_index < 0 or line_index >= len(lines):
            return False

        in_latex = False
        for i in range(line_index + 1):
            stripped = lines[i].strip()
            if stripped == "$$":
                in_latex = not in_latex

        return in_latex

    def _check_unclosed_inline_formatting(self, lines: list[str], report: ValidationReport) -> None:
        """Проверка незакрытых inline-форматов: **_, __/, ~~/, `."""
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Пропускаем строки внутри блоков кода
            if self._is_inside_code_block(lines, i - 1):
                continue
            # Пропускаем строки внутри блочного LaTeX $$...$$
            if self._is_inside_latex_block(lines, i - 1):
                continue
            # Пропускаем строки, содержащие маркеры $$
            if "$$" in line:
                continue

            # Проверка одиночных `
            self._check_unmatched_backticks(line, i, report)
            # Проверка ** (bold)
            self._check_unmatched_markers(line, i, report, "**", "bold")
            # Проверка __ (bold alt)
            self._check_unmatched_markers(line, i, report, "__", "bold (__)")
            # Проверка ~~ (strikethrough)
            self._check_unmatched_markers(line, i, report, "~~", "strikethrough")
            # Проверка одиночных * (italic)
            self._check_unmatched_markers(line, i, report, "*", "italic (*)")
            # Проверка одиночных _ (italic alt)
            self._check_unmatched_markers(line, i, report, "_", "italic (_)")

    def _check_unmatched_backticks(
        self, line: str, line_num: int, report: ValidationReport
    ) -> None:
        """Проверка несовпадающих обратных кавычек."""
        # Пропускаем строки-ограничители блоков кода (``` или ~~~)
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            return

        # Убираем экранированные бэктки
        cleaned = line.replace("\\`", "")
        count = 0
        i = 0
        while i < len(cleaned):
            if cleaned[i] == "`":
                # Считаем количество подряд идущих бэктков
                while i < len(cleaned) and cleaned[i] == "`":
                    i += 1
                count += 1
            else:
                i += 1

        if count % 2 != 0:
            report.issues.append(
                MarkdownIssue(
                    severity="error",
                    message=tr("Odd number of backticks (")
                    + "`"
                    + tr(") at char {char}").format(char=i),
                    line=line_num,
                )
            )

    def _check_unmatched_markers(
        self, line: str, line_num: int, report: ValidationReport, marker: str, name: str
    ) -> None:
        """Проверка несовпадающих маркеров форматирования."""
        # Пропускаем строки, где маркер используется как часть HTML-тега
        if marker in ("<", ">"):
            return

        pattern = f"(?<!\\\\){re.escape(marker)}"
        matches = list(re.finditer(pattern, line))

        if len(matches) % 2 != 0:
            # Проверяем, что это не часть блока кода (например, ``` или ~~~)
            for m in matches:
                start = m.start()
                # Проверяем что это не часть тройного маркера
                prefix = line[:start]
                suffix = line[m.end() :]
                if marker == "**" and (prefix.endswith("*") or suffix.startswith("*")):
                    continue
                if marker == "~~" and (prefix.endswith("~") or suffix.startswith("~")):
                    continue

                report.issues.append(
                    MarkdownIssue(
                        severity="warning",
                        message=tr("Unclosed {name} marker").format(name=name),
                        line=line_num,
                        char=m.start(),
                    )
                )
                break  # Одна проблема на строку

    def _check_empty_links_and_images(self, lines: list[str], report: ValidationReport) -> None:
        """Проверка пустых ссылок и изображений: [](), ![]."""
        for i, line in enumerate(lines, start=1):
            # Пустые изображения: ![]()
            if re.search(r"!\[\]\(\)", line):
                report.issues.append(
                    MarkdownIssue(
                        severity="warning",
                        message=tr("Empty image placeholder"),
                        line=i,
                    )
                )
            # Пустые ссылки: []()
            if re.search(r"(?<!!)\[\]\(\)", line):
                report.issues.append(
                    MarkdownIssue(
                        severity="warning",
                        message=tr("Empty link"),
                        line=i,
                    )
                )
            # Ссылка без текста: [text]()
            if re.search(r"\[.+?\]\(\s*\)", line):
                report.issues.append(
                    MarkdownIssue(
                        severity="warning",
                        message=tr("Link without URL"),
                        line=i,
                    )
                )
            # Изображение без текста: ![alt]()
            if re.search(r"!\[.+?\]\(\s*\)", line):
                report.issues.append(
                    MarkdownIssue(
                        severity="warning",
                        message=tr("Image without URL"),
                        line=i,
                    )
                )

    def _check_unclosed_links(self, lines: list[str], report: ValidationReport) -> None:
        """Проверка незакрытых квадратных скобок ссылок."""
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped == "$$":
                continue
            if self._is_inside_code_block(lines, i - 1):
                continue
            if self._is_inside_latex_block(lines, i - 1):
                continue

            # Считаем [ и ] (без учёта ![])
            text_only = re.sub(r"!\[", "__IMG__", line)
            open_count = text_only.count("[")
            close_count = text_only.count("]")

            if open_count > close_count:
                report.issues.append(
                    MarkdownIssue(
                        severity="error",
                        message=tr("Unclosed link bracket [ at line {num}").format(num=i),
                        line=i,
                    )
                )

    def _check_list_consistency(self, lines: list[str], report: ValidationReport) -> None:
        """Проверка согласованности маркеров списков."""
        in_list = False
        list_marker: str | None = None
        list_indent = 0

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            # Проверка unordered list markers
            ul_match = re.match(r"^(\s*)([-*+])\s+(\S.*)?$", line)
            if ul_match:
                indent = len(ul_match.group(1))
                marker = ul_match.group(2)
                if in_list and indent == list_indent and marker != list_marker:
                    report.issues.append(
                        MarkdownIssue(
                            severity="info",
                            message=tr(
                                "Mixed list markers ({prev} and {curr}) at line {num}"
                            ).format(prev=list_marker, curr=marker, num=i),
                            line=i,
                        )
                    )
                in_list = True
                list_marker = marker
                list_indent = indent
                continue

            # Проверка ordered list markers
            ol_match = re.match(r"^(\s*)(\d+)\.\s+(\S.*)?$", line)
            if ol_match:
                in_list = False
                list_marker = None
                continue

            # Если строка не является элементом списка
            if not stripped.startswith(("#", "```", "---", "***", ">")):
                in_list = False
                list_marker = None

    def _check_trailing_whitespace(self, lines: list[str], report: ValidationReport) -> None:
        """Проверка завершающих пробелов (не ошибка, но info)."""
        count = 0
        for line in lines:
            if line != line.rstrip() and line.strip():
                count += 1
        if count > 0:
            report.issues.append(
                MarkdownIssue(
                    severity="info",
                    message=tr("{count} line(s) with trailing whitespace").format(count=count),
                )
            )

    def _check_multiple_blank_lines(self, lines: list[str], report: ValidationReport) -> None:
        """Проверка множественных пустых строк."""
        consecutive = 0
        max_blank = 0
        blank_start = 0

        for i, line in enumerate(lines, start=1):
            if not line.strip():
                if consecutive == 0:
                    blank_start = i
                consecutive += 1
                max_blank = max(max_blank, consecutive)
            else:
                consecutive = 0

        if max_blank >= 3:
            report.issues.append(
                MarkdownIssue(
                    severity="info",
                    message=tr("{count} consecutive blank lines").format(count=max_blank),
                    line=blank_start,
                )
            )

    def _check_html_tags(self, lines: list[str], report: ValidationReport) -> None:
        """Проверка незакрытых HTML-тегов."""
        open_tags: list[tuple[str, int]] = []
        void_elements = {
            "br",
            "hr",
            "img",
            "input",
            "meta",
            "link",
            "area",
            "base",
            "col",
            "embed",
            "source",
            "track",
            "wbr",
        }

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped == "$$":
                continue
            if self._is_inside_code_block(lines, i - 1):
                continue
            if self._is_inside_latex_block(lines, i - 1):
                continue

            # Находим HTML-теги
            for match in re.finditer(r"<(/?)(\w+)([^>]*)/?>", line):
                is_closing = bool(match.group(1))
                tag_name = match.group(2).lower()

                if tag_name in void_elements:
                    continue

                if is_closing:
                    # Ищем соответствующий открытый тег
                    for j in range(len(open_tags) - 1, -1, -1):
                        if open_tags[j][0] == tag_name:
                            open_tags.pop(j)
                            break
                else:
                    open_tags.append((tag_name, i))

        for tag_name, line_num in open_tags[-3:]:  # Показываем последние 3
            report.issues.append(
                MarkdownIssue(
                    severity="warning",
                    message=tr("Unclosed HTML tag <{tag}> at line {num}").format(
                        tag=tag_name, num=line_num
                    ),
                    line=line_num,
                )
            )

    # ─── Утилиты ────────────────────────────────────────────────────────

    @staticmethod
    def _is_inside_code_block(lines: list[str], line_index: int) -> bool:
        """Проверяет, находится ли строка внутри блока кода ```."""
        if line_index < 0 or line_index >= len(lines):
            return False

        in_code = False
        for i in range(line_index):
            stripped = lines[i].strip()
            if stripped.startswith("```"):
                in_code = not in_code
        return in_code
