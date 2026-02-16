# GLOBECOM-Workshop Submission Artifact

## Overview
This artifact contains the LaTeX source code and associated figures for the paper "Active Governance Header: A Novel Approach for Data Sovereignty in Fair Digital Object Architecture", submitted to the GLOBECOM workshop.

## Directory Structure
- `main.tex`: The main LaTeX source file.
- `refs.bib`: Bibliography file containing references.
- `figures/`: Directory containing figures used in the paper.
  - `loss_curve.pdf`: RLCP Loss Convergence.
  - `autonomous_performance.pdf`: Latency vs Policy Scale.
- `scripts/`: Directory containing build scripts.
  - `build.sh`: Script to compile the paper.

## Build Instructions
To compile the paper, run the following command from the `paper_globecom` directory:
```bash
./scripts/build.sh
```

## Dependencies
- `pdflatex`
- `bibtex`
- `IEEEtran` document class

## Content Origin
The content is derived from the internal documentation and reports of the Active FDO project, specifically:
- `docs/paper/merged_paper.tex`
- `docs/paper/Defense_Robustness_Report.md`
- `docs/paper/Defense_Test_Report.md`
