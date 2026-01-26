#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 input_docx_root output_pdf_root" >&2
  exit 1
fi

in_root="$1"
out_root="$2"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ascript="${repo_root}/chuyenDe/scripts/docx_to_pdf_word.applescript"

if [[ ! -d "/Applications/Microsoft Word.app" ]]; then
  echo "Microsoft Word.app not found in /Applications." >&2
  exit 1
fi

in_root="$(cd "$in_root" && pwd)"
mkdir -p "$out_root"
out_root="$(cd "$out_root" && pwd)"

args=()
while IFS= read -r -d '' docx; do
  rel="${docx#${in_root}/}"
  subdir="$(dirname "$rel")"
  base="$(basename "$docx" .docx)"
  out_dir="${out_root}/${subdir}"
  mkdir -p "$out_dir"
  args+=("$docx" "${out_dir}/${base}.pdf")
done < <(find "$in_root" -type f -name '*.docx' -print0)

if [[ ${#args[@]} -eq 0 ]]; then
  echo "No .docx found under $in_root" >&2
  exit 1
fi

osascript "$ascript" "${args[@]}"
echo "Wrote PDFs under: $out_root"

