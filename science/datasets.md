# DATASETS SPECIFICATION & LEAKAGE AUDIT

This document specifies all training corpora, independent validation resources, and standardized test benchmarks relevant to the ProteinSolver research extension.

---

## 1. ProteinSolver Training Corpus (Gene3D)
- **Source:** Strokach et al. (*Cell Systems* 2020), derived from Gene3D domain annotations mapped to PDB structures.
- **Scale:** **72,464,122 sequence/adjacency-matrix pairs**.
- **Superfamily Partition:**
  - **1,373 total Gene3D superfamilies**.
  - **Training:** 1,029 superfamilies.
  - **Validation:** 172 superfamilies.
  - **Test:** 172 superfamilies.
- **Evidentiary Note on Schema:** Source inspection of `proteinsolver/datasets/protein.py` conclusively confirms that the on-disk serialization format is Apache Parquet (`.snappy.parquet`) with table columns `['sequence', 'residue_idx_1_corrected', 'residue_idx_2_corrected', 'distances']`, normalized into a 2D edge attribute tensor via continuous linear scalers $((d - 6) / 12, (j - i) / 68.1319)$. See `research/proteinsolver_data_schema.md`.
- **Usage in This Project:** We do **not** re-download the 72M training pairs. We leverage the pretrained weights produced from this corpus.

---

## 2. Independent Validation Benchmarks (Strokach et al. 2020)
*These datasets are strictly independent validation resources and are NOT part of the Gene3D training corpus.*

### A. ProTherm (Thermodynamic Stability of Point Mutations)
- **Description:** Curated collection of experimentally determined changes in folding free energy ($\Delta \Delta G$) upon single amino acid mutations across wild-type proteins.
- **Task:** Zero-shot correlation between model score difference $\Delta S = S(s_{\text{mut}}) - S(s_{\text{wt}})$ and experimental $\Delta \Delta G$.
- **Role in Project:** Serves as an auxiliary proxy metric to determine whether ProteinSolver retains biophysical stability sensitivity that ProteinMPNN might undervalue.

### B. Rocklin Miniprotein Dataset (Rocklin et al., Science 2017)
- **Description:** High-throughput protease sensitivity assay data for >40,000 *de novo* designed miniprotein sequences (folding stability scores) across 4 topologies: $\alpha\alpha\alpha$, $\beta\alpha\beta\beta$, $\alpha\beta\beta\alpha$, $\beta\beta\alpha\beta\beta$.
- **Task:** Classify stable vs. unstable computational designs.
- **Role in Project:** Independent validation benchmark for assessing stability discrimination on small, rigid de novo topologies.

---

## 3. Standard Modern Inverse Folding Benchmarks

### A. CATH 4.2 / 4.3 (Standard Topological Split)
- **Source:** Ingraham et al. (NeurIPS 2019), Dauparas et al. (Science 2022), Gao et al. (ICLR 2023).
- **Split:** Partitioned strictly by CATH topology code (no homologous architectures shared between train and test):
  - **Train:** ~18,024 chains.
  - **Validation:** ~608 chains.
  - **Test:** ~1,120 chains (CATH 4.2 test split).
- **Standard Metrics:** Native Sequence Recovery (AAR), Perplexity.

### B. TS50 / TS500 Benchmarks
- **Source:** Standard test sets of high-resolution, non-redundant PDB crystal structures curated to have $<30\%$ pairwise sequence identity to training sets.
- **Usage:** Fast, lightweight evaluation of sequence recovery and inference latency.

### C. CASP15 Targets
- **Source:** Evaluated in ProteinInvBench (Gao et al. 2023).
- **Usage:** Tests generalizability on recent, challenging natural protein folds.

### D. De Novo Backbones (RFdiffusion Test Suite)
- **Source:** Watson et al. (*Nature* 2023).
- **Usage:** Evaluates design capability on non-natural, computationally hallucinated backbones where no native wild-type sequence exists (evaluation strictly via self-consistency scRMSD and pLDDT).

---

## 4. Data Leakage Prevention Rules
1. **Homology Exclusion:** When testing on CATH 4.2 or TS50, verify that test targets do not belong to the 1,029 Gene3D training superfamilies of ProteinSolver.
2. **Structural Overlap Checks:** Run TM-align between test backbones and ProteinSolver training domain exemplars if ambiguous.
3. **No Retrospective Tuning:** All hyperparameters ($T^*, \lambda^*, \gamma^*$) must be selected strictly on the frozen development manifest (`data/manifests/development_20_cath42.txt`, canonical LF SHA-256: `47ab5fec66017b455f7eabee143dc83e99ec740640e945ed96752abb59483069`, $N_{\text{dev}}=20$ from Ingraham/Dauparas CATH 4.2 validation split) maximizing scalar objective $J$ and frozen prior to any test set evaluation (PREREGISTRATION Section 8), never on the final test set.
4. **TS50 Manifest Pre-Test Dependency:** The TS50 exact target manifest is a pre-test dependency that must be frozen prior to TS50 benchmark execution. Development tuning (E1) is not blocked by TS50 manifest preparation.


