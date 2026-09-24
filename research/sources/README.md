# RESEARCH SOURCES & DATA REGISTRY

This directory documents external repositories, databases, web servers, and source repositories referenced by the project.

## 1. Primary Code Repositories
- **ProteinSolver:** [https://github.com/ostrokach/proteinsolver](https://github.com/ostrokach/proteinsolver)
  - Primary author: Alexey Strokach (Kim Lab, University of Toronto)
  - License: MIT
  - Key assets: Pretrained model weights (`protein_solver_model.pth`), PyTorch Geometric data loaders.
- **ProteinMPNN:** [https://github.com/dauparas/ProteinMPNN](https://github.com/dauparas/ProteinMPNN)
  - Primary author: Justas Dauparas (Baker Lab, University of Washington / IPD)
  - License: MIT
  - Key assets: Pretrained model weights (vanilla, soluble, CA-only), autoregressive sampling scripts.
- **ProteinInvBench / OpenCPD:** [https://github.com/A4Bio/OpenCPD](https://github.com/A4Bio/OpenCPD)
  - Primary author: Zhangyang Gao, Stan Z. Li (A4Bio / Westlake University)
  - License: Apache-2.0
  - Key assets: Standardized implementations of 8+ inverse folding models, evaluation test sets (CATH 4.2, TS50, CASP15).
- **Boltz-1:** [https://github.com/jwohlwend/boltz](https://github.com/jwohlwend/boltz)
  - Primary author: Jeremy Wohlwend (MIT Jameel Clinic)
  - License: MIT
  - Key assets: Open-source AlphaFold3-level biomolecular structure prediction model weights and inference pipeline.

## 2. Benchmark Datasets & Databases
- **CATH Database:** [https://www.cathdb.info/](https://www.cathdb.info/) (v4.2 / v4.3 topological splits)
- **ProTherm Database:** Thermodynamic stability measurements for single mutants.
- **Rocklin Protease Miniproteins:** High-throughput stability scores for de novo designs (Rocklin et al. 2017).
