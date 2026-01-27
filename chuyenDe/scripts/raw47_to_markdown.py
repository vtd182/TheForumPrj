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
    if re.match(r"^(i{1,3}|iv|v|vi{0,3}|ix|x)\.\s+", s, flags=re.IGNORECASE):
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

    # Make Vietnamese translations italic to distinguish from English samples.
    if mode == "writing":
        if s.lower().startswith("(bản dịch"):
            return f"*{s}*"
        if s.startswith("(") and s.endswith(")") and re.search(r"[À-ỹ]", s):
            return f"*{s}*"

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

    out.append("::: cdvocabtable")
    out.append(f"| {_escape_table_cell(left_header)} | {_escape_table_cell(right_header)} |")
    out.append("| --- | --- |")
    for left, right in rows:
        out.append(f"| {_escape_table_cell(left)} | {_escape_table_cell(right)} |")
    out.append(":::")
    out.append("")
    return out, i


VOCAB_CONTEXT_RE = re.compile(r"(từ vựng|cụm từ|language focus|công cụ ngôn ngữ)", re.IGNORECASE)
VOCAB_HDR_TERM_RE = re.compile(r"^(từ.*cụm\s*từ|từ\s*/?\s*cụm\s*từ|từ\s*vựng\s*/\s*cụm\s*từ)", re.IGNORECASE)
VOCAB_HDR_MEANING_RE = re.compile(r"^nghĩa", re.IGNORECASE)
VOCAB_HDR_EXAMPLE_RE = re.compile(r"^(ví\s*dụ|example)", re.IGNORECASE)
VOCAB_HDR_BASIC_RE = re.compile(r"^từ\s*cơ\s*bản", re.IGNORECASE)
VOCAB_HDR_ADV_RE = re.compile(r"^từ\s*nâng\s*cao", re.IGNORECASE)


def _escape_table_cell(s: str) -> str:
    # Keep table structure safe for Markdown.
    return _normalize_text(s).replace("|", r"\|")


def _render_vocab_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    out: list[str] = []
    out.append("::: cdvocabtable")
    out.append("| " + " | ".join(_escape_table_cell(h) for h in headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        out.append("| " + " | ".join(_escape_table_cell(c) for c in row) + " |")
    out.append(":::")
    out.append("")
    return out


def _try_render_vocab_table_plain(paragraphs: list[Paragraph], *, start_index: int, mode: str) -> tuple[list[str], int] | None:
    if mode != "writing":
        return None

    def is_break(p: Paragraph) -> bool:
        if p.list_level is not None:
            return True
        s = _normalize_text(p.text)
        if not s:
            return True
        if _is_note_line(s, mode=mode):
            return True
        if _writing_heading_level(s) is not None:
            return True
        return False

    # Need consecutive non-list, non-heading header lines.
    if start_index + 2 >= len(paragraphs):
        return None
    if paragraphs[start_index].list_level is not None:
        return None

    h1 = _normalize_text(paragraphs[start_index].text)
    h2 = _normalize_text(paragraphs[start_index + 1].text)
    h3 = _normalize_text(paragraphs[start_index + 2].text)

    # 4-column vocab table (we will render as 3 columns to avoid overflow).
    if start_index + 3 < len(paragraphs):
        h4 = _normalize_text(paragraphs[start_index + 3].text)
        if (
            VOCAB_HDR_BASIC_RE.match(h1)
            and VOCAB_HDR_ADV_RE.match(h2)
            and VOCAB_HDR_MEANING_RE.match(h3)
            and VOCAB_HDR_EXAMPLE_RE.match(h4)
        ):
            i = start_index + 4
            cells: list[str] = []
            while i < len(paragraphs) and not is_break(paragraphs[i]):
                cells.append(_normalize_text(paragraphs[i].text))
                i += 1
            rows: list[list[str]] = []
            for j in range(0, len(cells), 4):
                if j + 3 >= len(cells):
                    break
                basic, adv, meaning, example = cells[j : j + 4]
                note = f"Nghĩa: {meaning}<br>Ví dụ: {example}"
                rows.append([basic, adv, note])
            return _render_vocab_table([h1, h2, "Nghĩa + Ví dụ"], rows), i

    # 3-column vocab table.
    if VOCAB_HDR_TERM_RE.match(h1) and VOCAB_HDR_MEANING_RE.match(h2) and VOCAB_HDR_EXAMPLE_RE.match(h3):
        i = start_index + 3
        cells: list[str] = []
        while i < len(paragraphs) and not is_break(paragraphs[i]):
            cells.append(_normalize_text(paragraphs[i].text))
            i += 1
        rows: list[list[str]] = []
        for j in range(0, len(cells), 3):
            if j + 2 >= len(cells):
                break
            rows.append(cells[j : j + 3])
        return _render_vocab_table([h1, h2, h3], rows), i

    return None


def _try_render_vocab_table_list(paragraphs: list[Paragraph], *, start_index: int, mode: str) -> tuple[list[str], int] | None:
    if mode != "writing":
        return None
    p0 = paragraphs[start_index]
    if p0.list_level is None or int(p0.list_level or 0) != 0:
        return None
    if (p0.list_fmt or "").lower() == "decimal":
        return None

    # Term definition should look like "Term (pos): meaning".
    first = _normalize_text(p0.text)
    if ":" not in first:
        return None
    key, val = first.split(":", 1)
    if not key.strip():
        return None

    i = start_index
    rows: list[list[str]] = []
    while i < len(paragraphs):
        p = paragraphs[i]
        if p.list_level is None:
            break
        lvl = int(p.list_level or 0)
        if lvl != 0:
            break

        term_line = _normalize_text(p.text)
        if ":" in term_line:
            term, meaning = term_line.split(":", 1)
        else:
            term, meaning = term_line, ""

        examples: list[str] = []
        extra_meaning: list[str] = []
        j = i + 1
        while j < len(paragraphs) and paragraphs[j].list_level is not None and int(paragraphs[j].list_level or 0) > 0:
            sub = _normalize_text(paragraphs[j].text)
            if re.match(r"^(ví\s*dụ|example)\s*:", sub, flags=re.IGNORECASE):
                examples.append(re.sub(r"^(ví\s*dụ|example)\s*:\s*", "", sub, flags=re.IGNORECASE))
            elif re.match(r"^nghĩa\s*là\s*:", sub, flags=re.IGNORECASE):
                extra_meaning.append(re.sub(r"^nghĩa\s*là\s*:\s*", "", sub, flags=re.IGNORECASE))
            elif sub.startswith("(") and sub.endswith(")") and re.search(r"[À-ỹ]", sub):
                examples.append(sub)
            j += 1

        meaning_out = _normalize_text(meaning)
        if extra_meaning:
            meaning_out = (meaning_out + " (" + "; ".join(extra_meaning) + ")").strip()
        ex_out = "<br>".join(examples)
        rows.append([term.strip(), meaning_out, ex_out])
        i = j

    if not rows:
        return None
    return _render_vocab_table(["Từ/Cụm từ", "Nghĩa", "Ví dụ"], rows), i


def _render_markdown_body(paragraphs: list[Paragraph], *, mode: str) -> list[str]:
    lines: list[str] = []
    in_list = False
    vocab_active = False

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
            if mode == "writing":
                if VOCAB_CONTEXT_RE.search(s):
                    vocab_active = True
                elif lvl == 2:
                    vocab_active = False
            lines.append("#" * lvl + " " + s)
            lines.append("")
            i += 1
            continue

        if mode == "writing":
            plain_table = _try_render_vocab_table_plain(paragraphs, start_index=i, mode=mode)
            if plain_table is not None:
                close_list()
                table_lines, next_i = plain_table
                lines.extend(table_lines)
                i = next_i
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

        if mode == "writing" and vocab_active:
            list_table = _try_render_vocab_table_list(paragraphs, start_index=i, mode=mode)
            if list_table is not None:
                close_list()
                table_lines, next_i = list_table
                lines.extend(table_lines)
                i = next_i
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
