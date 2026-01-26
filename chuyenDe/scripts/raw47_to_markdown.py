#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from generate_from_raw47 import (
    BEFORE_AFTER_RE,
    LEVEL_RE,
    Paragraph,
    Section,
    extract_paragraphs,
    split_sections,
)


@dataclass(frozen=True)
class OutputPaths:
    out_md_dir: Path

    def md_path(self, *, skill: str, level: int, week: int) -> Path:
        return self.out_md_dir / skill / f"Level{level}" / f"W{week}.md"


def _normalize_text(s: str) -> str:
    s = s.replace("\xa0", " ").strip()
    s = re.sub(r"[ \t]+", " ", s)
    return s


def _md_span(text: str, cls: str) -> str:
    return f"[{text}]{{.{cls}}}"


def _highlight_stance(value: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return _md_span(m.group(0), "cdgreen")

    return re.sub(
        r"\b(KHÔNG ĐỒNG Ý|KHONG DONG Y|ĐỒNG Ý|DONG Y)\b",
        repl,
        value,
        flags=re.IGNORECASE,
    )


def _format_kv_line(line: str) -> str | None:
    m = re.match(r"^(?P<key>[^:]{1,60})\s*:\s*(?P<val>.+)$", line)
    if not m:
        return None
    key = _normalize_text(m.group("key"))
    val = _normalize_text(m.group("val"))
    if key.lower() in {"câu trả lời", "cau tra loi"}:
        val = _highlight_stance(val)
    return f"**{key}:** {val}"


def _writing_heading_level(s: str) -> int | None:
    if s.lower().startswith("phần "):
        return 2
    if re.match(r"^\d+\.\s+", s) or ("Bước" in s) or ("Step" in s):
        return 3
    if re.match(r"^[A-Z]\.\s+", s):
        return 4
    return None


def _reading_heading_level(s: str) -> int | None:
    if s.lower().startswith("phần "):
        return 2
    if s.lower().startswith("questions") or s.lower().startswith("glossary"):
        return 2
    if re.fullmatch(r"[A-H]", s.strip()):
        return 3
    if re.match(r"^\d+\.\s+", s) and len(s) <= 90:
        return 3
    return None


def _is_note_line(s: str, *, mode: str) -> bool:
    s = s.strip()
    if mode == "writing":
        return bool(re.match(r"^(lưu ý|note|tips|tip)\b", s, flags=re.IGNORECASE))
    if mode == "reading":
        return bool(
            re.match(r"^(yêu cầu|requirement|instructions?)\b", s, flags=re.IGNORECASE)
            or re.match(r"^(choose|complete|answer|write|match)\b", s, flags=re.IGNORECASE)
        )
    return False


def _format_inline_paragraph(s: str, *, mode: str) -> str:
    s = _normalize_text(s)
    kv = _format_kv_line(s)
    if kv is not None:
        return kv

    if mode == "writing" and s.endswith(":") and len(s) <= 50:
        head = _normalize_text(s[:-1])
        return f"**{_md_span(head, 'cdblue')}:**"
    if mode == "reading" and s.endswith(":") and len(s) <= 40:
        head = _normalize_text(s[:-1])
        return f"**{_md_span(head, 'cdblue')}**"

    # Reading: roman-heading list entries like "i  Atmospheric impacts"
    m_roman = re.match(r"^(?P<roman>i{1,3}|iv|v|vi{0,3}|ix|x|xi)\s+(?P<rest>.+)$", s, flags=re.IGNORECASE)
    if mode == "reading" and m_roman:
        roman = m_roman.group("roman").lower()
        rest = _normalize_text(m_roman.group("rest"))
        return f"**{_md_span(roman, 'cdblue')}** {rest}"

    # Reading: (1) / 1) / 1. question lines
    m_q = re.match(r"^\((\d{1,3})\)\s*(.+)$", s)
    if mode == "reading" and m_q:
        return f"**({m_q.group(1)})** {_normalize_text(m_q.group(2))}"
    m_q2 = re.match(r"^(\d{1,3})[).]\s*(.+)$", s)
    if mode == "reading" and m_q2:
        return f"**{m_q2.group(1)}.** {_normalize_text(m_q2.group(2))}"

    return s


def _render_before_after_block(body: list[Paragraph], *, start_index: int) -> tuple[list[str], int]:
    """
    Returns (markdown_lines, next_index).
    Mirrors the LaTeX renderer's "Before & After" handling, but outputs a Markdown table.
    """
    title = _normalize_text(body[start_index].text)
    out: list[str] = []
    out.append(f"### {title}")
    out.append("")
    i = start_index + 1

    # Optional description lines before headers/rows.
    while i < len(body) and body[i].text.strip():
        t = _normalize_text(body[i].text)
        if _writing_heading_level(t) is not None:
            break
        if re.search(r"câu\s*gốc|before", t, flags=re.IGNORECASE):
            break
        out.append(f"> {t}")
        i += 1
    if out and out[-1].startswith("> "):
        out.append("")

    left_header = "Before"
    right_header = "After"
    if i + 1 < len(body):
        h1 = _normalize_text(body[i].text)
        h2 = _normalize_text(body[i + 1].text)
        if re.search(r"câu\s*gốc|before", h1, flags=re.IGNORECASE) and re.search(
            r"câu\s+nâng\s*cấp|after", h2, flags=re.IGNORECASE
        ):
            left_header = h1
            right_header = h2
            i += 2

    row_lines: list[str] = []
    while i < len(body):
        t_raw = body[i].text.strip()
        if not t_raw:
            i += 1
            break
        t = _normalize_text(t_raw)
        if _writing_heading_level(t) is not None:
            break
        row_lines.append(t)
        i += 1

    rows: list[tuple[str, str]] = []
    for j in range(0, len(row_lines), 2):
        left = row_lines[j]
        right = row_lines[j + 1] if j + 1 < len(row_lines) else ""
        rows.append((left, right))

    out.append(f"| {left_header} | {right_header} |")
    out.append("| --- | --- |")
    for left, right in rows:
        out.append(f"| {left} | {right} |")
    out.append("")
    return out, i


def _render_markdown_body(paragraphs: list[Paragraph], *, mode: str) -> list[str]:
    lines: list[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list and (not lines or lines[-1] != ""):
            lines.append("")
        in_list = False

    def heading_level(s: str) -> int | None:
        if mode == "writing":
            return _writing_heading_level(s)
        return _reading_heading_level(s)

    i = 0
    while i < len(paragraphs):
        p = paragraphs[i]
        s = _normalize_text(p.text)
        if not s:
            i += 1
            continue

        if mode == "reading" and p.list_level is None:
            m_roman = re.match(r"^(?P<roman>i{1,3}|iv|v|vi{0,3}|ix|x|xi)\s+(?P<rest>.+)$", s, flags=re.IGNORECASE)
            if m_roman:
                in_list = True
                lines.append(f"- {_format_inline_paragraph(s, mode=mode)}")
                i += 1
                continue
            m_ans = re.match(r"^(?P<num>\d{1,3})\s+(?P<rest>Paragraph\s+[A-H].*)$", s, flags=re.IGNORECASE)
            if m_ans:
                in_list = True
                num = _normalize_text(m_ans.group("num"))
                rest = _normalize_text(m_ans.group("rest"))
                lines.append(f"- **{num}.** {rest}")
                i += 1
                continue

        if mode == "writing" and BEFORE_AFTER_RE.search(s):
            close_list()
            block_lines, next_i = _render_before_after_block(paragraphs, start_index=i)
            lines.extend(block_lines)
            i = next_i
            continue

        lvl = heading_level(s)
        if lvl is not None:
            close_list()
            lines.append("#" * lvl + " " + s)
            lines.append("")
            i += 1
            continue

        if _is_note_line(s, mode=mode):
            close_list()
            lines.append("> " + s)
            lines.append("")
            i += 1
            continue

        if p.list_level is None:
            close_list()
            lines.append(_format_inline_paragraph(s, mode=mode))
            lines.append("")
            i += 1
            continue

        in_list = True
        list_level = max(0, int(p.list_level or 0))
        bullet = "-" if (p.list_fmt or "").lower() != "decimal" else "1."
        indent = " " * (4 * list_level)
        lines.append(f"{indent}{bullet} {_format_inline_paragraph(s, mode=mode)}")
        i += 1

    close_list()
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def render_writing_md(*, level: int, section: Section) -> str:
    prompt = section.paragraphs[0].text if section.paragraphs else "[Your Writing Prompt Here]"
    body = section.paragraphs[1:] if len(section.paragraphs) >= 2 else []
    collection = f"Level {level} — W{section.week} ({section.dates})"

    out: list[str] = []
    out.append("---")
    out.append(f'title: "{collection}"')
    out.append("skill: Writing")
    out.append(f"level: {level}")
    out.append(f"week: {section.week}")
    out.append(f'dates: "{section.dates}"')
    out.append("---")
    out.append("")
    out.append("::: collectiontitle")
    out.append(collection)
    out.append(":::")
    out.append("")
    out.append("::: prompt")
    out.append(_normalize_text(prompt))
    out.append(":::")
    out.append("")
    out.extend(_render_markdown_body(body, mode="writing"))
    out.append("")
    return "\n".join(out)


def render_reading_md(*, level: int, section: Section) -> str:
    title = section.paragraphs[0].text if section.paragraphs else "Reading"
    body = section.paragraphs[1:] if len(section.paragraphs) >= 2 else []
    collection = f"Level {level} — W{section.week} ({section.dates})"

    out: list[str] = []
    out.append("---")
    out.append(f'title: "{collection}"')
    out.append("skill: Reading")
    out.append(f"level: {level}")
    out.append(f"week: {section.week}")
    out.append(f'dates: "{section.dates}"')
    out.append("---")
    out.append("")
    out.append("::: collectiontitle")
    out.append(collection)
    out.append(":::")
    out.append("")
    out.append("## " + _normalize_text(title))
    out.append("")
    out.extend(_render_markdown_body(body, mode="reading"))
    out.append("")
    return "\n".join(out)


def _find_raw47_input_dir(repo_root: Path) -> Path:
    candidates = [
        repo_root / "chuyenDe" / "raw47",
        repo_root / "chuyenDe" / "LS" / "raw" / "raw47",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise SystemExit("Cannot find raw47 input dir (tried: " + ", ".join(map(str, candidates)) + ")")


def main() -> int:
    parser = argparse.ArgumentParser(description="Split raw47 docx into Markdown files (Writing + Reading).")
    parser.add_argument(
        "--out",
        default="chuyenDe/RW/md/raw47",
        help="Output dir for Markdown (default: chuyenDe/RW/md/raw47)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    input_dir = _find_raw47_input_dir(repo_root)
    out_paths = OutputPaths(out_md_dir=(repo_root / args.out))

    docx_files = sorted(input_dir.glob("*.docx"))
    if not docx_files:
        raise SystemExit(f"No .docx found in {input_dir}")

    written = 0
    for docx_path in docx_files:
        m = LEVEL_RE.search(docx_path.name)
        if not m:
            raise SystemExit(f"Cannot infer level from filename: {docx_path.name}")
        level = int(m.group("level"))

        paragraphs = extract_paragraphs(docx_path)
        sections = split_sections(paragraphs)
        if not sections:
            raise SystemExit(f"No Wk sections found in {docx_path.name}")

        for section in sections:
            if section.skill == "Writing":
                md = render_writing_md(level=level, section=section)
            elif section.skill == "Reading":
                md = render_reading_md(level=level, section=section)
            else:
                raise SystemExit(f"Unexpected skill: {section.skill}")

            out_path = out_paths.md_path(skill=section.skill, level=level, week=section.week)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md, encoding="utf-8")
            written += 1

    print(f"Wrote {written} Markdown files to {out_paths.out_md_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
