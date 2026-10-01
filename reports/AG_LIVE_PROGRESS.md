# Antigravity Live Progress

**Task:** PROTEINSOLVER - FINAL R1 SOURCE ADJUDICATION, CONTRADICTION ELIMINATION & HARD R2 GATE
**Agent:** Lead Scientific Reproducibility Engineer + Evidence-Governance Agent
**Started:** 2026-10-01T10:12:30+05:30
**Updated:** 2026-10-01T10:29:00+05:30
**Status:** COMPLETE / R2_READY

---

## Metric Tracking
- **Completed stages:** [1/7], [2/7], [3/7], [4/7], [5/7], [6/7], [7/7]
- **Candidate contradictions:** 17
- **Confirmed contradictions:** 12
- **Fixed:** 12
- **Unresolved:** 0
- **Blocked:** 0
- **Current action:** Final hard R2 release gate complete; repository clean; declared R2_READY.
- **Elapsed runtime:** 16m 30s

---

## Stages Progress

- [x] **[1/7] Safety + evidence inventory:** Verified exact working directory `D:\Projects\Protein Design`, branch `main`, parent commit `d961ef0b865f03d05a3df339b9f84b8f20c9ea56`, HEAD `98bc6d00a6b286563ea024cc229199db843179a3`. Verified external repositories clean and untouched (`external/proteinsolver-original` at `69ef0965...`, `D:\Projects\ProteinSolver` at `58255bc6...`).
- [x] **[2/7] Primary-paper adjudication:** Reconciled final published *Cell Systems* paper (11(4): 402–411.e4, Oct 2020; DOI: 10.1016/j.cels.2020.08.016; PMID: 32971019) via CrossRef and preprint text. Adjudicated Figure 1 strictly as panels 1A, 1B, 1C; Figure 2A as accuracy trajectory; Figure 2B–2F panel semantics; Figure 2G–2N exact panel map; and Supplementary Figures S3–S5 target folds. Identified and corrected biological identities (1N5U = Human Serum Albumin domain 3; 4BEU = Alanine racemase; 4UNU = Immunoglobulin lambda variable; 4Z8J = SNX27 PDZ domain).
- [x] **[3/7] Historical implementation adjudication:** Inspected historical upstream source code (`proteinsolver/datasets/protein.py`, `proteinsolver/models/proteinnet.py`, `proteinsolver/nn/edge_conv_mod.py`). Proved that graph self-loops are filtered (`row_index != col_index`), asserted absent, and stripped in `forward` via `remove_self_loops`. Proved that edge tensor entering `embed_adj` has strictly 2 channels (`adj_input_size = 2`), consisting of normalized distance and normalized sequence separation; raw distance is not fed as a 3rd channel. Established that 68.1319 is a fixed historical scaling constant. Documented batch sizes: 4 for primary GCN training, 1 for validation/eval.
- [x] **[4/7] Experimental/provenance adjudication:** Cryptographically hashed all checkpoint files (`e53-s1952148-d93703104.state` size 2,278,071 bytes, SHA-256: `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727`); excised hallucinated hash `c830026e...`. Reconciled EXP005 ProTherm metrics ($N=3,471$, differentiated raw vs normalized REU vs Cartesian ddG). Reconciled EXP006 Rocklin stability metrics, preserving EEHEE Round 4 negative correlation exception. Calibrated EXP007 BeStSel $p > 0.05$ as failure to detect a difference under tested conditions (not structural equivalence). Bounded EXP008 as single-target MAP diagnostic fixture with unbenchmarked full regeneration cost.
- [x] **[5/7] Global current-authority contradiction sweep:** Audited Tier-B documents for stale overclaims, phantom panels, and contradictory texts. Replaced all occurrences of `c830026e...`, `498-507`, `serum response factor`, 3 edge channels, and native self-loops in current authority.
- [x] **[6/7] Verification + bounded repair:** Verified governance preflight CLI and pytest suite (81/81 passed). Ingested durable lesson L-026. Verified external repositories remain untouched.
- [x] **[7/7] Final hard R2 gate:** Evaluated release criteria A through Y. Verified cleanroom boundaries. Rendered final binary release decision: R2_READY.
