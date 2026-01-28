#!/usr/bin/env bash
set -euo pipefail

# Regenerate LS (Listening/Speaking) PDFs from existing Markdown only.
#
# Default input layout:
#   chuyenDe/LS/md/raw47/<Skill>/Level<level>/W<week>.md
# Output:
#   chuyenDe/LS/pdf/output/<Skill>-Level<level>-W<week>.pdf
#
# Usage:
#   bash chuyenDe/scripts/ls_md_to_pdf.sh [md_root] [out_dir]

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
builder="${repo_root}/chuyenDe/latex/md_to_pdf.sh"

md_root="${1:-${repo_root}/chuyenDe/LS/md/raw47}"
out_dir="${2:-${repo_root}/chuyenDe/LS/pdf/output}"

if [[ ! -d "${md_root}" ]]; then
  echo "Missing Markdown dir: ${md_root}" >&2
  exit 1
fi

mkdir -p "${out_dir}"
rm -f "${out_dir}"/*.pdf >/dev/null 2>&1 || true

while IFS= read -r -d '' md; do
  rel="${md#${md_root}/}"
  skill="${rel%%/*}"
  level_week="${rel#*/}"
  level="${level_week%%/*}"
  week_file="${level_week#*/}"
  week="${week_file%.md}"

  if [[ "${skill}" != "Listening" && "${skill}" != "Speaking" ]]; then
    echo "Skip (unknown skill folder): ${md#${repo_root}/}" >&2
    continue
  fi

  out="${out_dir}/${skill}-${level}-${week}.pdf"
  bash "${builder}" "${md}" "${out}" "${skill}" >/dev/null
  echo "${out#${repo_root}/}"
done < <(find "${md_root}" -type f -name '*.md' -print0)

