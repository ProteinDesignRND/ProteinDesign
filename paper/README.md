# PAPER & MANUSCRIPT ARTIFACTS

This directory contains manuscript drafts, LaTeX source files, publication-quality vector figures, and curated BibTeX bibliography files for the semester-long research project.

---

## Directory Organization

```
paper/
├── draft/               # Markdown and LaTeX manuscript sections
│   ├── 01_introduction.md
│   ├── 02_related_work.md
│   ├── 03_methods.md
│   ├── 04_experiments.md
│   ├── 05_results.md
│   └── 06_discussion.md
├── figures/             # High-resolution SVG / PDF plots and diagrams
├── tables/              # LaTeX / Markdown tables of benchmark results
└── references.bib       # Curated BibTeX file containing verified DOIs and entries
```

---

## Manuscript Writing Standards

1. **Evidence-Bounded Writing:** Every empirical claim made in the manuscript must directly reference a table or figure generated from the `evaluation/` directory.
2. **Zero Citation Fabrication:** Every citation in `references.bib` must be cross-verified against its official DOI, PubMed ID, or arXiv identifier.
3. **Transparent Limitations:** The manuscript must prominently discuss limitations, including:
   - Reliance on computational structural oracles (ESMFold/AF2) rather than wet-lab expression.
   - The trade-offs between distance-only graph formulations and full-coordinate models.
   - Regimes where simpler baselines dominate.
