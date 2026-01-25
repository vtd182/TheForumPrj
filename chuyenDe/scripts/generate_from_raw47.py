#!/usr/bin/env python3
from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
HEADER_RE = re.compile(
    r"^W(?P<week>\d+)\s*\((?P<dates>[^)]*)\)\s*:\s*(?P<skill>Writing|Reading)\s*$",
    re.IGNORECASE,
)
LEVEL_RE = re.compile(r"level(?P<level>\d+)", re.IGNORECASE)


@dataclass(frozen=True)
class Paragraph:
    text: str
    list_level: int | None = None  # 0-based nesting level for Word numbering/bullets
    list_fmt: str | None = None  # e.g. "bullet", "decimal"


@dataclass(frozen=True)
class Section:
    week: int
    dates: str
    skill: str  # "Writing" | "Reading"
    paragraphs: list[Paragraph]  # section body only (excludes header line)


def latex_escape(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = text.replace("\\", r"\textbackslash{}")
    for ch, repl in [
        ("{", r"\{"),
        ("}", r"\}"),
        ("$", r"\$"),
        ("&", r"\&"),
        ("#", r"\#"),
        ("%", r"\%"),
        ("_", r"\_"),
        ("^", r"\^{}"),
        ("~", r"\~{}"),
    ]:
        text = text.replace(ch, repl)
    return text


def _parse_numbering(doc: zipfile.ZipFile) -> dict[tuple[str, str], str]:
    """
    Returns mapping: (numId, ilvl) -> numFmt (e.g. bullet/decimal).
    Best-effort; if numbering.xml missing or incomplete, returns {}.
    """
    try:
        xml = doc.read("word/numbering.xml")
    except KeyError:
        return {}

    root = ET.fromstring(xml)

    abstract_levels: dict[str, dict[str, str]] = {}
    for abstract in root.findall("./w:abstractNum", NS):
        abs_id = abstract.get(f"{{{NS['w']}}}abstractNumId")
        if not abs_id:
            continue
        levels: dict[str, str] = {}
        for lvl in abstract.findall("./w:lvl", NS):
            ilvl = lvl.get(f"{{{NS['w']}}}ilvl")
            if ilvl is None:
                continue
            num_fmt_node = lvl.find("./w:numFmt", NS)
            if num_fmt_node is None:
                continue
            fmt = num_fmt_node.get(f"{{{NS['w']}}}val")
            if fmt:
                levels[ilvl] = fmt
        if levels:
            abstract_levels[abs_id] = levels

    num_to_abs: dict[str, str] = {}
    for num in root.findall("./w:num", NS):
        num_id = num.get(f"{{{NS['w']}}}numId")
        if not num_id:
            continue
        abs_node = num.find("./w:abstractNumId", NS)
        if abs_node is None:
            continue
        abs_id = abs_node.get(f"{{{NS['w']}}}val")
        if abs_id:
            num_to_abs[num_id] = abs_id

    mapping: dict[tuple[str, str], str] = {}
    for num_id, abs_id in num_to_abs.items():
        levels = abstract_levels.get(abs_id)
        if not levels:
            continue
        for ilvl, fmt in levels.items():
            mapping[(num_id, ilvl)] = fmt
    return mapping


def extract_paragraphs(docx_path: Path) -> list[Paragraph]:
    with zipfile.ZipFile(docx_path) as doc:
        numbering = _parse_numbering(doc)
        xml = doc.read("word/document.xml")
    root = ET.fromstring(xml)

    paragraphs: list[Paragraph] = []
    for p in root.findall(".//w:p", NS):
        texts = [t.text or "" for t in p.findall(".//w:t", NS)]
        if not texts:
            continue
        s = "".join(texts).replace("\xa0", " ").strip()

        if not s:
            continue

        list_level: int | None = None
        list_fmt: str | None = None
        num_pr = p.find("./w:pPr/w:numPr", NS)
        if num_pr is not None:
            num_id_node = num_pr.find("./w:numId", NS)
            ilvl_node = num_pr.find("./w:ilvl", NS)
            if num_id_node is not None and ilvl_node is not None:
                num_id = num_id_node.get(f"{{{NS['w']}}}val")
                ilvl = ilvl_node.get(f"{{{NS['w']}}}val")
                if num_id is not None and ilvl is not None and ilvl.isdigit():
                    list_level = int(ilvl)
                    list_fmt = numbering.get((num_id, ilvl))

        paragraphs.append(Paragraph(text=s, list_level=list_level, list_fmt=list_fmt))
    return paragraphs


def split_sections(paragraphs: list[Paragraph]) -> list[Section]:
    sections: list[Section] = []
    current_week: int | None = None
    current_dates: str = ""
    current_skill: str = ""
    current_paras: list[Paragraph] = []

    def flush() -> None:
        nonlocal current_week, current_dates, current_skill, current_paras
        if current_week is None:
            return
        sections.append(
            Section(
                week=current_week,
                dates=current_dates,
                skill=current_skill,
                paragraphs=current_paras,
            )
        )
        current_week = None
        current_dates = ""
        current_skill = ""
        current_paras = []

    for p in paragraphs:
        m = HEADER_RE.match(p.text)
        if m:
            flush()
            current_week = int(m.group("week"))
            current_dates = m.group("dates").strip()
            current_skill = m.group("skill").title()
            continue
        if current_week is None:
            continue
        current_paras.append(p)

    flush()
    return sections


def _is_writing_heading(s: str) -> bool:
    if s.lower().startswith("phần "):
        return True
    if re.match(r"^\d+\.\s+", s):
        return True
    if "Bước" in s or "Step" in s:
        return True
    if re.match(r"^[A-Z]\.\s+", s):
        return True
    return False


def _latex_escape_with_english_parens(text: str) -> str:
    """
    Escapes text for LaTeX, but italicizes short English-only parentheticals.
    Example: "... (Decoding the Prompt)" -> "... \\textit{(Decoding the Prompt)}"
    """
    out: list[str] = []
    pos = 0
    for m in re.finditer(r"\([^)]*\)", text):
        before = text[pos : m.start()]
        out.append(latex_escape(before))

        seg = m.group(0)
        inner = seg[1:-1].strip()
        if re.fullmatch(r"[A-Za-z0-9 &./'\"-]{1,60}", inner):
            out.append(r"\textit{" + latex_escape(seg) + r"}")
        else:
            out.append(latex_escape(seg))
        pos = m.end()
    out.append(latex_escape(text[pos:]))
    return "".join(out)


def _render_before_after_table(rows: list[tuple[str, str]], *, left_header: str, right_header: str) -> list[str]:
    if not rows:
        return []

    out: list[str] = []
    out.append(r"\begin{cdtablebox}")
    out.append(r"\renewcommand{\arraystretch}{1.25}")
    out.append(
        r"\begin{tabularx}{\linewidth}{>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X}"
    )
    out.append(r"\rowcolor{topicblue!12}\textbf{" + latex_escape(left_header) + r"} & \textbf{" + latex_escape(right_header) + r"} \\")
    out.append(r"\hline")
    for left, right in rows:
        out.append(latex_escape(left) + r" & " + latex_escape(right) + r" \\")
        out.append(r"\hline")
    out.append(r"\end{tabularx}")
    out.append(r"\end{cdtablebox}")
    return out


def _format_key_value(key: str, value: str) -> str:
    key_stripped = key.strip()
    val_escaped = latex_escape(value.strip())

    if key_stripped.lower() in {"môn học", "mon hoc"}:
        key_tex = r"\cdpurple{\underline{\textbf{Môn học:}}}"
        return key_tex + " " + val_escaped
    if key_stripped.lower() in {"tại sao quan trọng", "tai sao quan trong"}:
        key_tex = r"\cdpurple{\underline{\textit{Tại sao quan trọng:}}}"
        return key_tex + " " + val_escaped

    key_tex = r"\cdkv{" + latex_escape(key_stripped) + r"}"
    val_tex = val_escaped

    if key_stripped.lower() in {"câu trả lời", "cau tra loi"}:
        # highlight common stance markers if present
        val_tex = re.sub(
            r"\b(KHÔNG ĐỒNG Ý|KHONG DONG Y|ĐỒNG Ý|DONG Y)\b",
            lambda m: r"\cdgreen{\textbf{" + latex_escape(m.group(0)) + r"}}",
            val_tex,
            flags=re.IGNORECASE,
        )

    return key_tex + r"{" + val_tex + r"}"


def render_paragraph(paragraph: Paragraph, *, mode: str) -> str:
    s = paragraph.text.strip()
    if not s:
        return ""

    if mode == "writing":
        if s.lower().startswith("phần "):
            return rf"\cdsection{{{_latex_escape_with_english_parens(s)}}}" + "\n"
        if re.match(r"^\d+\.\s+", s) or "Bước" in s or "Step" in s:
            return rf"\cdstep{{{_latex_escape_with_english_parens(s)}}}" + "\n"
        if re.match(r"^[A-Z]\.\s+", s):
            return rf"\cdgreenheading{{{_latex_escape_with_english_parens(s)}}}" + "\n"

        kv_match = re.match(r"^(?P<key>[^:]{1,60})\s*:\s*(?P<val>.+)$", s)
        if kv_match:
            return _format_key_value(kv_match.group("key"), kv_match.group("val")) + "\n"

        if s.endswith(":") and len(s) <= 50:
            heading = latex_escape(s[:-1].rstrip())
            return rf"\cdblue{{\textbf{{{heading}:}}}}" + "\n"

        if re.match(r"^(lưu ý|note|tips|tip)\b", s.strip(), flags=re.IGNORECASE):
            return rf"\cdnoteinline{{{latex_escape(s)}}}" + "\n"

        return latex_escape(s) + "\n"

    if mode == "reading":
        if s.lower().startswith("phần "):
            return rf"\cdsection{{{latex_escape(s)}}}" + "\n"
        if re.fullmatch(r"[A-H]", s):
            return rf"\textbf{{{latex_escape(s)}}}\par" + "\n"
        if s.lower().startswith("questions") or s.lower().startswith("glossary"):
            return rf"\cdsection{{{latex_escape(s)}}}" + "\n"
        if re.match(r"^\d+\.\s+", s) and len(s) <= 90:
            return rf"\cdstep{{{_latex_escape_with_english_parens(s)}}}" + "\n"
        if re.match(r"^(yêu cầu|requirement|instructions?)\b", s, flags=re.IGNORECASE):
            return rf"\cdnoteinline{{{latex_escape(s)}}}" + "\n"
        if re.match(r"^(choose|complete|answer|write|match)\b", s, flags=re.IGNORECASE):
            return rf"\cdnoteinline{{{latex_escape(s)}}}" + "\n"
        if s.endswith(":") and len(s) <= 40:
            heading = latex_escape(s[:-1].rstrip())
            return rf"\cdblue{{\textbf{{{heading}}}}}" + "\n"
        m_q = re.match(r"^\((\d{1,3})\)\s*(.+)$", s)
        if m_q:
            return rf"\textbf{{({m_q.group(1)})}} {latex_escape(m_q.group(2))}" + "\n"
        m_q2 = re.match(r"^(\d{1,3})[).]\s*(.+)$", s)
        if m_q2:
            return rf"\textbf{{{m_q2.group(1)}.}} {latex_escape(m_q2.group(2))}" + "\n"
        m_q3 = re.match(r"^(\d{1,3})\s{2,}(.+)$", s)
        if m_q3:
            return rf"\textbf{{{m_q3.group(1)}}} {latex_escape(m_q3.group(2))}" + "\n"
        m_roman = re.match(r"^(i{1,3}|iv|v|vi{0,3}|ix|x|xi)\s{2,}(.+)$", s, flags=re.IGNORECASE)
        if m_roman:
            roman = m_roman.group(1).lower()
            rest = m_roman.group(2)
            return rf"\cdblue{{\textbf{{{latex_escape(roman)}}}}} {latex_escape(rest)}" + "\n"
        m_cau = re.match(r"^(Câu\\s*\\d+)\\s*:\\s*(.+)$", s, flags=re.IGNORECASE)
        if m_cau:
            return rf"\textbf{{{latex_escape(m_cau.group(1))}:}} {latex_escape(m_cau.group(2))}" + "\n"
        return latex_escape(s) + "\n"

    raise ValueError(f"unknown mode: {mode}")


def render_paragraphs(paragraphs: list[Paragraph], *, mode: str) -> list[str]:
    """
    Renders paragraphs while preserving Word list nesting when possible.
    """
    lines: list[str] = []
    list_stack: list[str] = []  # env per nesting level

    def current_level() -> int:
        return len(list_stack) - 1

    def close_lists(target_level: int = -1) -> None:
        while current_level() > target_level:
            env = list_stack.pop()
            lines.append(rf"\end{{{env}}}")

    def begin_list(env: str) -> None:
        list_stack.append(env)
        lines.append(rf"\begin{{{env}}}")

    def choose_env(p: Paragraph) -> str:
        if p.list_fmt and p.list_fmt.lower() not in {"bullet", "none"}:
            return "enumerate"
        return "itemize"

    for p in paragraphs:
        s = p.text.strip()
        if not s:
            continue

        is_heading = mode == "writing" and _is_writing_heading(s)

        if is_heading or p.list_level is None:
            close_lists()
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(render_paragraph(p, mode=mode).rstrip())
            continue

        # list paragraph
        lvl = p.list_level or 0

        # Word sometimes starts lists at ilvl=1 without providing a parent; render safely.
        if current_level() < 0 and lvl > 0:
            lvl = 0

        # Avoid jumping more than one nesting level at a time (also unsafe in LaTeX).
        if lvl > current_level() + 1:
            lvl = current_level() + 1

        if current_level() < 0:
            begin_list(choose_env(p))
        elif lvl > current_level():
            # Enter a nested list within the previous \item (LaTeX-valid).
            begin_list(choose_env(p))
        elif lvl < current_level():
            close_lists(target_level=lvl)

        content = render_paragraph(p, mode=mode).rstrip()
        lines.append(r"\item " + content)

    close_lists()
    return [ln for ln in lines if ln is not None]


def render_writing_tex(*, level: int, section: Section) -> str:
    prompt = section.paragraphs[0].text if section.paragraphs else "[Your Writing Prompt Here]"
    body = section.paragraphs[1:] if len(section.paragraphs) >= 2 else []

    parts: list[str] = []
    parts.append(r"\documentclass{../templateWriting/cdwriting}")
    parts.append("")
    parts.append(r"\newcommand{\authorinfo}{THE FORUM CENTER - NGUYỄN HOÀNG HUY}")
    parts.append(r"\newcommand{\documenttitle}{TÀI LIỆU CHUYÊN ĐỀ WRITING}")
    parts.append(
        r"\newcommand{\collectiontitle}{"
        + latex_escape(f"Level {level} — W{section.week} ({section.dates})")
        + r"}"
    )
    parts.append("")
    parts.append(r"\begin{document}")
    parts.append("")
    parts.append(r"\thispagestyle{firstpage}")
    parts.append(r"\makeworkshopheader{\authorinfo}{\documenttitle}{\collectiontitle}")
    parts.append(r"\pagestyle{otherpages}")
    parts.append("")
    parts.append(r"\workshopprompt{" + latex_escape(prompt) + r"}")
    parts.append("")
    parts.extend(render_writing_paragraphs(body))
    parts.append("")
    parts.append(r"\end{document}")
    parts.append("")
    return "\n".join(parts)


BEFORE_AFTER_RE = re.compile(r"(before\s*&\s*after|bảng\s+nâng\s+cấp)", re.IGNORECASE)


def render_writing_paragraphs(paragraphs: list[Paragraph]) -> list[str]:
    """
    Writing renderer with special handling for Before/After vocab upgrade blocks.
    """
    lines: list[str] = []
    chunk: list[Paragraph] = []

    def flush_chunk() -> None:
        nonlocal chunk
        if chunk:
            lines.extend(render_paragraphs(chunk, mode="writing"))
            chunk = []

    i = 0
    while i < len(paragraphs):
        p = paragraphs[i]
        s = p.text.strip()

        if s and BEFORE_AFTER_RE.search(s):
            flush_chunk()

            # Title
            lines.append(r"\cdstep{" + latex_escape(s) + r"}")
            i += 1

            # Optional description lines before the headers / rows
            desc: list[str] = []
            while i < len(paragraphs):
                t = paragraphs[i].text.strip()
                if not t:
                    i += 1
                    break
                if _is_writing_heading(t):
                    break
                if re.search(r"câu\s*gốc|before", t, flags=re.IGNORECASE):
                    break
                desc.append(t)
                i += 1
            if desc:
                lines.append(r"\cdnoteinline{" + latex_escape(" ".join(desc)) + r"}")

            # Headers (best-effort)
            left_header = "Before"
            right_header = "After"
            if i + 1 < len(paragraphs):
                h1 = paragraphs[i].text.strip()
                h2 = paragraphs[i + 1].text.strip()
                if re.search(r"câu\s*gốc|before", h1, flags=re.IGNORECASE) and re.search(
                    r"câu\s+nâng\s*cấp|after", h2, flags=re.IGNORECASE
                ):
                    left_header = h1
                    right_header = h2
                    i += 2

            # Rows: consume pairs until blank line / next heading
            row_lines: list[str] = []
            while i < len(paragraphs):
                t = paragraphs[i].text.strip()
                if not t:
                    i += 1
                    break
                if _is_writing_heading(t):
                    break
                row_lines.append(t)
                i += 1

            rows: list[tuple[str, str]] = []
            for j in range(0, len(row_lines), 2):
                left = row_lines[j]
                right = row_lines[j + 1] if j + 1 < len(row_lines) else ""
                rows.append((left, right))

            lines.extend(
                _render_before_after_table(rows, left_header=left_header, right_header=right_header)
            )
            continue

        chunk.append(p)
        i += 1

    flush_chunk()
    return lines


def render_reading_tex(*, level: int, section: Section) -> str:
    title = section.paragraphs[0].text if section.paragraphs else "Reading"
    body = section.paragraphs[1:] if len(section.paragraphs) >= 2 else []

    parts: list[str] = []
    parts.append(r"\documentclass{../templateReading/cdreading}")
    parts.append("")
    parts.append(r"\newcommand{\authorinfo}{THE FORUM CENTER - NGUYỄN HOÀNG HUY}")
    parts.append(r"\newcommand{\documenttitle}{TÀI LIỆU CHUYÊN ĐỀ READING}")
    parts.append(
        r"\newcommand{\collectiontitle}{"
        + latex_escape(f"Level {level} — W{section.week} ({section.dates})")
        + r"}"
    )
    parts.append("")
    parts.append(r"\begin{document}")
    parts.append("")
    parts.append(r"\thispagestyle{firstpage}")
    parts.append(r"\makeworkshopheader{\authorinfo}{\documenttitle}{\collectiontitle}")
    parts.append(r"\pagestyle{otherpages}")
    parts.append("")
    parts.append(r"\cdsection{" + latex_escape(title) + r"}")
    parts.append("")
    parts.extend(render_paragraphs(body, mode="reading"))
    parts.append("")
    parts.append(r"\end{document}")
    parts.append("")
    return "\n".join(parts)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    input_dir_candidates = [
        repo_root / "chuyenDe" / "raw47",
        repo_root / "chuyenDe" / "LS" / "raw" / "raw47",
    ]
    input_dir = next((p for p in input_dir_candidates if p.exists()), None)
    if input_dir is None:
        raise SystemExit("Cannot find raw47 input dir (tried: " + ", ".join(map(str, input_dir_candidates)) + ")")
    out_dir = repo_root / "chuyenDe" / "RW" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    docx_files = sorted(input_dir.glob("*.docx"))
    if not docx_files:
        raise SystemExit(f"No .docx found in {input_dir}")

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
                tex = render_writing_tex(level=level, section=section)
                out_path = out_dir / f"Writing-Level{level}-W{section.week}.tex"
            elif section.skill == "Reading":
                tex = render_reading_tex(level=level, section=section)
                out_path = out_dir / f"Reading-Level{level}-W{section.week}.tex"
            else:
                raise SystemExit(f"Unexpected skill: {section.skill}")

            out_path.write_text(tex, encoding="utf-8")
            print(out_path.relative_to(repo_root))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
