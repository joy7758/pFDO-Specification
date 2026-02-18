# GLOBECOM-Workshop Submission Artifact

## Overview
This artifact contains the LaTeX source code and associated figures for the paper "PHY-Level Deterministic Control: Overlap Execution within IEEE 802.3dj RS-FEC Decode Window", submitted to the GLOBECOM workshop.

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
- `pdflatex` (TeX Live or MacTeX)
- `bibtex`
- `IEEEtran` document class
- `poppler` (optional, for page count check via `pdfinfo`)

## Content Origin
The content is derived from the internal documentation and reports of the Active FDO project.
All data figures are generated from the project's simulation environment.

## Compliance Check
- [x] Page limit: $\le$ 6 pages.
- [x] References: IEEE/IETF standard sources used.
- [x] Formatting: IEEEtran conference.
