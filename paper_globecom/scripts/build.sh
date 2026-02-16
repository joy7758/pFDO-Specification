#!/bin/bash
# Navigate to the parent directory of the script (i.e., paper_globecom)
cd "$(dirname "$0")/.."

# Compile the LaTeX document
pdflatex main
bibtex main
pdflatex main
pdflatex main
