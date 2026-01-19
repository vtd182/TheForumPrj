#!/usr/bin/env python3
import argparse
import datetime as dt
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from generate_from_raw import Entry, latex_escape, parse_raw, write_data_tex, write_main_tex


@dataclass(frozen=True)
class Result:
    raw: Path
    topic: str
    entries: int
    out_dir: Path
    pdf: Path | None
    status: str
    message: str
    generated_at: str


def infer_topic(raw_path: Path, text: str) -> str:
    for line in text.splitlines()[:30]:
        if "chủ đề" in line.lower() and "**" in line:
            m = re.search(r"chủ đề\s+\*\*(?P<t>.+?)\*\*", line, flags=re.IGNORECASE)
            if m:
                return m.group("t").strip()
    for line in text.splitlines()[:10]:
        ln = line.strip()
        if not ln or ln == "---":
            continue
        if ln.startswith("## ") or re.match(r"^\d+\.\s*\*\*", ln) or ln.startswith("**"):
            break
        if len(ln) <= 80:
            return ln
    stem = raw_path.stem
    spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", stem).strip()
    return spaced


def infer_output_name(raw_path: Path, topic: str) -> str:
    stem = raw_path.stem
    stem_overrides = {"enviroment": "environment"}
    stem = stem_overrides.get(stem, stem)
    if stem and stem.isascii():
        base = stem[0].lower() + stem[1:]
    else:
        parts = re.findall(r"[A-Za-z0-9]+", topic)
        camel = "".join(p.capitalize() for p in parts) or "vocab"
        base = camel[0].lower() + camel[1:]
    return f"{base}Vocab"


def compile_pdf(project_dir: Path, tex_name: str) -> Path:
    subprocess.check_call(
        ["xelatex", "-interaction=nonstopmode", "-halt-on-error", f"{tex_name}.tex"],
        cwd=project_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.check_call(
        ["xelatex", "-interaction=nonstopmode", "-halt-on-error", f"{tex_name}.tex"],
        cwd=project_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    pdf = project_dir / f"{tex_name}.pdf"
    if not pdf.exists():
        raise RuntimeError(f"PDF not produced: {pdf}")
    return pdf


def write_progress(results: list[Result], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# Raw → Template Progress\n\n")
    lines.append(f"Last run: `{dt.datetime.now().isoformat(timespec='seconds')}`\n\n")
    lines.append("| Raw file | Topic | Entries | Output | PDF | Status |\n")
    lines.append("|---|---:|---:|---|---|---|\n")
    for r in sorted(results, key=lambda x: x.raw.name.lower()):
        raw = r.raw.as_posix()
        out = r.out_dir.as_posix()
        pdf = r.pdf.as_posix() if r.pdf else ""
        lines.append(
            f"| `{raw}` | {latex_escape(r.topic)} | {r.entries} | `{out}` | `{pdf}` | {r.status} |\n"
        )
    out_path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch-generate PDFs for all raw files in a directory.")
    parser.add_argument("--raw-dir", type=Path, default=Path("Vocab/raw"))
    parser.add_argument("--out-base", type=Path, default=Path("Vocab"))
    parser.add_argument("--author", default="THE FORUM CENTER - NGUYỄN HOÀNG HUY")
    parser.add_argument("--title", default="VOCABULARY ĐỘC QUYỀN")
    parser.add_argument("--compile", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--progress", type=Path, default=Path("Vocab/raw/PROGRESS.md"))
    args = parser.parse_args()

    raw_files = sorted(args.raw_dir.glob("*.txt"))
    if not raw_files:
        raise SystemExit(f"No .txt raw files found in: {args.raw_dir}")

    template_dir = Path(__file__).resolve().parents[1]
    results: list[Result] = []

    for raw_path in raw_files:
        generated_at = dt.datetime.now().isoformat(timespec="seconds")
        try:
            text = raw_path.read_text(encoding="utf-8").strip("\ufeff")
            entries: list[Entry] = parse_raw(text)
            if not entries:
                raise ValueError("No entries parsed (unsupported format?)")

            topic = infer_topic(raw_path, text)
            out_name = infer_output_name(raw_path, topic)
            out_dir = args.out_base / out_name
            out_dir.mkdir(parents=True, exist_ok=True)

            for fname in ["forumvocab.cls", "UTM-Impact.ttf"]:
                src = template_dir / fname
                if src.exists():
                    shutil.copy2(src, out_dir / fname)

            write_data_tex(entries, out_dir / "data.tex")
            topic_line = f"TỪ VỰNG CHỦ ĐỀ: {topic.upper()}"
            write_main_tex(args.author, args.title, topic_line, out_dir / f"{out_name}.tex")

            pdf_path: Path | None = None
            if args.compile:
                pdf_path = compile_pdf(out_dir, out_name)

            results.append(
                Result(
                    raw=raw_path,
                    topic=topic,
                    entries=len(entries),
                    out_dir=out_dir,
                    pdf=pdf_path,
                    status="OK",
                    message="",
                    generated_at=generated_at,
                )
            )
        except Exception as e:  # noqa: BLE001
            topic = infer_topic(raw_path, raw_path.read_text(encoding="utf-8").strip("\ufeff"))
            out_name = infer_output_name(raw_path, topic)
            results.append(
                Result(
                    raw=raw_path,
                    topic=topic,
                    entries=0,
                    out_dir=args.out_base / out_name,
                    pdf=None,
                    status="FAIL",
                    message=str(e),
                    generated_at=generated_at,
                )
            )

    write_progress(results, args.progress)

    failed = [r for r in results if r.status != "OK"]
    if failed:
        print(f"Generated with failures: {len(failed)} (see {args.progress})")
        for r in failed[:10]:
            print(f"- {r.raw.name}: {r.message}")
        return 1

    print(f"Generated {len(results)} PDFs (see {args.progress})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
