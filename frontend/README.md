# FUSE: Protein Design & Verification Workbench (Group G1588)

A production-grade scientific web workbench for structure-conditioned protein sequence design combining **ProteinSolver** constraint satisfaction graph neural network priors with **ProteinMPNN** autoregressive sequence generation, audited under **Amendment A3** frozen scientific constraints.

---

## 🏛️ Architecture & Core Views

The application implements all 7 core workbench views:

1. **Research Dashboard (`/`)**
   - E0 milestone progress tracker (`E0-RUNTIME: COMPLETE`, `E0-SCIENTIFIC-HARDENING: COMPLETE`, `E0-EQUIVALENCE-STATUS: FUNCTIONALLY REPRODUCED`).
   - Amendment A3 frozen parameters card.
   - Verification gates overview (Gates 0 through 4).
   - System telemetry and historical baseline audit flags.

2. **Design Studio (`/design-studio`)**
   - Benchmark structure selector (CATH 4.2 cohort targets including Ubiquitin `1UBQ`, Tenascin `1tenA00`, Cro `2croA00`, Calmodulin `3clnA00`, and audited `1n5uA03`).
   - Protocol selector (All-Masked Inverse Folding, Hotspot Redesign, Core Repacking).
   - Amendment A3 lock toggle ($T_{\text{mpnn}}=0.1$, $T_{\text{ps}}=1.0$, $\lambda=0.5$, $\gamma=0.0$).
   - Real-time 3D target backbone preview and sequence inspector.
   - Co-design execution initiation.

3. **Workflow Designer (`/workflow`)**
   - Interactive Directed Acyclic Graph (DAG) visualizing the full multi-stage co-design pipeline.
   - Node-level inspection with mathematical formulations, parameters, tensor shapes, and verification evidence.

4. **Job Monitor (`/jobs`)**
   - Real-time execution queue and progress tracking.
   - Interactive execution holds (pause/resume pipeline at critical decision gates).
   - Live log streaming with severity filters (`INFO`, `WARN`, `METRIC`, `GATE`).
   - GPU telemetry with clear differentiation between live hardware metrics and prototype simulation.

5. **Candidate Explorer (`/candidates`)**
   - Filterable, sortable scientific candidate data grid.
   - Metrics: Sequence Recovery Rate %, Oracle $\text{scRMSD}$ ($\text{\AA}$), Scaled $\text{pLDDT}$, Perplexity, and Hybrid Score.
   - Multi-attribute threshold filters ($\text{scRMSD} \le 2.0\text{ \AA}$, $\text{pLDDT} \ge 80.0$).
   - Sequence mutation difference viewer against wild-type.
   - One-click batch exports to FASTA and CSV formats.

6. **Structure & Validation Workbench (`/structure`)**
   - High-craft interactive 3D molecular viewer with WebGL and Mol* integration.
   - AlphaFold / ESMFold per-residue $\text{pLDDT}$ confidence color spectrum:
     - $\ge 90$: Deep Blue (`#0053D6`, Very High)
     - $70 - 90$: Cyan (`#65CBF3`, Confident)
     - $50 - 70$: Yellow (`#FFDB13`, Low)
     - $< 50$: Orange (`#FF7D45`, Very Low)
   - Representations: Cartoon Ribbon, Ball-and-Stick, Spacefill Spheres, Surface Envelope.
   - Double-binding 2-way synchronization: clicking any residue in the sequence inspector highlights and pins that exact residue in 3D; clicking in 3D highlights the residue in the sequence strip.
   - Direct integration link to Mol* sidecar viewer (`sidecar://structural-biology/biomolecular_structure_viewer/ui.html`).
   - PDB coordinate download.

7. **Reports & Provenance (`/reports`)**
   - Cryptographic Provenance Manifest viewer (Manifest ID, Commit hash, SHA-256 root hash).
   - Milestone E0 verification audit records (strict checkpoint load, zero missing/unexpected keys, 567,060 parameters, EXP004 mask-invariance diff = 0.0).
   - Amendment A3 compliance certificate.
   - Exportable JSON and Markdown manifests.
   - Reproducibility CLI commands.

---

## 🔒 Strict Anti-Fabrication & Scientific Parameter Governance

- **Frozen Parameters (Amendment A3):**
  - $\text{ProteinMPNN Temperature } T = 0.1$
  - $\text{ProteinSolver Temperature } T = 1.0$
  - $\text{Hybrid Weight } \lambda = 0.5$
  - $\text{Diversity Penalty } \gamma = 0.0$
  - $\text{Benchmark Set: } 20\text{ CATH 4.2 Targets}$
  - $\text{Self-Consistency Gate: } \text{scRMSD} \le 2.0\text{ \AA}, \text{Scaled pLDDT} \ge 80.0$
  - $\text{Checkpoint Parameters: } 567,060\text{ params (strict=True)}$

- **Anti-Fabrication & Truthfulness Safeguards:**
  - When the backend API is disconnected, the system automatically displays an unmissable banner indicating **PROTOTYPE / OFFLINE MODE**.
  - All simulated or demo actions are explicitly tagged with `[SIMULATED_DEMO]` or `DEMO` badges.
  - Audited historical baseline data (such as the 41.30% recovery on `1n5uA03` from the E0 baseline audit) is preserved and tagged with `AUDIT`.
  - Quarantine notice prominently flagged on `1n5uA03` due to unverified training set membership in the 72M corpus, preventing data leakage in benchmark claims.

---

## 🚀 Development & Build

```bash
# Install dependencies
npm install

# Run unit & integration tests
npm test

# Run TypeScript checks & linting
npm run lint

# Build production bundle
npm run build

# Start dev server
npm run dev
```
