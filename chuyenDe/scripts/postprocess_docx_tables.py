#!/usr/bin/env python3
from __future__ import annotations

import argparse
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import NamedTemporaryFile


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _w(tag: str) -> str:
    return f"{{{NS['w']}}}{tag}"


def _get_attr(el: ET.Element, name: str) -> str | None:
    return el.get(f"{{{NS['w']}}}{name}")


def _set_attr(el: ET.Element, name: str, value: str) -> None:
    el.set(f"{{{NS['w']}}}{name}", value)


def _is_vocab_table(tbl: ET.Element) -> bool:
    tbl_pr = tbl.find("./w:tblPr", NS)
    if tbl_pr is None:
        return False
    tbl_style = tbl_pr.find("./w:tblStyle", NS)
    if tbl_style is None:
        return False
    return _get_attr(tbl_style, "val") == "CDVocabTable"

def _is_option_table(tbl: ET.Element) -> bool:
    tbl_pr = tbl.find("./w:tblPr", NS)
    if tbl_pr is None:
        return False
    tbl_style = tbl_pr.find("./w:tblStyle", NS)
    if tbl_style is None:
        return False
    return _get_attr(tbl_style, "val") == "CDOptionTable"

def _is_answer_table(tbl: ET.Element) -> bool:
    tbl_pr = tbl.find("./w:tblPr", NS)
    if tbl_pr is None:
        return False
    tbl_style = tbl_pr.find("./w:tblStyle", NS)
    if tbl_style is None:
        return False
    return _get_attr(tbl_style, "val") == "CDAnswerTable"

def _is_choice_table(tbl: ET.Element) -> bool:
    tbl_pr = tbl.find("./w:tblPr", NS)
    if tbl_pr is None:
        return False
    tbl_style = tbl_pr.find("./w:tblStyle", NS)
    if tbl_style is None:
        return False
    return _get_attr(tbl_style, "val") == "CDChoiceTable"

def _is_answer_key_table(tbl: ET.Element) -> bool:
    tbl_pr = tbl.find("./w:tblPr", NS)
    if tbl_pr is None:
        return False
    tbl_style = tbl_pr.find("./w:tblStyle", NS)
    if tbl_style is None:
        return False
    return _get_attr(tbl_style, "val") == "CDAnswerKeyTable"


def _is_reading_vocab_table(tbl: ET.Element) -> bool:
    tbl_pr = tbl.find("./w:tblPr", NS)
    if tbl_pr is None:
        return False
    tbl_style = tbl_pr.find("./w:tblStyle", NS)
    if tbl_style is None:
        return False
    return _get_attr(tbl_style, "val") == "CDReadingVocabTable"


def _count_columns(tbl: ET.Element) -> int:
    grid = tbl.find("./w:tblGrid", NS)
    if grid is not None:
        cols = grid.findall("./w:gridCol", NS)
        if cols:
            return len(cols)
    # Fallback: count cells in first row
    tr = tbl.find("./w:tr", NS)
    if tr is not None:
        tcs = tr.findall("./w:tc", NS)
        if tcs:
            return len(tcs)
    return 0


def _ensure_tbl_layout_autofit(tbl: ET.Element) -> None:
    tbl_pr = tbl.find("./w:tblPr", NS)
    if tbl_pr is None:
        return
    layout = tbl_pr.find("./w:tblLayout", NS)
    if layout is None:
        layout = ET.Element(_w("tblLayout"))
        tbl_pr.append(layout)
    _set_attr(layout, "type", "autofit")

def _ensure_tbl_indent(tbl: ET.Element, *, indent_twips: int) -> None:
    tbl_pr = tbl.find("./w:tblPr", NS)
    if tbl_pr is None:
        return
    ind = tbl_pr.find("./w:tblInd", NS)
    if ind is None:
        ind = ET.Element(_w("tblInd"))
        tbl_pr.append(ind)
    _set_attr(ind, "type", "dxa")
    _set_attr(ind, "w", str(indent_twips))


def _ensure_tbl_width_dxa(tbl: ET.Element, *, width_twips: int) -> None:
    tbl_pr = tbl.find("./w:tblPr", NS)
    if tbl_pr is None:
        return
    tblw = tbl_pr.find("./w:tblW", NS)
    if tblw is None:
        tblw = ET.Element(_w("tblW"))
        tbl_pr.append(tblw)
    _set_attr(tblw, "type", "dxa")
    _set_attr(tblw, "w", str(width_twips))


def _ensure_tbl_centered(tbl: ET.Element) -> None:
    tbl_pr = tbl.find("./w:tblPr", NS)
    if tbl_pr is None:
        return
    jc = tbl_pr.find("./w:jc", NS)
    if jc is None:
        jc = ET.Element(_w("jc"))
        tbl_pr.append(jc)
    _set_attr(jc, "val", "center")

    # Ensure no indentation forces left alignment.
    ind = tbl_pr.find("./w:tblInd", NS)
    if ind is not None:
        tbl_pr.remove(ind)


def _set_grid_widths(tbl: ET.Element, *, content_width_twips: int) -> None:
    grid = tbl.find("./w:tblGrid", NS)
    if grid is None:
        return
    cols = grid.findall("./w:gridCol", NS)
    if not cols:
        return
    n = len(cols)
    base = content_width_twips // n
    remainder = content_width_twips - base * n
    for i, col in enumerate(cols):
        w = base + (remainder if i == n - 1 else 0)
        _set_attr(col, "w", str(w))

def _set_grid_widths_weighted(tbl: ET.Element, *, widths: list[int]) -> None:
    grid = tbl.find("./w:tblGrid", NS)
    if grid is None:
        return
    cols = grid.findall("./w:gridCol", NS)
    if not cols:
        return
    if len(cols) != len(widths):
        return
    for col, w_val in zip(cols, widths, strict=False):
        _set_attr(col, "w", str(w_val))


def _postprocess_document_xml(xml_bytes: bytes) -> bytes:
    root = ET.fromstring(xml_bytes)

    # Letter page width 12240 twips; margins left/right 1134 twips (2cm) in our template.
    content_width_twips = 12240 - 1134 - 1134

    indent_twips = 240  # ~2 small spaces visually

    for tbl in root.findall(".//w:tbl", NS):
        if _is_vocab_table(tbl):
            _ensure_tbl_layout_autofit(tbl)
            _ensure_tbl_indent(tbl, indent_twips=indent_twips)
            usable_width = content_width_twips - indent_twips
            _ensure_tbl_width_dxa(tbl, width_twips=usable_width)
            _set_grid_widths(tbl, content_width_twips=usable_width)
            continue
        if _is_answer_table(tbl):
            _ensure_tbl_layout_autofit(tbl)
            _ensure_tbl_indent(tbl, indent_twips=indent_twips)
            usable_width = content_width_twips - indent_twips
            _ensure_tbl_width_dxa(tbl, width_twips=usable_width)
            # 3 columns: narrow / wide / narrow.
            w1 = int(usable_width * 0.14)
            w3 = int(usable_width * 0.14)
            w2 = max(0, usable_width - w1 - w3)
            _set_grid_widths_weighted(tbl, widths=[w1, w2, w3])
            continue
        if _is_choice_table(tbl):
            _ensure_tbl_layout_autofit(tbl)
            _ensure_tbl_indent(tbl, indent_twips=indent_twips)
            usable_width = content_width_twips - indent_twips
            _ensure_tbl_width_dxa(tbl, width_twips=usable_width)
            # 2 columns: narrow / wide.
            w1 = int(usable_width * 0.18)
            w2 = max(0, usable_width - w1)
            _set_grid_widths_weighted(tbl, widths=[w1, w2])
            continue
        if _is_answer_key_table(tbl):
            _ensure_tbl_layout_autofit(tbl)
            _ensure_tbl_indent(tbl, indent_twips=indent_twips)
            usable_width = content_width_twips - indent_twips
            _ensure_tbl_width_dxa(tbl, width_twips=usable_width)
            w1 = int(usable_width * 0.18)
            w2 = max(0, usable_width - w1)
            _set_grid_widths_weighted(tbl, widths=[w1, w2])
            continue
        if _is_reading_vocab_table(tbl):
            _ensure_tbl_layout_autofit(tbl)
            _ensure_tbl_indent(tbl, indent_twips=indent_twips)
            usable_width = content_width_twips - indent_twips
            _ensure_tbl_width_dxa(tbl, width_twips=usable_width)
            w1 = int(usable_width * 0.24)
            w2 = int(usable_width * 0.14)
            w4 = int(usable_width * 0.22)
            w3 = max(0, usable_width - w1 - w2 - w4)
            _set_grid_widths_weighted(tbl, widths=[w1, w2, w3, w4])
            continue
        if _is_option_table(tbl):
            _ensure_tbl_centered(tbl)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def rewrite_docx_in_place(docx_path: Path) -> None:
    with zipfile.ZipFile(docx_path, "r") as zin:
        entries = zin.infolist()
        document_xml = zin.read("word/document.xml")
        new_document_xml = _postprocess_document_xml(document_xml)

        with NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp_path = Path(tmp.name)

        try:
            with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                for info in entries:
                    data = zin.read(info.filename)
                    if info.filename == "word/document.xml":
                        data = new_document_xml
                    zout.writestr(info.filename, data)
            tmp_path.replace(docx_path)
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Postprocess DOCX tables (vocab) to be full-width within margins.")
    ap.add_argument("docx", nargs="+", help="Path(s) to .docx files")
    args = ap.parse_args()

    for p in args.docx:
        docx_path = Path(p)
        if not docx_path.exists():
            raise SystemExit(f"Not found: {docx_path}")
        rewrite_docx_in_place(docx_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
