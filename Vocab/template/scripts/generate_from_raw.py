#!/usr/bin/env python3
import argparse
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Entry:
    word: str
    pos: str
    ipa: str
    definition_en: str
    note_vi: str
    example_en: str


ENTRY_RE_H2 = re.compile(
    r"^##\s+\*\*(?P<word>.+?)\s+\((?P<pos>[^)]+)\)\s+/(?P<ipa>.+?)/:\*\*\s+(?P<rest>.+?)\s*$"
)
# Supports formats like:
#   1. **Sustainability (n) /.../:** ...
#   **Sustainability (n) /.../:** ...
ENTRY_RE_LIST = re.compile(
    r"^(?:\d+\.\s*)?\*\*(?P<word>.+?)\s+\((?P<pos>[^)]+)\)\s+/(?P<ipa>.+?)/:\*\*\s+(?P<rest>.+?)\s*$"
)
EXAMPLE_RE = re.compile(r"^Ví dụ:\s*(?P<ex>.*)\s*$", re.IGNORECASE)


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "#": r"\#",
        "$": r"\$",
        "%": r"\%",
        "&": r"\&",
        "_": r"\_",
        "^": r"\textasciicircum{}",
        "~": r"\textasciitilde{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def parse_raw(text: str) -> list[Entry]:
    lines = [ln.rstrip() for ln in text.splitlines()]
    entries: list[Entry] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        m = ENTRY_RE_H2.match(line) or ENTRY_RE_LIST.match(line)
        if not m:
            continue
        word = m.group("word").strip()
        pos = m.group("pos").strip()
        ipa = m.group("ipa").strip()
        rest = m.group("rest").strip()
        # Prefer capturing the final Vietnamese note in parentheses at end of the line.
        note_vi = ""
        definition_en = rest
        m2 = re.match(r"^(?P<def>.*?)(?:\s*\((?P<note>[^()]*)\))\.?\s*$", rest)
        if m2 and m2.group("note") is not None:
            definition_en = m2.group("def").strip()
            note_vi = m2.group("note").strip()

        example_en_parts: list[str] = []
        while i < len(lines):
            ln = lines[i].strip()
            if ln.startswith("## "):
                break
            i += 1
            if not ln:
                if example_en_parts:
                    break
                continue
            exm = EXAMPLE_RE.match(ln)
            if exm:
                ex = exm.group("ex").strip()
                if ex:
                    example_en_parts.append(ex)
                while i < len(lines):
                    peek = lines[i].strip()
                    if not peek or peek.startswith("## "):
                        break
                    if EXAMPLE_RE.match(peek):
                        break
                    example_en_parts.append(peek)
                    i += 1
                break

        entries.append(
            Entry(
                word=word,
                pos=pos,
                ipa=ipa,
                definition_en=definition_en,
                note_vi=note_vi,
                example_en=" ".join(example_en_parts).strip(),
            )
        )
    return entries


def write_data_tex(entries: list[Entry], path: Path) -> None:
    parts: list[str] = []
    parts.append("% Auto-generated from raw.txt\n")
    parts.append("% Usage:\n")
    parts.append("%   \\vocabentry{word}{/ipa/ (pos)}{definition}{example}{note}\n\n")
    for e in entries:
        pron = f"/{e.ipa}/ ({e.pos})"
        parts.append("\\vocabentry{" + latex_escape(e.word) + "}\n")
        parts.append("{" + latex_escape(pron) + "}\n")
        parts.append("{" + latex_escape(e.definition_en) + "}\n")
        parts.append("{" + latex_escape(e.example_en) + "}\n")
        parts.append("{" + latex_escape(e.note_vi) + "}\n\n")
    path.write_text("".join(parts), encoding="utf-8")


def write_main_tex(author: str, title: str, topic: str, out_path: Path) -> None:
    out_path.write_text(
        "\\documentclass{forumvocab}\n\n"
        "% ============================================\n"
        "% DOCUMENT CONFIGURATION\n"
        "% ============================================\n\n"
        f"\\newcommand{{\\authorinfo}}{{{latex_escape(author)}}}\n"
        f"\\newcommand{{\\documenttitle}}{{{latex_escape(title)}}}\n"
        f"\\newcommand{{\\topictitle}}{{{latex_escape(topic)}}}\n\n"
        "\\begin{document}\n\n"
        "\\thispagestyle{firstpage}\n"
        "\\makefirstpageheader{\\authorinfo}{\\documenttitle}{\\topictitle}\n"
        "\\pagestyle{otherpages}\n\n"
        "\\begin{multicols}{2}\n"
        "\\input{data.tex}\n"
        "\\end{multicols}\n\n"
        "\\end{document}\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a vocab LaTeX project from a raw.txt file.")
    parser.add_argument("raw", type=Path, help="Path to raw.txt")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output directory to create/update")
    parser.add_argument("--name", default="educationVocab", help="Base name for the main .tex file")
    parser.add_argument("--author", default="THE FORUM CENTER", help="Header author info")
    parser.add_argument("--title", default="EDUCATION VOCABULARY", help="Header document title")
    parser.add_argument("--topic", default="TỪ VỰNG CHỦ ĐỀ: EDUCATION", help="Topic title line")
    args = parser.parse_args()

    raw_text = args.raw.read_text(encoding="utf-8").strip("\ufeff")
    if not raw_text.strip():
        raise SystemExit(f"Raw file is empty: {args.raw}")

    entries = parse_raw(raw_text)
    if not entries:
        raise SystemExit("No entries parsed. Check raw format (expected lines starting with '## **...').")

    template_dir = Path(__file__).resolve().parents[1]
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    for fname in ["forumvocab.cls", "UTM-Impact.ttf"]:
        src = template_dir / fname
        if src.exists():
            shutil.copy2(src, out_dir / fname)

    write_data_tex(entries, out_dir / "data.tex")
    write_main_tex(args.author, args.title, args.topic, out_dir / f"{args.name}.tex")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
