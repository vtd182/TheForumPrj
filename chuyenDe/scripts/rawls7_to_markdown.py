#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


RAW_NAME_RE = re.compile(r"^(Listening|Speaking)-Level(?P<level>\d+)-W(?P<week>\d+)\.docx$", re.I)


@dataclass(frozen=True)
class ParsedName:
    skill: str
    level: int
    week: int


def _parse_filename(p: Path) -> ParsedName | None:
    m = RAW_NAME_RE.match(p.name)
    if not m:
        return None
    skill = m.group(1)
    skill = "Listening" if skill.lower() == "listening" else "Speaking"
    return ParsedName(skill=skill, level=int(m.group("level")), week=int(m.group("week")))


def _run_pandoc_to_md(docx: Path) -> str:
    proc = subprocess.run(
        [
            "pandoc",
            str(docx),
            "--to",
            "markdown",
            "--wrap=none",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.stdout


_HR_RE = re.compile(r"^\s*-{10,}\s*$")
_EMPTY_TABLE_RE = re.compile(r"^\s*\|\s*\|\s*$")
_EMPTY_TABLE_RULE_RE = re.compile(r"^\s*\|\s*-+\s*\|\s*$")


def _strip_md_emphasis(s: str) -> str:
    s = s.strip()
    # remove surrounding emphasis a few times (pandoc sometimes nests *** **)
    for _ in range(3):
        s2 = re.sub(r"^\*\*\*(.+)\*\*\*$", r"\1", s)
        s2 = re.sub(r"^\*\*(.+)\*\*$", r"\1", s2)
        s2 = re.sub(r"^\*(.+)\*$", r"\1", s2)
        if s2 == s:
            break
        s = s2.strip()
    return s


def _clean_heading(line: str) -> str:
    m = re.match(r"^(#{1,6})\s+(.*)$", line)
    if not m:
        return line
    hashes = m.group(1)
    rest = _strip_md_emphasis(m.group(2))
    rest = re.sub(r"\s+", " ", rest).strip()
    return f"{hashes} {rest}"


def _drop_weird_lines(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s in {"**\\**", "**\\", "\\", "**\\**\\**"}:
        return True
    if re.fullmatch(r"#{1,6}\s*", s):
        return True
    if s == "**\\**" or s == "**\\** ":
        return True
    return False


def _normalize_underlines(s: str) -> str:
    # [Gift]{.underline} -> Gift
    s = re.sub(r"\[([^\]]+)\]\{\.underline\}", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\{\.underline[^}]*\}", r"\1", s)
    # <u>Gift</u> (gfm sometimes) -> Gift
    s = re.sub(r"<u>(.*?)</u>", r"\1", s)
    return s


def _normalize_bullets(line: str) -> str:
    s = line.rstrip()
    s = re.sub(r"^\s*[•●·]\s+", "- ", s)
    return s


def _is_main_ideas_line(line: str) -> bool:
    s = _strip_md_emphasis(_normalize_underlines(line)).strip().lower()
    return s in {"main ideas:", "main ideas"}


def _clean_grid_table_to_prompt(lines: list[str], *, start: int) -> tuple[list[str], int] | None:
    # Pandoc sometimes emits grid table for cue card (single-column).
    if not lines[start].lstrip().startswith("+"):
        return None
    i = start
    if not re.match(r"^\s*\+\-+\+\s*$", lines[i]):
        return None

    i += 1
    content: list[str] = []
    while i < len(lines):
        ln = lines[i].rstrip("\n")
        if re.match(r"^\s*\+\=+\+\s*$", ln) or re.match(r"^\s*\+\-+\+\s*$", ln):
            # end of table
            i += 1
            break
        m = re.match(r"^\s*\|\s*(.*?)\s*\|\s*$", ln)
        if m:
            cell = _strip_md_emphasis(_normalize_underlines(m.group(1))).strip()
            if cell:
                content.append(cell)
        i += 1

    if not content:
        return None

    title = content[0]
    rest_started = False
    cues: list[str] = []
    rest: list[str] = []

    for c in content[1:]:
        c = c.strip()
        if not c:
            continue
        if rest_started:
            rest.append(c)
            continue

        # Cue-card bullets are usually short phrases like "When it was".
        if re.match(r"^(When|Where|Why|Who|What|And)\\b", c, flags=re.I) and len(c) <= 90 and not re.search(
            r"[.!?]", c
        ):
            cues.append(c)
            continue

        # If we already collected the typical 4 cues, treat anything else as the model answer.
        if len(cues) >= 4:
            rest_started = True
            rest.append(c)
            continue

        # If it looks like a paragraph (sentences / long), start the model answer section.
        if len(c) > 110 or re.search(r"[.!?]", c) or re.match(r"^I('?m)?\\b", c, flags=re.I):
            rest_started = True
            rest.append(c)
            continue

        cues.append(c)

    out: list[str] = []
    out.append("::: prompt")
    out.append(f"**{title}**")
    for b in cues:
        out.append(f"- {b}")
    out.append(":::")
    out.append("")
    if rest:
        out.append("**Sample answer:**")
        out.append("")
        for p in rest:
            out.append(p)
            out.append("")
    return out, i


def _clean_simple_table_to_pipe(lines: list[str], *, start: int) -> tuple[list[str], int] | None:
    """
    Convert Pandoc "simple tables" (Markdown) into a pipe table wrapped in cdlisteningtable.

    Example pattern:
      Header A     Header B
        -----      -----
        row a      row b
    """
    if start + 1 >= len(lines):
        return None
    header = _normalize_underlines(lines[start].rstrip())
    sep = lines[start + 1].rstrip()

    if header.strip() == "" or not re.search(r"\s{2,}", header):
        return None
    if not re.match(r"^\s*-{5,}(\s+-{5,})+\s*$", sep):
        return None

    header_parts = [p.strip() for p in re.split(r"\s{2,}", header.strip()) if p.strip()]
    if len(header_parts) != 2:
        return None

    h1 = _strip_md_emphasis(header_parts[0]).strip()
    h2 = _strip_md_emphasis(header_parts[1]).strip()

    rows: list[tuple[str, str]] = []
    i = start + 2
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        # stop at next section/paragraph (table rows are indented in pandoc output)
        if not ln.startswith(" "):
            break
        parts = [p.strip() for p in re.split(r"\s{2,}", ln.strip(), maxsplit=1)]
        if not parts:
            i += 1
            continue
        left = parts[0]
        right = parts[1] if len(parts) > 1 else ""
        # Keep inline emphasis in cells (bold placeholders), but normalize underline syntax.
        left = _normalize_underlines(left)
        right = _normalize_underlines(right)
        rows.append((left, right))
        i += 1

    if not rows:
        return None

    out: list[str] = []
    out.append("::: cdlisteningtable")
    out.append(f"| {h1} | {h2} |")
    out.append("| --- | --- |")
    for left, right in rows:
        out.append(f"| {left.replace('|', '\\\\|')} | {right.replace('|', '\\\\|')} |")
    out.append(":::")
    out.append("")
    return out, i


def clean_docx_markdown(text: str, *, skill: str) -> str:
    raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    # Drop leading artifacts (pandoc sometimes emits an empty horizontal rule/table).
    lines: list[str] = []
    for ln in raw_lines:
        if _HR_RE.match(ln):
            continue
        if _EMPTY_TABLE_RE.match(ln) or _EMPTY_TABLE_RULE_RE.match(ln):
            continue
        if _drop_weird_lines(ln):
            continue
        lines.append(ln)

    out: list[str] = []
    i = 0
    in_list = False
    after_mainideas = False
    mainideas_seen_items = 0

    while i < len(lines):
        ln = lines[i].rstrip()
        ln = _normalize_underlines(ln)

        # Fix broken bold markers (pandoc can split **...** across lines).
        if ln.endswith("**") and ln.count("**") == 1 and not ln.lstrip().startswith("**"):
            ln = ln[:-2].rstrip()
        if ln.lstrip().startswith("**") and not ln.rstrip().endswith("**") and ln.count("**") == 1:
            ln = ln.lstrip()[2:].lstrip()
        ln = re.sub(r"\*\*\\\*\*\s*$", "", ln)
        ln = re.sub(r"\*\*\\\s*$", "", ln)

        # Normalize vocab marker lines (we'll append the vocab table at the end).
        ln_stripped = _strip_md_emphasis(ln).strip()
        if re.fullmatch(r"(?i)(từ vựng|tu vung|vocabulary)(\\s*[-–—].*)?", ln_stripped) or re.fullmatch(
            r"(?i)từ vựng\\s*--\\s*vocabulary\\s*list", ln_stripped
        ):
            ln = "## Từ vựng"

        # Remove standalone title line from source docx (we inject our own collection title).
        if _strip_md_emphasis(ln).strip().lower().startswith("tài liệu chuyên đề"):
            i += 1
            continue

        # Listening: convert Pandoc simple tables (e.g., "Complete the table below") to pipe tables.
        if skill.lower() == "listening":
            tbl_simple = _clean_simple_table_to_pipe(lines, start=i)
            if tbl_simple is not None:
                block, next_i = tbl_simple
                out.extend(block)
                in_list = False
                after_mainideas = False
                mainideas_seen_items = 0
                i = next_i
                continue

        # Convert grid table cue card (Speaking Part 2) into prompt box.
        tbl = _clean_grid_table_to_prompt(lines, start=i)
        if tbl is not None and skill.lower() == "speaking":
            block, next_i = tbl
            out.extend(block)
            in_list = False
            after_mainideas = False
            mainideas_seen_items = 0
            i = next_i
            continue

        # Headings: strip bold/italic wrappers.
        if re.match(r"^#{1,6}\s+", ln):
            ln = _clean_heading(ln)
            if re.fullmatch(r"#{1,6}\s*", ln.strip()):
                i += 1
                continue
            # Normalize vocab heading text (we'll append the vocab table at the end).
            if re.search(r"(từ vựng|vocabulary)", ln, flags=re.I):
                ln = re.sub(r"^#{1,6}\s+.*$", "## Từ vựng", ln)

        # Normalize some bold-only lines into headings for Listening.
        if skill.lower() == "listening":
            only_bold = re.match(r"^\s*\*\*(.+?)\*\*\s*$", ln)
            if only_bold:
                text_b = only_bold.group(1).strip()
                text_b_norm = _normalize_underlines(text_b)
                if re.match(r"^(SECTION\s+\d+|Questions?\s+\d)", text_b_norm, flags=re.I):
                    if re.match(r"^Questions?\s+\d", text_b_norm, flags=re.I):
                        ln = f"### {text_b_norm}"
                    else:
                        ln = f"## {text_b_norm}"
                else:
                    ln = f"**{text_b_norm}**"
            # Also handle lines like "SECTION 2**" left over from a split bold marker.
            if re.match(r"^\s*SECTION\s+\d+\*{2}\s*$", ln, flags=re.I):
                ln = re.sub(r"\*{2}\s*$", "", ln).strip()
                ln = f"## {ln}"

        # Speaking: remove accidental "## " in normal paragraphs.
        if skill.lower() == "speaking":
            if (
                ln.startswith("## ")
                and not re.match(r"^##\s+PART\s+\d+", ln, flags=re.I)
                and not re.search(r"(từ vựng|vocabulary)", ln, flags=re.I)
            ):
                ln = ln[3:].lstrip()
            if ln.startswith("#### ") and not re.match(r"^####\s+\d+\.", ln):
                candidate = ln[5:].strip()
                candidate = _strip_md_emphasis(candidate)
                if _is_main_ideas_line(candidate):
                    ln = candidate
                elif after_mainideas:
                    # Often, "Main ideas" lines are mistakenly styled as headings in DOCX.
                    # Keep them plain here so the main-ideas normalizer can bulletize them.
                    ln = candidate
                elif len(candidate) <= 60 and "?" not in candidate:
                    ln = f"### {candidate}"
                else:
                    ln = candidate

        ln = _normalize_bullets(ln)

        if _is_main_ideas_line(ln):
            out.append("**[Main ideas]{.cdblue}:**")
            after_mainideas = True
            mainideas_seen_items = 0
            in_list = False
            i += 1
            continue

        # If we are in "Main ideas" block, coerce short lines into bullets until a real paragraph starts.
        if after_mainideas:
            s = ln.strip()
            if not s:
                # Ignore blanks inside the block if the next non-empty line still looks like an item.
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    raw_nxt = _normalize_underlines(lines[j].rstrip())
                    if raw_nxt.lstrip().startswith("#"):
                        mhd = re.match(r"^\s*(#{1,6})\s+(.+)$", raw_nxt)
                        if mhd:
                            lvl = len(mhd.group(1))
                            heading_text = _strip_md_emphasis(mhd.group(2).strip())
                            # Allow only deep headings (####...) that are clearly "idea bullets".
                            if lvl >= 4 and not re.match(r"^\d+\.", heading_text) and "?" not in heading_text and len(heading_text) <= 140:
                                i += 1
                                continue
                            # Otherwise treat as structural break.
                        out.append("")
                        after_mainideas = False
                        in_list = False
                        i += 1
                        continue

                    nxt = _normalize_bullets(_normalize_underlines(lines[j].rstrip()))
                    nxt = re.sub(r"^#{1,6}\s+", "", nxt).strip()
                    nxt = _strip_md_emphasis(nxt)
                    if re.match(r"^\d+\.", nxt):
                        out.append("")
                        after_mainideas = False
                        in_list = False
                        i += 1
                        continue
                    if nxt and not re.match(r"^(PART|SECTION)\b", nxt, flags=re.I) and len(nxt) <= 140:
                        i += 1
                        continue
                out.append("")
                after_mainideas = False
                in_list = False
                i += 1
                continue
            if s.startswith("- "):
                out.append(s)
                in_list = True
                mainideas_seen_items += 1
                i += 1
                continue
            # treat short lines as bullets (pandoc sometimes turned them into headings)
            plain = s
            if re.match(r"^#{1,6}\s+", plain):
                # Topic/part headings end the main-ideas block.
                if re.match(r"^#{1,3}\s+", plain):
                    after_mainideas = False
                    in_list = False
                    continue
                heading_text = re.sub(r"^#{1,6}\s+", "", plain).strip()
                # If this looks like a real structural heading, stop the main-ideas block.
                if re.match(r"^(PART|SECTION)\b", heading_text, flags=re.I):
                    after_mainideas = False
                    in_list = False
                    continue
                plain = heading_text
            if re.match(r"^\*\*\d+\.", plain):
                after_mainideas = False
                in_list = False
                continue
            if re.match(r"^\d+\.", plain):
                after_mainideas = False
                in_list = False
                continue
            plain = _strip_md_emphasis(plain)
            if len(plain) <= 140 and mainideas_seen_items < 12:
                out.append(f"- {plain}")
                in_list = True
                mainideas_seen_items += 1
                i += 1
                continue
            # otherwise start a paragraph
            out.append("")
            after_mainideas = False
            in_list = False

        # Collapse blank lines inside lists.
        if not ln.strip():
            if in_list and i + 1 < len(lines):
                nxt = _normalize_bullets(_normalize_underlines(lines[i + 1].rstrip()))
                if nxt.strip().startswith("- "):
                    i += 1
                    continue
            out.append("")
            in_list = False
            i += 1
            continue

        # Drop empty headings like "##" that can appear from DOCX artifacts.
        if re.fullmatch(r"#{1,6}\s*", ln.strip()):
            i += 1
            continue

        if ln.strip().startswith("- "):
            in_list = True
        else:
            in_list = False

        # Normalize "PART X:" headings in speaking.
        if skill.lower() == "speaking":
            m_part = re.match(r"^(##)\s+PART\s+(\d+)\s*:?\s*$", ln, flags=re.I)
            if m_part:
                ln = f"## PART {m_part.group(2)}"

        out.append(ln)
        i += 1

    # Trim repeated blank lines.
    cleaned: list[str] = []
    blank = 0
    for ln in out:
        if ln.strip() == "":
            blank += 1
            if blank <= 1:
                cleaned.append("")
            continue
        blank = 0
        # Drop consecutive duplicate vocab headings.
        if ln.strip() == "## Từ vựng" and cleaned and cleaned[-1].strip() == "## Từ vựng":
            continue
        cleaned.append(ln.rstrip())

    return "\n".join(cleaned).strip() + "\n"


def _append_vocab_table(md: str, *, vocab_rows: list[list[str]]) -> str:
    lines = md.rstrip().split("\n")

    def has_vocab_heading() -> bool:
        for ln in lines:
            low = ln.lower()
            if re.match(r"^#{1,6}\s+", ln) and ("từ vựng" in low or "vocabulary" in low):
                return True
        return False

    if not has_vocab_heading():
        lines.append("")
        lines.append("## Từ vựng")
        lines.append("")

    # Always append ONE reading-style vocab table at the very end.
    lines.append("")
    lines.append("::: cdreadingvocabtable")
    lines.append("| Từ vựng (Từ loại) | /Phiên âm/ | Nghĩa tiếng Anh (Giải thích tiếng Việt) | Ví dụ minh họa |")
    lines.append("| --- | --- | --- | --- |")

    if vocab_rows:
        for r in vocab_rows:
            w, ipa, meaning, example = (r + ["", "", "", ""])[:4]
            w = w.replace("|", "\\|")
            ipa = ipa.replace("|", "\\|")
            meaning = meaning.replace("|", "\\|")
            example = example.replace("|", "\\|")
            lines.append(f"| {w} | {ipa} | {meaning} | {example} |")
    else:
        lines.append("|  |  |  |  |")

    lines.append(":::")
    lines.append("")
    return "\n".join(lines)


def render_markdown(*, meta: ParsedName, body: str) -> str:
    title = f"TÀI LIỆU CHUYÊN ĐỀ {meta.skill.upper()}"
    front = [
        "---",
        f'title: "{title}"',
        f"skill: {meta.skill}",
        f"level: {meta.level}",
        f"week: {meta.week}",
        "---",
        "",
        "::: collectiontitle",
        title,
        ":::",
        "",
    ]
    return "\n".join(front) + body


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert rawls7 DOCX (Listening/Speaking) into Markdown for templates.")
    ap.add_argument("--in-dir", type=Path, default=Path("chuyenDe/LS/raw/rawls7"))
    ap.add_argument("--out-dir", type=Path, default=Path("chuyenDe/LS/md/rawls7"))
    args = ap.parse_args()

    in_dir: Path = args.in_dir
    out_dir: Path = args.out_dir

    if not in_dir.exists():
        raise SystemExit(f"Missing input dir: {in_dir}")

    docxs = sorted(p for p in in_dir.iterdir() if p.suffix.lower() == ".docx")
    if not docxs:
        raise SystemExit(f"No .docx found in: {in_dir}")

    for docx in docxs:
        meta = _parse_filename(docx)
        if meta is None:
            continue
        raw_md = _run_pandoc_to_md(docx)
        cleaned = clean_docx_markdown(raw_md, skill=meta.skill)
        cleaned = _append_vocab_table(cleaned, vocab_rows=[])

        out_path = out_dir / meta.skill / f"Level{meta.level}" / f"W{meta.week}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render_markdown(meta=meta, body=cleaned), encoding="utf-8")
        print(out_path)


if __name__ == "__main__":
    main()
