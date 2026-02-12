# Active FDO: Governance-Aware Segment Specification

**Reference Implementation for "Bridging Global Interoperability and Regional Sovereignty"**

This repository contains the reference implementation, specifications, and benchmarking tools for the Active FDO (A-FDO) protocol extension. It enables machine-actionable governance at the transport segment level for Digital Object Interface Protocol (DOIP) networks.

---

## Repository Structure

```
FDO_Project/
├── benchmarks/          # Performance evaluation tools and results
│   ├── plots/           # Generated plots (PDFs)
│   ├── results/         # Raw data (JSON/TXT)
│   └── ...              # Plot generation scripts
├── docs/                # Documentation
│   ├── paper/           # LaTeX source and academic papers
│   └── spec/            # Formal specifications (Header, Policy Dictionary)
├── scripts/             # Simulation and utility scripts
│   └── run_simulation.py # Main MCP-based simulation entry point
├── spec/                # DOIP Segment Schemas (JSON)
└── src/                 # Core implementation source code
    ├── fdo_gate.py      # FDO Gate Logic (Compliance Filter)
    ├── mcp_server.py    # MCP Server Implementation
    └── doip_segments/   # Python class definitions for DOIP segments
```

## Getting Started

### Prerequisites

*   Python 3.8+
*   Dependencies listed in `requirements.txt`

### Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Simulation

The core demonstration uses the Model Context Protocol (MCP) to simulate an Active FDO Gate filtering traffic based on governance policies.

```bash
python scripts/run_simulation.py
```

This script will:
1.  Initialize an MCP server instance (`src/mcp_server.py`).
2.  Simulate legitimate traffic (Policy: Public).
3.  Simulate a tampering attack (Man-in-the-Middle).
4.  Simulate a policy violation (Unauthorized Access).
5.  Output the defense results for each scenario.

## Key Features

1.  **O(1) MsBV Lookup**: Constant-time policy enforcement using Multistate Bit Vectors.
2.  **Folded Checksum**: Integrity verification for governance headers.
3.  **Governance-Aware**: Supports granular data sovereignty rules (e.g., GDPR, China DSL).

## Citation

Please refer to the `docs/paper` directory for the associated academic publication: *"Bridging Global Interoperability and Regional Sovereignty: The Active FDO Protocol Extension."*

**Lead Researcher:** Bin Zhang (GitHub: joy7758)
**Affiliation:** FDO Standards Architecture Group
