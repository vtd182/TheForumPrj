#!/usr/bin/env bash
set -euo pipefail

# Convert a chuyenDe Markdown file (same structure as DOCX pipeline) into PDF via LaTeX templates.
#
# Requirements:
# - pandoc
# - xelatex (TeX Live / MacTeX)
#
# Usage:
#   bash chuyenDe/latex/md_to_pdf.sh input.md output.pdf [Reading|Writing]

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 input.md output.pdf [Reading|Writing]" >&2
  exit 1
fi

in="$1"
out="$2"
skill_arg="${3:-}"

chuyende_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build_dir="${chuyende_root}/RW/build-mdpdf"
filter="${chuyende_root}/latex/pandoc/cd-forum-latex.lua"

in_abs="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "${in}")"
out_abs="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "${out}")"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc not found (macOS: brew install pandoc)." >&2
  exit 1
fi
if ! command -v xelatex >/dev/null 2>&1; then
  echo "xelatex not found (install TeX Live / MacTeX)." >&2
  exit 1
fi

if [[ ! -f "${in_abs}" ]]; then
  echo "Not found: ${in_abs}" >&2
  exit 1
fi

meta_skill="$(python3 - "${in_abs}" <<'PY'
import re,sys
p=sys.argv[1]
text=open(p,'r',encoding='utf-8').read().splitlines()
if not text or text[0].strip()!='---':
    print('')
    raise SystemExit(0)
# collect yaml frontmatter lines until next ---
y=[]
for line in text[1:]:
    if line.strip()=='---':
        break
    y.append(line)
yaml='\n'.join(y)

def find_key(key):
    m=re.search(r'^%s\s*:\s*(.*)$'%re.escape(key), yaml, flags=re.M)
    if not m:
        return ''
    v=m.group(1).strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v=v[1:-1]
    return v

skill=find_key('skill')
print(skill)
PY
)"

skill="${skill_arg:-${meta_skill}}"
if [[ "${skill}" != "Reading" && "${skill}" != "Writing" ]]; then
  echo "Cannot infer skill. Pass Reading/Writing as arg3 or set frontmatter: skill: Reading|Writing" >&2
  exit 1
fi

mkdir -p "${build_dir}"
rm -f "${build_dir}/content.tex" "${build_dir}/main.tex" "${build_dir}/main.pdf" "${build_dir}/main.aux" "${build_dir}/main.log" >/dev/null 2>&1 || true

skill_upper="$(printf "%s" "${skill}" | tr '[:lower:]' '[:upper:]')"
doctype="TÀI LIỆU CHUYÊN ĐỀ ${skill_upper}"
class_rel=""
if [[ "${skill}" == "Reading" ]]; then
  class_rel="../templateReading/cdreading"
else
  class_rel="../templateWriting/cdwriting"
fi

pandoc "${in_abs}" \
  -t latex \
  --from markdown+raw_attribute+fenced_divs+bracketed_spans+pipe_tables \
  --lua-filter="${filter}" \
  -o "${build_dir}/content.tex"

cat > "${build_dir}/main.tex" <<EOF
\\documentclass{${class_rel}}

\\newcommand{\\authorinfo}{THE FORUM CENTER - NGUYỄN HOÀNG HUY}
\\newcommand{\\documenttitle}{${doctype}}

\\begin{document}
\\thispagestyle{firstpage}
\\makeworkshopheader{\\authorinfo}{\\documenttitle}{}
\\pagestyle{otherpages}

\\input{content.tex}

\\end{document}
EOF

(cd "${build_dir}" && xelatex -interaction=nonstopmode main.tex >/dev/null)
(cd "${build_dir}" && xelatex -interaction=nonstopmode main.tex >/dev/null)

mkdir -p "$(dirname "${out_abs}")"
cp "${build_dir}/main.pdf" "${out_abs}"
echo "${out_abs}"
