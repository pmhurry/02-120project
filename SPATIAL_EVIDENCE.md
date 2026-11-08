# Full-data spatial evidence — November 7, 2026

Checkpoint 2, session 2 uses spatial-v1, the six checksum-verified source archives,
all 32,285 stable-ID features, and all 17,370 metadata-matched spots. This is a
separate analysis from the historical 348-spot outputs. No target ranking is
computed in this session.

Rebuild offline with Python 3.10 or newer (standard library only):

```sh
python3 inspect_spatial.py
python3 -m unittest discover -s tests -v
```

## Library QC and analysis population

The predeclared QC rule excludes only spots with zero total counts. All features
contribute to the library total. No mitochondrial, low-library, or gene-detection
threshold is imposed. This is limited library-size QC, not a claim that every
retained spot has optimal tissue or sequencing quality.

| Mouse | Retained | Excluded | Library min / median / max | Annotated / other |
| --- | ---: | ---: | --- | --- |
| t_24h_m1 | 3,075 | 0 | 499 / 4,251 / 30,127 | 852 / 2,223 |
| t_24h_m2 | 2,688 | 0 | 977 / 6,492 / 20,657 | 825 / 1,863 |
| t_48h_m4 | 2,965 | 0 | 2,084 / 9,931 / 34,129 | 440 / 2,525 |
| t_48h_m5 | 3,457 | 0 | 2,953 / 13,251 / 31,230 | 522 / 2,935 |
| t_72h_m1 | 2,734 | 0 | 2,248 / 11,051.5 / 30,436 | 389 / 2,345 |
| t_72h_m2 | 2,451 | 0 | 1,438 / 8,182 / 27,775 | 367 / 2,084 |

Library depths vary considerably. Library normalization accounts for total depth,
but does not remove cell-composition, spatial, annotation, or technical confounding.
There are still two mice per time point; spots are not independent animals.

## Calculations and missingness

For each retained spot and feature, calculate `ln(1 + 10000 * count / library)`.
For example, a count of 1 in a library of 4 gives `ln(2501)` (about 7.8244).
A measured zero in a positive library contributes zero. A zero library contributes
no expression or detection observation, rather than a measured zero.

For every feature within each mouse, calculate annotated and other group means,
raw-count detection fractions (number with count > 0 divided by retained group
size), group counts, and annotated-minus-other mean difference. The difference
uses log-normalized expression units; it is not a log fold change. Sparse storage
implicitly includes measured zeros in each group denominator without allocating
a full dense expression matrix. Duplicate symbols retain their separate stable IDs.

An empty group has unavailable mean/detection/difference, saved as an empty CSV
cell. A measured all-zero feature in a present group has mean and detection zero.
All groups in this dataset are present after QC.

Equal-mouse summaries average the two mouse means/differences at each time point.
The combined 48/72-hour view averages all four mice equally (equivalently the two
time-point averages). Incomplete mouse/group coverage leaves the aggregate missing;
available-mouse counts remain visible. These averages are descriptive summaries,
not the conservative spatial ranking component S planned for November 8.

24-hour necrotic-region context is separate from 48/72-hour collagen-linked
annotations. Three collagen panel genes are flagged as annotation-linked contextual
markers. Collagen agreement with the later labels is not independent validation.

## Exported tables

All outputs are in `results/spatial/`:

- `library_qc.csv`: retained/excluded counts and library statistics per mouse.
- `spot_libraries.csv.gz`: barcode-specific library size, group, and retention status.
- `per_mouse.csv.gz`: 193,710 rows (32,285 features × six mice), including means,
  detection fractions, differences, group counts, annotation context, and status.
- `equal_mouse.csv.gz`: 129,140 rows, with separate 24-hour, 48-hour, 72-hour,
  and combined 48/72-hour contexts and explicit availability.
- `subset_comparison.csv`: four selected genes, shared-spot normalization checks,
  and full-versus-subset within-mouse contrasts.
- `manifest.json`: input/archive identity, methods, code hashes, output checksums,
  and missing-value conventions. Gzip file bytes may differ on rebuild because of
  gzip timestamps; the table values and ordering are reproducible.

## Subset comparison and reference effects

For Col1a1, Col1a2, Col3a1, and Alb, all 348 shared spots have identical raw counts,
all-feature library totals, and normalized values (maximum numerical difference 0).
Full-data group contrasts can differ because the groups contain additional spots:

| Gene / mouse | Subset difference | Full-data difference |
| --- | ---: | ---: |
| Col1a1 / t_24h_m1 | -0.064815 | 0.091287 |
| Col1a1 / t_48h_m5 | 0.954793 | 1.343123 |
| Col1a1 / t_72h_m2 | 1.592054 | 1.095457 |
| Alb / t_72h_m2 | -0.865843 | -0.803779 |

The first sign change illustrates coverage sensitivity; it is not evidence of a
biological change between datasets. The subset included only four annotated spots
in t_72h_m2 versus 367 in the full data. Normalization has no fitted population
reference, so adding spots does not change a shared spot's normalized value.
The historical collagen z-score *does* use dataset-wide means and SDs: its reference
would change if recomputed on full data. That score and its saved figures remain
unchanged, and no full-data collagen z-score is implied here.

## Validation and remaining scope

All 24 unit tests pass. New synthetic checks cover hand normalization, identical
proportions, a known positive/negative contrast, spot-column permutation, duplicate
symbols, zero libraries, absent groups, invalid sparse columns, unequal group
sizes with equal mouse weights, and time-context separation/missingness.
The full-data run verifies six archive checksums; output review confirms all
193,710 per-mouse and 129,140 aggregate rows are available and output checksums match.

No causal effect, intervention direction, efficacy, or safety conclusion follows
from these contrasts. Ranking/mapping gates are November 8 work; the interface is
November 9 work. Guided student explanation/review was completed; answers and corrections are
recorded in journal/checkpoint2_session2_notes.md.
