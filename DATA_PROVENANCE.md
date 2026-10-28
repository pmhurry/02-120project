# Coverage and provenance — October 28, 2026

## What happened to the supplied expression matrix?

The 348 expression barcodes equal `metadata_barcodes[::50]` exactly: metadata
indices 0, 50, 100, …, 17,350, in the same order. This is systematic subsampling
by file position. On October 28, the project owner confirmed that the matrix was
reduced this way because the full file was too large for GitHub. The selection
was for file size, not biological quality filtering. This explanation is supplied
by the project owner; the exact barcode pattern was independently checked.
Git first records both supplied files in commit `757cc45` as an upload, with no
generating script.

This does not make the subset random or representative. It also does not establish
that every omitted spot passes any particular quality threshold.

## Sources and versions

- Counts/images: [authors' Visium archive, record 10901217, v1](https://zenodo.org/records/10901217), accessed October 28, 2026.
- Metadata: [authors' study archive, record 6035873, v2](https://zenodo.org/records/6035873), accessed October 28, 2026.

The supplied `Visium_Meta_data.txt` has MD5
`84aab211579f319c0e8a465a9ec72115`, exactly the checksum published for that file
in record 6035873. This establishes its source byte for byte; it does not
independently reproduce the annotation procedure.

Published ZIP checksums for recovery:

| Sample | MD5 |
|---|---|
| 24_m1 | e5c745814e430b83b32dc4641b5828f5 |
| 24_m2 | c686c9f6982676131ddeae33280209df |
| 48_m4 | b29df9e20a484d7d9e06da267f7d6c78 |
| 48_m5 | 14e3d248a0bc8a40da6938acae25ee43 |
| 72_m1 | 531f76f5637359de201dba8bfb44f506 |
| 72_m2 | 418a06e1f562ab50ab80234d254d92f4 |

Download URL pattern:
`https://zenodo.org/records/10901217/files/{sample}.zip`.
Downloaded archives belong in `data/source/` (ignored by Git); retain the original
ZIPs rather than overwriting the supplied CSV.

## Reconciliation procedure

`inspect_archive.py` reads an archive without extracting files or modifying data.
For example:

```sh
python3 inspect_archive.py data/source/24_m1.zip --sample 24_m1 --expected-md5 e5c745814e430b83b32dc4641b5828f5
```

It verifies the published checksum when supplied, checks feature-symbol order,
matches sample-prefixed barcodes, and compares every gene count for every supplied
spot in that sample, including zeros absent from the sparse matrix. Counts come
from `outs/raw_feature_bc_matrix/{matrix.mtx,features.tsv,barcodes.tsv}.gz`.
The features file retains gene identifiers, so future loading should retain those
identifiers alongside repeated symbols.

For coordinates, it compares metadata `(x, y)` with the positions file's
`(pxl_col_in_fullres, pxl_row_in_fullres)`. These are image pixels, not micrometers.
The archive's scale factors connect full-resolution positions to the supplied
high/low-resolution tissue images. Pixel agreement alone does not validate a
rendered image overlay; that still needs a visual check.

## Annotation limits

Metadata provenance is verified by checksum. The earlier paper-methods review
recorded collagen-based annotations at 48/72 h and manual necrotic-region
annotation at 24 h; see `DATA_INSPECTION.md`. The study archive also lists manually
annotated Loupe files. We have not independently regenerated the binary labels
from those files or reproduced the thresholds. Consequently, label interpretation
still differs across time, and collagen enrichment remains a reproduction check
rather than independent validation.

## Recovery results and checkpoint scope

All six downloaded ZIPs match the published checksums. Every archive has 32,285
features in the same symbol order as the supplied matrix. Audit outputs are saved
in `provenance/{sample}.txt`.

| Sample | Metadata barcodes recovered | Supplied spots compared | Count mismatches | Pixel coordinates matching |
|---|---:|---:|---:|---:|
| 24_m1 | 3,075/3,075 | 62 | 0 | 3,075 |
| 24_m2 | 2,688/2,688 | 54 | 0 | 2,688 |
| 48_m4 | 2,965/2,965 | 59 | 0 | 2,965 |
| 48_m5 | 3,457/3,457 | 69 | 0 | 3,457 |
| 72_m1 | 2,734/2,734 | 55 | 0 | 2,734 |
| 72_m2 | 2,451/2,451 | 49 | 0 | 2,451 |
| Total | 17,370/17,370 | 348 | 0 | 17,370 |

All metadata spots are flagged as in-tissue in the archive positions files. Raw
archives also contain barcodes outside the supplied metadata; future analyses
should explicitly select metadata barcodes rather than include all raw barcodes.
In-tissue status does not replace expression-quality assessment.

**Checkpoint decision:** retain the explicitly limited 348-spot workflow for
checkpoint 1 normalization/scoring checks; use recovered full data for the
project's scientific analysis after validating the sparse loader in checkpoint 2.
The full counts and images are now
available locally in `data/source/`, but using them requires a validated sparse
loader. Full-coverage loading is follow-up work before app development. A dense
32,285-by-17,370 table would contain about 561 million entries, so expanding the
current dense loader is a poor default.

The current `load_dataset` still reads the supplied CSV. Missing measurements in
that workflow remain missing; no source files were overwritten. No full-data
gene comparisons, image overlays, or label regeneration were performed today.
