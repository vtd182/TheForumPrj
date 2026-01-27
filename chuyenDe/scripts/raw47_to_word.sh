#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc not found. Install it first (macOS: brew install pandoc)." >&2
  exit 1
fi

python3 "${repo_root}/chuyenDe/word/build_reference_docx.py" >/dev/null
python3 "${repo_root}/chuyenDe/scripts/raw47_to_markdown.py"

md_root="${repo_root}/chuyenDe/RW/md/raw47"
out_root="${repo_root}/chuyenDe/RW/docx/raw47"
converter="${repo_root}/chuyenDe/word/pandoc/md_to_docx.sh"
ref_w="${repo_root}/chuyenDe/word/reference-writing.docx"
ref_r="${repo_root}/chuyenDe/word/reference-reading.docx"
postprocess="${repo_root}/chuyenDe/scripts/postprocess_docx_tables.py"

rm -rf "${out_root}"
mkdir -p "${out_root}"

while IFS= read -r -d '' md; do
  rel="${md#${md_root}/}"
  skill="${rel%%/*}"
  level_week="${rel#*/}"
  level="${level_week%%/*}"
  week_file="${level_week#*/}"
  week="${week_file%.md}"

  out_dir="${out_root}/${skill}/${level}"
  mkdir -p "${out_dir}"
  out="${out_dir}/${week}.docx"

  if [[ "${skill}" == "Writing" ]]; then
    bash "${converter}" "${md}" "${out}" "${ref_w}"
  else
    bash "${converter}" "${md}" "${out}" "${ref_r}"
  fi
  python3 "${postprocess}" "${out}"
  echo "${out#${repo_root}/}"
done < <(find "${md_root}" -type f -name '*.md' -print0)
