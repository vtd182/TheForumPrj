#!/bin/bash
# ============================================================
# compile.sh — Biên dịch tài liệu Math-2026
# Sử dụng: ./compile.sh
# ============================================================

set -e

export PATH="/Library/TeX/texbin:$PATH"

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "🔨 Pass 1/2: Compiling main.tex..."
mkdir -p build
xelatex -interaction=nonstopmode -output-directory=build main.tex > /dev/null 2>&1

echo "🔨 Pass 2/2: Resolving TOC & cross-references..."
xelatex -interaction=nonstopmode -output-directory=build main.tex > /dev/null 2>&1

# Count pages
PAGES=$(grep -c "Output written" build/main.log 2>/dev/null || echo "?")
echo ""
echo "✅ Done! PDF: build/main.pdf"
echo "📄 Pages: check build/main.pdf"

# Check for errors
ERRORS=$(grep -c "^!" build/main.log 2>/dev/null || echo "0")
if [ "$ERRORS" -gt 0 ]; then
  echo "⚠️  $ERRORS error(s) found. Check build/main.log"
else
  echo "🎉 0 errors"
fi

# Open PDF on macOS
open build/main.pdf 2>/dev/null || true
