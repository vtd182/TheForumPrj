#!/usr/bin/env bash
set -euo pipefail

# Regenerate LS (Listening/Speaking) DOCX from existing Markdown only.
#
# Default input layout:
#   chuyenDe/LS/md/raw47/<Skill>/Level<level>/W<week>.md
# Output:
#   chuyenDe/LS/docx/raw47/<Skill>/Level<level>/W<week>.docx
#
# Usage:
#   bash chuyenDe/scripts/ls_md_to_word.sh [md_root] [out_root]

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc not found. Install it first (macOS: brew install pandoc)." >&2
  exit 1
fi

md_root="${1:-${repo_root}/chuyenDe/LS/md/raw47}"
out_root="${2:-${repo_root}/chuyenDe/LS/docx/raw47}"
converter="${repo_root}/chuyenDe/word/pandoc/md_to_docx.sh"
ref_l="${repo_root}/chuyenDe/word/reference-listening.docx"
ref_s="${repo_root}/chuyenDe/word/reference-speaking.docx"
postprocess="${repo_root}/chuyenDe/scripts/postprocess_docx_tables.py"

if [[ ! -d "${md_root}" ]]; then
  echo "Missing Markdown dir: ${md_root}" >&2
  exit 1
fi

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

  if [[ "${skill}" == "Listening" ]]; then
    bash "${converter}" "${md}" "${out}" "${ref_l}"
  elif [[ "${skill}" == "Speaking" ]]; then
    bash "${converter}" "${md}" "${out}" "${ref_s}"
  else
    echo "Skip (unknown skill folder): ${md#${repo_root}/}" >&2
    continue
  fi

  python3 "${postprocess}" "${out}"
  echo "${out#${repo_root}/}"
done < <(find "${md_root}" -type f -name '*.md' -print0)

