#!/bin/bash
cd "$(dirname "$0")/.."
set -e
echo "Building GLOBECOM paper..."
rm -f main.aux main.bbl main.blg main.log main.out main.pdf bibtex.log
echo "Running pdflatex (1/3)..."
pdflatex -interaction=nonstopmode main.tex > main.log 2>&1 || { echo "pdflatex failed"; tail -n 60 main.log; exit 1; }
echo "Running bibtex..."
bibtex main > bibtex.log 2>&1 || { echo "bibtex failed"; tail -n 60 bibtex.log; exit 1; }
echo "Running pdflatex (2/3)..."
pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1
echo "Running pdflatex (3/3)..."
pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1
echo "Build successful. PDF is at $(pwd)/main.pdf"
if command -v pdfinfo >/dev/null 2>&1; then
  pdfinfo main.pdf | grep Pages || true
fi
