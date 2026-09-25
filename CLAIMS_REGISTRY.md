# CLAIMS REGISTRY

This registry tracks the formal status of all scientific claims, architectural assumptions, and empirical assertions in the project. Claims are strictly categorized to prevent hypotheses or inferences from silently hardening into accepted facts.

---

## 1. VERIFIED CLAIMS (`[VERIFIED]`)
*Claims supported by direct inspection of primary literature, official source code, or published mathematical proofs.*

| ID | Claim Statement | Primary Source / Evidence Base | Date Verified |
|---|---|---|---|
| **V-01** | ProteinSolver uses a residual Graph Neural Network architecture with 4 residual blocks. | Strokach et al., *Cell Systems* (2020), DOI: 10.1016/j.cels.2020.08.016; `ostrokach/proteinsolver` repo. | 2026-09-24 |
| **V-02** | ProteinSolver node and edge embedding dimensions are both 128. | Strokach et al., *Cell Systems* (2020). | 2026-09-24 |
| **V-03** | ProteinSolver protein graph nodes represent amino acids or masked/unknown residues; edges represent spatial interactions. | Strokach et al., *Cell Systems* (2020). | 2026-09-24 |
| **V-04** | ProteinSolver edge features include shortest Cartesian distance (cutoff 12 Å) and sequence separation \|i - j\|. | Strokach et al., *Cell Systems* (2020). | 2026-09-24 |
| **V-05** | ProteinSolver training randomly masks approximately 50% of residues and optimizes cross-entropy loss to predict masked residues. | Strokach et al., *Cell Systems* (2020). | 2026-09-24 |
| **V-06** | ProteinSolver's training corpus contains 72,464,122 sequence/adjacency-matrix pairs across 1,373 Gene3D superfamilies. | Strokach et al., *Cell Systems* (2020). | 2026-09-24 |
| **V-07** | ProteinSolver's superfamily dataset split consists of 1,029 training, 172 validation, and 172 test superfamilies. | Strokach et al., *Cell Systems* (2020). | 2026-09-24 |
| **V-08** | ProTherm and Rocklin-related datasets are independent validation resources, not interchangeable with the main training corpus. | Strokach et al., *Cell Systems* (2020); Rocklin et al., *Science* (2017). | 2026-09-24 |
| **V-09** | ProteinMPNN uses an autoregressive message-passing neural network with random decoding order, conditioning on 3D backbone coordinates (N, CA, C, O) via invariant geometric features. | Dauparas et al., *Science* (2022), DOI: 10.1126/science.add2187. | 2026-09-24 |
| **V-10** | ProteinMPNN achieves approximately 51–52% native sequence recovery on standard CATH 4.2 test benchmarks, outperforming standalone ProteinSolver (~32–35%). | Dauparas et al. (2022); ProteinInvBench (Gao et al., 2023). | 2026-09-24 |
| **V-11** | ProteinSolver dataset storage is Apache Parquet (`.snappy.parquet`) with table columns `['sequence', 'residue_idx_1_corrected', 'residue_idx_2_corrected', 'distances']`, normalized via linear scaling $((d-6)/12, (j-i)/68.1319)$, not HDF5. | Verified in `proteinsolver/datasets/protein.py` (lines 188–246). | 2026-09-24 |
| **V-12** | Original historical `ProteinNet` instantiates (567,060 params), executes forward passes on CUDA, and loads published checkpoint `e53-s1952148-d93703104.state` under `strict=True` with 0 missing and 0 unexpected keys after layer prefix normalization (`graph_conv_0` $\to$ `graph_conv_1`, `graph_conv.0..2` $\to$ `graph_conv_2..4`). | Empirically verified in `test_original_execution.py` and `reports/PROTEINSOLVER_PROVENANCE_MANIFEST.md`. | 2026-09-24 |
| **V-13** | On target structure 1n5uA03 (92 AA), valid all-masked inverse-folding sequence recovery using the original repository's CSP unmasking algorithm yields 41.30% (38/92 matches) in 1.77s. This is classified as a *single-target all-masked inverse-folding integration result*, not general benchmark accuracy. | Empirically verified in `test_original_execution.py`, EXP000, and EXP001. | 2026-09-24 |
| **V-14** | In the tested all-masked mask-invariance experiment (EXP004, `data.x = 20`, `data.y = None`), changing hidden/native labels produced a maximum absolute logit difference of 0.00000000e+00. Passing `data.y` causes `protein_design.py` to copy reference labels via `strategy="ref"`, producing an informational leak. | Empirically verified in `experiments/EXP004_MASK_INVARIANCE/`. | 2026-09-24 |
| **V-15** | On the tested target 1n5uA03, feature pipeline tensors (`x`, `edge_index`, `edge_attr`, `batch`) extracted via the original repo pipeline (`ProteinData` $\to$ `row_to_data` $\to$ `transform_edge_attr` $\to$ `Batch`) are numerically identical (`max diff: 0.0`) to the cleanroom extractor `extract_protein_graph`. General equivalence across all structures: NOT VERIFIED. | Empirically verified in feature pipeline audit. | 2026-09-24 |

---

## 2. SUPPORTED BUT NOT FULLY VERIFIABLE (`[NOT VERIFIABLE]`)

| ID | Statement | Context / Evidence Base | Status |
|---|---|---|---|
| **NV-01** | Target structure 1n5uA03 training set membership in the full 72M Gene3D corpus. | Author verified `"1.10.246.10" in cath_ids` evaluated to `False` in `notebooks/16_protein_analysis_experimental.ipynb`. However, because the full 72M training Parquet corpus is stored on an external cluster and not bundled in git, exact training membership cannot be independently verified from accessible metadata without downloading the corpus. | **NOT VERIFIABLE FROM ACCESSIBLE METADATA** |

---

## 3. SUPPORTED BUT NEEDS PRIMARY-SOURCE / CODE CHECK (`[SUPPORTED-NEEDS-CHECK]`)
*Claims widely cited or asserted in recent preprints/papers that require direct verification in our codebase or against specific dataset files.*

| ID | Claim Statement | Cited In | Required Action |
|---|---|---|---|
| **S-01** | *(RESOLVED & MOVED TO V-11)* Dataset schema verified as Apache Parquet. | `proteinsolver/datasets/protein.py` | Complete (2026-09-24). |
| **S-02** | PiFold achieves 51.66% sequence recovery on CATH 4.2 in a single forward pass (non-autoregressive). | Gao et al., *ICLR* (2023). | Verify benchmark evaluation code and test split alignment. |
| **S-03** | Combining ProteinMPNN with language model logits (IgLM) via simple inference-time logit addition improves native sequence recovery in CDR loops. | Shuai et al., *bioRxiv* (2023). | Check whether this logit combination generalizes to non-antibody globular proteins. |

---

## 4. INFERENCES (`[INFERENCE]`)
*Logical deductions derived from verified properties, pending direct experimental demonstration.*

| ID | Inference Statement | Underlying Verified Facts | Status |
|---|---|---|---|
| **I-01** | Because ProteinSolver relies only on pairwise distance cutoffs (<12 Å) and sequence separation without local coordinate frame orientations (which ProteinMPNN uses), its probability distribution may be less sensitive to minor backbone torsional perturbations. | Facts V-04 and V-09. | Plausible inference; requires sensitivity analysis. |
| **I-02** | High sequence recovery does not necessarily maximize functional library diversity; standard low-temperature sampling from ProteinMPNN creates narrow sequence clusters. | Literature consensus (ProteinZero 2024; Dauparas et al. 2022). | Supported by literature, pending quantification. |
| **I-03** | Naive linear averaging of ProteinSolver and ProteinMPNN probabilities may degrade design quality if ProteinSolver's error rate dominates. | Fact V-10 (recovery gap of 33% vs 51%). | High probability risk; motivates non-linear or multi-objective Pareto selection over naive ensembling. |

---

## 5. OPEN HYPOTHESES (`[HYPOTHESIS]`)
*Core research questions that form the provisional investigation.*

| ID | Hypothesis Statement | Test / Validation Mechanism | Current Status |
|---|---|---|---|
| **H-01** | Information from ProteinSolver can complement modern structure-conditioned sequence-design models (e.g., ProteinMPNN). | Evaluate whether ProteinSolver scores correlate with orthogonal biophysical traits (e.g., core packing, stability) not captured by ProteinMPNN perplexity. | **UNTESTED HYPOTHESIS** |
| **H-02** | A diversity-aware, multi-objective candidate selection framework can exploit model complementarity to improve the quality-diversity trade-off of designed protein sequences. | Measure Pareto hypervolume of (scRMSD, scTM, sequence diversity) across E0–E5 experimental matrices. | **UNTESTED HYPOTHESIS** |
| **H-03** | Rescoring and reranking ProteinMPNN-generated candidates using ProteinSolver CSP constraint-satisfaction metrics enriches for candidates with higher AlphaFold self-consistency. | Self-consistency evaluation using AlphaFold2 / ESMFold on filtered vs unfiltered pools. | **UNTESTED HYPOTHESIS** |

---

## 6. REJECTED CLAIMS (`[REJECTED]`)
*Ideas, claims, or hypotheses explicitly disproven or ruled out by literature audit or empirical test.*

| ID | Rejected Statement | Reason for Rejection | Date Rejected |
|---|---|---|---|
| **R-01** | ProteinSolver is competitive with ProteinMPNN as a standalone sequence design engine on modern benchmarks. | Refuted by ProteinInvBench (Gao et al., 2023) and Dauparas et al. (2022); ProteinSolver has significantly lower sequence recovery (~33% vs ~51%). | 2026-09-24 |
| **R-02** | The combination of sequence generation + AlphaFold2 filtering is a novel contribution. | Refuted by Watson et al. (Nature 2023, RFdiffusion) and standard Baker Lab pipelines where ProteinMPNN + AF2 is the established baseline. | 2026-09-24 |
| **R-03** | Training a new 70M+ parameter foundation model from scratch is required for this research extension. | Unfeasible given project compute budget; scientifically unjustified when pretrained checkpoints and inference-time ensembling/selection can address the research question directly. | 2026-09-24 |
