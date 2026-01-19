#!/usr/bin/env python3
import argparse
import re
import subprocess
import tempfile
from pathlib import Path


def _render_ppm(pdf_path: Path, page: int, out_path: Path, dpi: int) -> None:
    subprocess.check_call(
        [
            "gs",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=ppmraw",
            f"-r{dpi}",
            f"-dFirstPage={page}",
            f"-dLastPage={page}",
            f"-sOutputFile={str(out_path)}",
            str(pdf_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _read_ppm_rgb(path: Path):
    with path.open("rb") as f:
        if f.readline().strip() != b"P6":
            raise ValueError(f"{path} is not a binary PPM (P6)")

        tokens = []
        while len(tokens) < 3:
            line = f.readline()
            if not line:
                raise ValueError(f"{path} has an incomplete header")
            if line.startswith(b"#") or not line.strip():
                continue
            tokens += line.split()

        width, height, maxv = int(tokens[0]), int(tokens[1]), int(tokens[2])
        if maxv != 255:
            raise ValueError(f"{path} has maxval={maxv}, expected 255")

        data = f.read(width * height * 3)
        if len(data) != width * height * 3:
            raise ValueError(f"{path} has truncated pixel data")

        return width, height, data


def _mean_redness(width: int, rgb: bytes, x0: int, x1: int, y0: int, y1: int) -> float:
    x0 = max(0, min(width, x0))
    x1 = max(0, min(width, x1))
    if x1 <= x0 or y1 <= y0:
        return 0.0

    row_bytes = width * 3
    total_r = total_g = total_b = 0
    n = 0
    for y in range(y0, y1):
        off = y * row_bytes + x0 * 3
        for _x in range(x0, x1):
            r = rgb[off]
            g = rgb[off + 1]
            b = rgb[off + 2]
            total_r += r
            total_g += g
            total_b += b
            n += 1
            off += 3

    r = total_r / n
    g = total_g / n
    b = total_b / n
    return r - (g + b) / 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Checks that watermark intensity is consistent between page 1 and page 2."
    )
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument(
        "--max-ratio",
        type=float,
        default=1.2,
        help="Fail if page1/page2 redness ratio exceeds this.",
    )
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF not found: {args.pdf}")

    with tempfile.TemporaryDirectory(prefix="forum_wm_check_") as td:
        tdir = Path(td)
        p1 = tdir / "p1.ppm"
        p2 = tdir / "p2.ppm"
        _render_ppm(args.pdf, 1, p1, args.dpi)
        _render_ppm(args.pdf, 2, p2, args.dpi)

        w1, h1, d1 = _read_ppm_rgb(p1)
        w2, h2, d2 = _read_ppm_rgb(p2)
        if (w1, h1) != (w2, h2):
            raise SystemExit(f"Rendered pages have different sizes: {(w1, h1)} vs {(w2, h2)}")

        # Sample a region likely to include watermark pixels while avoiding headers/footers.
        # These coordinates are tuned to the template's typical content area.
        x0, x1, y0, y1 = 560, 680, 780, 1120
        r1 = _mean_redness(w1, d1, x0, x1, y0, y1)
        r2 = _mean_redness(w2, d2, x0, x1, y0, y1)

        ratio = (r1 / r2) if r2 > 1e-6 else float("inf")
        print(f"page1_redness={r1:.2f} page2_redness={r2:.2f} ratio={ratio:.2f}")

        if ratio > args.max_ratio:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

