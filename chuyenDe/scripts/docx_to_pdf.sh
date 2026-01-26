#!/usr/bin/env bash
set -euo pipefail

if ! command -v soffice >/dev/null 2>&1; then
  echo "soffice not found. Install LibreOffice first." >&2
  exit 1
fi

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 input_docx_root output_pdf_root" >&2
  exit 1
fi

in_root="$1"
out_root="$2"

in_root="$(cd "$in_root" && pwd)"
mkdir -p "$out_root"
out_root="$(cd "$out_root" && pwd)"

tmp_base="$(mktemp -d)"
trap 'rm -rf "$tmp_base"' EXIT

while IFS= read -r -d '' docx; do
  rel="${docx#${in_root}/}"
  subdir="$(dirname "$rel")"
  base="$(basename "$docx" .docx)"

  out_dir="${out_root}/${subdir}"
  mkdir -p "$out_dir"

  tmp_out="${tmp_base}/${subdir}"
  mkdir -p "$tmp_out"

  # LibreOffice always writes into outdir with same basename.
  soffice --headless --nologo --nolockcheck --nodefault --nofirststartwizard \
    --convert-to pdf --outdir "$tmp_out" "$docx" >/dev/null

  if [[ ! -f "${tmp_out}/${base}.pdf" ]]; then
    echo "Failed to convert: ${docx}" >&2
    exit 1
  fi
  mv -f "${tmp_out}/${base}.pdf" "${out_dir}/${base}.pdf"
  echo "${out_dir#${out_root}/}/${base}.pdf"
done < <(find "$in_root" -type f -name '*.docx' -print0)

