#!/usr/bin/env python3
import argparse
import datetime as dt
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from generate_from_raw import ENTRY_RE_H2, ENTRY_RE_LIST


@dataclass(frozen=True)
class FileStats:
    path: Path
    total_entries: int
    unique_entries: int
    removed_duplicates: int
    duplicates: Counter[str]


def find_entry_word(line: str) -> str | None:
    ln = line.strip()
    m = ENTRY_RE_H2.match(ln) or ENTRY_RE_LIST.match(ln)
    if not m:
        return None
    return m.group("word").strip()


def dedup_file(path: Path, apply: bool) -> FileStats:
    text = path.read_text(encoding="utf-8").strip("\ufeff")
    lines = text.splitlines(keepends=True)

    entry_starts: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        word = find_entry_word(line)
        if word:
            entry_starts.append((idx, word))

    if not entry_starts:
        return FileStats(path=path, total_entries=0, unique_entries=0, removed_duplicates=0, duplicates=Counter())

    preamble = lines[: entry_starts[0][0]]
    starts_only = [i for i, _ in entry_starts]

    seen: set[str] = set()
    kept_blocks: list[list[str]] = []
    duplicates: Counter[str] = Counter()

    for j, (start_idx, word) in enumerate(entry_starts):
        end_idx = starts_only[j + 1] if j + 1 < len(starts_only) else len(lines)
        block = lines[start_idx:end_idx]
        key = word.casefold()
        if key in seen:
            duplicates[word] += 1
            continue
        seen.add(key)
        kept_blocks.append(block)

    new_lines: list[str] = []
    new_lines.extend(preamble)
    for b in kept_blocks:
        new_lines.extend(b)

    total_entries = len(entry_starts)
    unique_entries = len(kept_blocks)
    removed = total_entries - unique_entries

    if apply and removed > 0:
        path.write_text("".join(new_lines), encoding="utf-8")

    return FileStats(
        path=path,
        total_entries=total_entries,
        unique_entries=unique_entries,
        removed_duplicates=removed,
        duplicates=duplicates,
    )


def write_report(stats: list[FileStats], out_path: Path) -> None:
    now = dt.datetime.now().isoformat(timespec="seconds")
    lines: list[str] = []
    lines.append("# Vocab Raw Dedup Report\n\n")
    lines.append(f"Last run: `{now}`\n\n")
    lines.append("Rule: de-duplicate repeated `word` entries within each file (keep the first occurrence).\n\n")
    lines.append("| File | Total entries | Unique entries | Removed duplicates |\n")
    lines.append("|---|---:|---:|---:|\n")
    for s in sorted(stats, key=lambda x: x.path.name.casefold()):
        lines.append(f"| `{s.path.as_posix()}` | {s.total_entries} | {s.unique_entries} | {s.removed_duplicates} |\n")

    lines.append("\n## Duplicates Detail\n")
    for s in sorted(stats, key=lambda x: x.path.name.casefold()):
        if not s.duplicates:
            continue
        lines.append(f"\n### `{s.path.as_posix()}`\n")
        lines.append("| Word | Extra occurrences |\n")
        lines.append("|---|---:|\n")
        for word, cnt in s.duplicates.most_common():
            lines.append(f"| {word} | {cnt} |\n")

    out_path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="De-duplicate repeated vocab entries in raw .txt files.")
    parser.add_argument("--raw-dir", type=Path, default=Path("Vocab/raw"))
    parser.add_argument("--report", type=Path, default=Path("Vocab/raw/DEDUP_REPORT.md"))
    parser.add_argument("--apply", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    raw_files = sorted(args.raw_dir.glob("*.txt"), key=lambda p: p.name.casefold())
    if not raw_files:
        raise SystemExit(f"No .txt files found in: {args.raw_dir}")

    stats: list[FileStats] = []
    for p in raw_files:
        stats.append(dedup_file(p, apply=args.apply))

    write_report(stats, args.report)

    changed = sum(1 for s in stats if s.removed_duplicates)
    removed = sum(s.removed_duplicates for s in stats)
    print(f"Processed {len(stats)} files; changed {changed}; removed duplicates {removed}. Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

