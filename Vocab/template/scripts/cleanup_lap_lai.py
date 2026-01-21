#!/usr/bin/env python3
import argparse
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path

from generate_from_raw import ENTRY_RE_H2, ENTRY_RE_LIST


LAP_LAI_RE = re.compile(r"lặp\s+lại", re.IGNORECASE)
LAP_LAI_PAREN_RE = re.compile(r"\s*\([^()]*lặp\s+lại[^()]*\)\.?\s*", re.IGNORECASE)
PLACEHOLDER_ONLY_RE = re.compile(r"^\(\s*lặp\s+lại.*\)\.?\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class Change:
    path: Path
    line_no: int
    word: str
    before: str
    after: str


def iter_entry_lines(path: Path) -> list[tuple[int, re.Match[str], str]]:
    text = path.read_text(encoding="utf-8").strip("\ufeff")
    out: list[tuple[int, re.Match[str], str]] = []
    for i, line in enumerate(text.splitlines(), 1):
        ln = line.strip()
        m = ENTRY_RE_H2.match(ln) or ENTRY_RE_LIST.match(ln)
        if not m:
            continue
        out.append((i, m, line))
    return out


def get_entry_word(m: re.Match[str]) -> str:
    return m.group("word").strip()


def get_entry_rest(m: re.Match[str]) -> str:
    return m.group("rest").strip()


def strip_lap_lai(rest: str) -> str:
    cleaned = LAP_LAI_PAREN_RE.sub(" ", rest)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.replace(" .", ".").replace(" ,", ",")
    cleaned = re.sub(r"\s+\.", ".", cleaned)
    return cleaned


def has_non_lap_lai_parens(rest: str) -> bool:
    for p in re.findall(r"\([^()]*\)", rest):
        if not LAP_LAI_RE.search(p):
            return True
    return False


def build_best_rest_index(raw_files: list[Path], manual_rest: dict[str, str]) -> dict[str, str]:
    best: dict[str, str] = {}
    for path in raw_files:
        for _, m, _line in iter_entry_lines(path):
            word = get_entry_word(m)
            rest = get_entry_rest(m)
            if PLACEHOLDER_ONLY_RE.match(rest):
                continue
            if LAP_LAI_RE.search(rest):
                rest = strip_lap_lai(rest)
            if not rest or LAP_LAI_RE.search(rest):
                continue
            best.setdefault(word.casefold(), rest)

    for k, v in manual_rest.items():
        best.setdefault(k.casefold(), v)
    return best


def rewrite_file(
    path: Path, best_rest: dict[str, str], apply: bool
) -> tuple[list[Change], bool]:
    text = path.read_text(encoding="utf-8").strip("\ufeff")
    lines = text.splitlines(keepends=True)

    changes: list[Change] = []
    changed = False

    for idx, line in enumerate(lines):
        ln = line.strip()
        m = ENTRY_RE_H2.match(ln) or ENTRY_RE_LIST.match(ln)
        if not m:
            continue

        word = get_entry_word(m)
        rest = get_entry_rest(m)
        if not LAP_LAI_RE.search(rest):
            continue

        before = line.rstrip("\n")
        new_rest: str | None = None

        if PLACEHOLDER_ONLY_RE.match(rest):
            new_rest = best_rest.get(word.casefold())
            if not new_rest:
                raise SystemExit(
                    f"Missing replacement for placeholder-only entry: {path}:{idx+1} word={word!r}"
                )
        else:
            if has_non_lap_lai_parens(rest):
                new_rest = strip_lap_lai(rest)
            else:
                # If the only note is '(Lặp lại ...)', try to replace with a better rest
                # that includes a Vietnamese note. Fallback to stripping the marker.
                new_rest = best_rest.get(word.casefold()) or strip_lap_lai(rest)

        # Normalize spacing & ensure no lingering marker.
        new_rest = re.sub(r"\s+", " ", (new_rest or "").strip())
        if LAP_LAI_RE.search(new_rest):
            raise SystemExit(f"Cleanup left 'lặp lại' behind: {path}:{idx+1}")

        after = re.sub(r"(?P<prefix>^(?:\d+\.\s*)?\*\*.+?/\s*:\*\*\s+).*$", r"\g<prefix>" + new_rest, ln)
        if after == ln:
            # safer rebuild using match groups
            prefix = ln[: ln.find(m.group("rest"))]
            after = prefix + new_rest

        lines[idx] = after + ("\n" if line.endswith("\n") else "")
        changes.append(Change(path=path, line_no=idx + 1, word=word, before=before, after=lines[idx].rstrip("\n")))
        changed = True

    if changed and apply:
        path.write_text("".join(lines), encoding="utf-8")
    return changes, changed


def write_report(changes: list[Change], out_path: Path) -> None:
    now = dt.datetime.now().isoformat(timespec="seconds")
    lines: list[str] = []
    lines.append("# Vocab Raw \"Lặp lại\" Cleanup Report\n\n")
    lines.append(f"Last run: `{now}`\n\n")
    lines.append("Rule: remove '(Lặp lại ...)' placeholders/markers from entry meanings.\n\n")
    by_file: dict[str, list[Change]] = {}
    for c in changes:
        by_file.setdefault(c.path.as_posix(), []).append(c)

    lines.append("| File | Changes |\n")
    lines.append("|---|---:|\n")
    for fname in sorted(by_file.keys(), key=str.casefold):
        lines.append(f"| `{fname}` | {len(by_file[fname])} |\n")

    lines.append("\n## Details\n")
    for fname in sorted(by_file.keys(), key=str.casefold):
        lines.append(f"\n### `{fname}`\n")
        for c in by_file[fname]:
            lines.append(f"- `{c.path.as_posix()}:{c.line_no}` `{c.word}`\n")

    out_path.write_text("".join(lines), encoding="utf-8")


def manual_replacements() -> dict[str, str]:
    # Used for entries that had only '(Lặp lại ...)' as their meaning.
    return {
        "Acceleration": "The increase in speed or rate of change of velocity. (Đây là một danh từ dùng để chỉ sự tăng tốc.)",
        "Aerodynamics": "The study of how air moves and how it affects objects moving through it, especially aircraft. (Đây là một danh từ dùng để chỉ ngành khí động học.)",
        "Astrobiology": "The study of the origin, evolution, and possibility of life in the universe. (Đây là một danh từ dùng để chỉ ngành sinh học vũ trụ.)",
        "Ballast": "Heavy material used to provide stability, especially gravel under railway tracks or weight in a ship. (Đây là một danh từ dùng để chỉ vật dằn/đá ballast giúp ổn định.)",
        "Bay": "A broad inlet of the sea where the land curves inward. (Đây là một danh từ dùng để chỉ vịnh.)",
        "Berth": "A ship's assigned place at a dock; also a place to sleep on a ship or train. (Đây là một danh từ/động từ dùng để chỉ chỗ neo đậu hoặc đưa tàu vào bến.)",
        "Bioethics": "The study of ethical issues raised by advances in biology and medicine. (Đây là một danh từ dùng để chỉ đạo đức sinh học.)",
        "Braking": "The action of slowing down or stopping a vehicle using brakes. (Đây là một danh từ dùng để chỉ việc phanh/giảm tốc.)",
        "Breakwater": "A barrier built to protect a shore or harbor from the force of waves. (Đây là một danh từ dùng để chỉ đê chắn sóng.)",
        "Bypass": "A road that goes around a town or congested area; to go around or avoid something. (Đây là một danh từ/động từ dùng để chỉ đường tránh hoặc tránh đi vòng.)",
        "Canal": "An artificial waterway built to allow boats or ships to travel inland. (Đây là một danh từ dùng để chỉ kênh đào/kênh nhân tạo.)",
        "Carriage": "A vehicle or compartment for carrying passengers, especially a railway carriage. (Đây là một danh từ dùng để chỉ toa xe/hành khách hoặc khoang tàu.)",
        "Chassis": "The frame of a vehicle, onto which the body and other parts are attached. (Đây là một danh từ dùng để chỉ khung gầm.)",
        "Cockpit": "The compartment in an aircraft where the pilot sits and controls the plane. (Đây là một danh từ dùng để chỉ buồng lái.)",
        "Control tower": "A tall building at an airport from which air traffic controllers monitor and guide aircraft. (Đây là một danh từ dùng để chỉ tháp điều khiển không lưu.)",
        "Deck": "A floor-like platform on a ship; also a level of a bus or other vehicle. (Đây là một danh từ dùng để chỉ boong tàu/tầng của phương tiện.)",
        "Dredging": "The process of removing mud, sand, or sediment from the bottom of a river, harbor, or channel to deepen it. (Đây là một danh từ dùng để chỉ hoạt động nạo vét.)",
        "Fleet": "A group of ships or a collection of vehicles operated by a company or organization. (Đây là một danh từ dùng để chỉ hạm đội/đội xe.)",
        "Freight": "Goods transported in bulk by truck, train, ship, or aircraft. (Đây là một danh từ dùng để chỉ hàng hóa vận chuyển.)",
        "Fuselage": "The main body of an aircraft, to which the wings and tail are attached. (Đây là một danh từ dùng để chỉ thân máy bay.)",
        "Gauge": "A measuring device; also the distance between rails on a railway; to measure or estimate. (Đây là một danh từ/động từ dùng để chỉ thước đo/khổ ray hoặc đo lường.)",
        "Hangar": "A large building where aircraft are stored and maintained. (Đây là một danh từ dùng để chỉ nhà chứa máy bay.)",
        "Inertia": "The tendency of an object to resist changes in its motion (to stay at rest or keep moving). (Đây là một danh từ dùng để chỉ quán tính.)",
        "Jetty": "A structure extending into the water to protect a harbor or provide a place for boats to dock. (Đây là một danh từ dùng để chỉ cầu cảng/đê chắn nhỏ vươn ra biển.)",
        "Junction": "A place where roads or railway lines meet, cross, or diverge. (Đây là một danh từ dùng để chỉ nút giao.)",
        "Liability": "Legal responsibility for something; in finance, a company's debts or obligations. (Đây là một danh từ dùng để chỉ trách nhiệm pháp lý hoặc khoản nợ phải trả.)",
        "Light rail": "An urban rail transport system using relatively light trains, often with street-level sections. (Đây là một danh từ dùng để chỉ tàu điện nhẹ.)",
        "Lock": "A gated section of a canal used to raise or lower boats between different water levels; to secure something. (Đây là một danh từ/động từ dùng để chỉ âu tàu/khóa.)",
        "Locomotive": "The engine that pulls a train; relating to movement or propulsion. (Đây là một danh từ/tính từ dùng để chỉ đầu máy xe lửa hoặc thuộc về chuyển động.)",
        "Melody": "A sequence of musical notes that form the main tune of a song or piece of music. (Đây là một danh từ dùng để chỉ giai điệu.)",
        "Obsession": "A persistent, often uncontrollable, preoccupation with an idea, feeling, or person. (Đây là một danh từ dùng để chỉ sự ám ảnh/nỗi ám ảnh.)",
        "Orbit": "To move in a curved path around a planet, moon, or star. (Đây là một động từ dùng để chỉ việc quay quanh quỹ đạo.)",
        "Particulate": "Tiny particles, especially those suspended in air; relating to particles. (Đây là một danh từ/tính từ dùng để chỉ hạt bụi mịn hoặc dạng hạt.)",
        "Payload": "The cargo carried by a vehicle, especially by a spacecraft or rocket. (Đây là một danh từ dùng để chỉ tải trọng hữu ích.)",
        "Pier": "A platform on pillars projecting from the shore into the water, used for docking or walking. (Đây là một danh từ dùng để chỉ cầu tàu/bến tàu.)",
        "Quality": "The standard of something as measured against other things; a distinctive attribute. (Đây là một danh từ dùng để chỉ chất lượng/phẩm chất.)",
        "Quay": "A stone or concrete platform beside water where ships load and unload. (Đây là một danh từ dùng để chỉ cầu cảng/bờ kè bốc dỡ.)",
        "Rolling stock": "Railway vehicles, such as locomotives, carriages, and wagons. (Đây là một danh từ dùng để chỉ đoàn toa xe/thiết bị phương tiện đường sắt.)",
        "Runway": "A strip of land at an airport on which aircraft take off and land. (Đây là một danh từ dùng để chỉ đường băng.)",
        "Siding": "A short track beside the main railway line used for passing or storing trains. (Đây là một danh từ dùng để chỉ đường ray nhánh.)",
        "Sleepers": "Beams (wooden or concrete) laid across a railway track to support the rails. (Đây là một danh từ dùng để chỉ tà vẹt đường sắt.)",
        "Subway": "An underground railway system, especially in a city. (Đây là một danh từ dùng để chỉ tàu điện ngầm.)",
        "Suspension": "The system of springs and shock absorbers that connects a vehicle to its wheels. (Đây là một danh từ dùng để chỉ hệ thống treo/giảm xóc.)",
        "Tarmac": "A paved surface, especially an area at an airport where aircraft park or move. (Đây là một danh từ dùng để chỉ mặt đường nhựa/khu sân đỗ máy bay.)",
        "Taxiway": "A path on an airport along which aircraft taxi between the runway and the terminal. (Đây là một danh từ dùng để chỉ đường lăn.)",
        "Telemetry": "The automatic measurement and wireless transmission of data from remote sources. (Đây là một danh từ dùng để chỉ hệ thống đo xa/truyền dữ liệu từ xa.)",
        "Trajectory": "The path followed by a moving object through the air or in space. (Đây là một danh từ dùng để chỉ quỹ đạo/đường bay.)",
        "Viaduct": "A long bridge carrying a road or railway across a valley, river, or other obstacle. (Đây là một danh từ dùng để chỉ cầu cạn.)",
        "Wagon": "A railway vehicle used for transporting goods; a large vehicle for carrying goods. (Đây là một danh từ dùng để chỉ toa hàng/xe chở hàng.)",
        "Wharf": "A structure built along the shore where ships can dock to load and unload. (Đây là một danh từ dùng để chỉ cầu cảng/bến cảng.)",
        "Wing": "The flat structure on an aircraft that produces lift and enables it to fly. (Đây là một danh từ dùng để chỉ cánh máy bay.)",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove '(Lặp lại ...)' markers from vocab raw files.")
    parser.add_argument("--raw-dir", type=Path, default=Path("Vocab/raw"))
    parser.add_argument("--report", type=Path, default=Path("Vocab/raw/LAP_LAI_CLEANUP_REPORT.md"))
    parser.add_argument("--apply", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    raw_files = sorted(args.raw_dir.glob("*.txt"), key=lambda p: p.name.casefold())
    if not raw_files:
        raise SystemExit(f"No .txt files found in: {args.raw_dir}")

    manual_rest = manual_replacements()
    best_rest = build_best_rest_index(raw_files, manual_rest)

    all_changes: list[Change] = []
    changed_files = 0
    for path in raw_files:
        changes, changed = rewrite_file(path, best_rest=best_rest, apply=args.apply)
        all_changes.extend(changes)
        if changed:
            changed_files += 1

    write_report(all_changes, args.report)
    print(f"Processed {len(raw_files)} files; changed {changed_files}; fixes {len(all_changes)}. Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

