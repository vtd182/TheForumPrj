#!/usr/bin/env bash
set -euo pipefail

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc not found. Install it first (macOS: brew install pandoc)." >&2
  exit 1
fi

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 input.md output.docx [reference.docx]" >&2
  exit 1
fi

in="$1"
out="$2"
ref_override="${3:-}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
filter="${repo_root}/chuyenDe/word/pandoc/cd-forum.lua"

if [[ -n "$ref_override" ]]; then
  ref="$ref_override"
else
  ref="${repo_root}/chuyenDe/word/reference.docx"
fi

if [[ ! -f "$ref" ]]; then
  echo "Missing reference docx: $ref" >&2
  echo "Generate it via: python3 ${repo_root}/chuyenDe/word/build_reference_docx.py" >&2
  exit 1
fi

pandoc "$in" \
  -o "$out" \
  --from markdown+raw_attribute+fenced_divs+bracketed_spans \
  --reference-doc "$ref" \
  --lua-filter "$filter"
