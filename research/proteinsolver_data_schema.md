# PROTEINSOLVER: DATASET FORENSICS & ON-DISK SCHEMA

This document records the exact, source-verified dataset schema discovered by inspecting `proteinsolver/datasets/protein.py` and `proteinsolver/datasets/protein_v2.py`.

---

## 1. Resolution of Historical Uncertainty

> [!IMPORTANT]
> **Resolution of Claim S-01:** Previous literature reviews tentatively assumed an HDF5 on-disk format based on early repository notes. Source code inspection reveals that the actual on-disk serialization format used by the author for the Gene3D training corpus is **Apache Parquet (`.snappy.parquet`)** read via `pyarrow.parquet`.

---

## 2. Parquet File Schema & Column Specifications

The raw datasets distributed at `http://deep-protein-gen.data.proteinsolver.org/` consist of partitioned Parquet files:

```
deep-protein-gen/processed/
├── training_data_0/
│   └── part-00000-a260936c-8c1c-4b93-b9ab-57757dbf29b8-c000.snappy.parquet
├── training_data_1/
│   └── part-00000-7cab69dd-7eec-4823-8c4b-c355264bca9b-c000.snappy.parquet
├── validation_data/
│   └── part-00000-4f535e50-cdf4-4275-b6b3-a3038f24a1a9-c000.snappy.parquet
└── test_data/
    └── part-00000-ba92a066-6ee2-47dc-883c-fd2044ecaa00-c000.snappy.parquet
```

### Table Columns (Discovered in `proteinsolver/datasets/protein.py`, lines 188–205)

| Field Name | Storage Dtype | Python / Arrow Type | Description |
|---|---|---|---|
| `sequence` | UTF-8 String | `str` | Amino acid sequence of the domain (hyphens/gaps `'-'` stripped). |
| `residue_idx_1_corrected` | Array / List of int | `List[int64]` | Zero-based index of source residue in contacting pair. Renamed to `row_index`. |
| `residue_idx_2_corrected` | Array / List of int | `List[int64]` | Zero-based index of target residue in contacting pair. Renamed to `col_index`. |
| `distances` | Array / List of float | `List[float32]` | Shortest heavy-atom Cartesian distance in Angstroms ($< 12.0\text{ \AA}$). |
| `database_id` | String (optional metadata) | `str` | Gene3D superfamily accession (e.g., `G3DSA:2.40.155.10`). |

---

## 3. In-Memory Graph Object Representation (`torch_geometric.data.Data`)

When parsed by `proteinsolver.datasets.protein.row_to_data` and transformed by `transform_edge_attr`:

```python
data = Data(
    x=seq,              # [N], torch.long (0..19 for AAs, 20 for MASK)
    edge_index=edge_index,  # [2, 2*E], torch.long (undirected, self-loops removed)
    edge_attr=edge_attr     # [2*E, 2], torch.float (normalized Cartesian + sequence distance)
)
```

### Edge Normalization Formulas (Exact)
1. **Cartesian Distance Feature:**
   $$\text{edge\_attr}[:, 0] = \frac{d - 6.0}{12.0}$$
   Centers a 6 Å contact around 0, mapping the $[0, 12]$ Å range to $[-0.5, +0.5]$.
2. **Sequence Separation Feature:**
   $$\text{edge\_attr}[:, 1] = \frac{(j - i) - 0.0}{68.1319}$$
   Normalizes the 1D primary sequence distance offset by the empirical mean/std across Gene3D domains ($68.1319$).

---

## 4. Availability of Training Corpus
- The remote URL `http://deep-protein-gen.data.proteinsolver.org/` points to the historical Google Cloud Storage bucket (`https://storage.googleapis.com`).
- As specified in our research protocol (`DEC-004`), downloading the massive 72M Parquet dataset is deliberately **rejected** because our focus is evaluating the trained model's inference properties using the author's official converged checkpoint.
