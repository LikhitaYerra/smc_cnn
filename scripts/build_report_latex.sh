#!/usr/bin/env bash
# Build AI Clinic research report from LaTeX
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_DIR="$ROOT/docs/report"
OUTPUT="$ROOT/docs/AI_Clinic_Research_Report.pdf"

cd "$ROOT"

# Ensure figures exist
if [ ! -f docs/assets/figures/fig01_architecture.png ]; then
  echo "Generating report figures..."
  python3 scripts/generate_report_figures.py
fi

# Ensure logo exists
if [ ! -f docs/assets/aivancity_logo.png ]; then
  mkdir -p docs/assets
  curl -sL "https://upload.wikimedia.org/wikipedia/fr/7/76/Logo-aivancity.png" \
    -o docs/assets/aivancity_logo.png
fi

cd "$REPORT_DIR"

echo "Compiling LaTeX report..."
pdflatex -interaction=nonstopmode main.tex > /dev/null
bibtex main > /dev/null 2>&1 || true
pdflatex -interaction=nonstopmode main.tex > /dev/null
pdflatex -interaction=nonstopmode main.tex > /dev/null

cp main.pdf "$OUTPUT"

# Cleanup aux files
rm -f main.aux main.bbl main.blg main.log main.out

echo "Report built: $OUTPUT"
ls -lh "$OUTPUT"
