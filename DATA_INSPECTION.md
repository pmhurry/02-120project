# Data inspection — October 27, 2026

The current files support a prototype of the proposed project, with substantial limits on expression-map coverage and on validation. Source data were not changed.

**October 28 update:** See [coverage and provenance](DATA_PROVENANCE.md).
The expression barcodes exactly equal every 50th metadata barcode, and the
metadata file's checksum matches the authors' published file. The findings below
describe the originally supplied subset; archive recovery does not change that CSV.
The project owner subsequently confirmed the subset was selected to fit GitHub's
file-size limit. Full archives have now been recovered and reconciled; the
historical unknowns and recovery recommendations below are resolved as described
in the provenance report.

## Files and integrity

`spatial_matrix.csv` contains 32,285 gene rows and 348 spot columns. `Visium_Meta_data.txt` is comma-delimited despite its extension and contains 17,370 spot records.

- All 348 expression spot IDs match unique metadata IDs. Join by ID, never by row position.
- The other 17,022 metadata spots have no expression in the supplied matrix. Only 2.00% of metadata spots have expression; the reason for this subset is unknown.
- Both metadata IDs and matrix spot IDs are unique. Metadata have no empty fields.
- Counts are finite, nonnegative integers, consistent with UMI counts, although processing provenance has not been independently established.
- No expression spot has zero total counts. Spot totals range from 1,333 to 25,812; the median is 9,382. Normalize for library size before comparing expression.
- 91.44% of matrix entries are zero; 17,211 gene rows are entirely zero in this subset. Zeros alone do not establish poor quality.
- There are 32,245 unique gene symbols: 38 symbols occur more than once, accounting for 40 extra rows. Preserve these rows until their feature identities are clarified; do not silently overwrite them in a symbol-indexed dictionary.

## Time points and samples

| Time | Samples | Metadata spots | Spots with expression | Fibrogenic expression spots | Other expression spots |
|---|---|---:|---:|---:|---:|
| 24 h | t_24h_m1, t_24h_m2 | 5,763 | 116 | 43 | 73 |
| 48 h | t_48h_m4, t_48h_m5 | 6,422 | 128 | 18 | 110 |
| 72 h | t_72h_m1, t_72h_m2 | 5,185 | 104 | 14 | 90 |

All six samples have both labels and unique coordinates among their expression spots. One 72 h sample has only four fibrogenic expression spots. Compare samples separately before summarizing time points; spots are not independent biological replicates.

The fraction annotated fibrogenic in the full metadata is 29.10%, 14.98%, and 14.58% at 24, 48, and 72 h. In the expression subset it is 37.07%, 14.06%, and 13.46%. Consequently, subset proportions should not substitute for full-metadata proportions. These are annotated-spot fractions, not direct measurements of tissue area or fibrosis severity.

## Exploratory marker check

For each spot, I divided counts by its total counts, multiplied by 10,000, and applied the natural logarithm as `log1p`. Entries below are group means, pooled across the two samples at each time point. These are descriptive comparisons, not significance tests.

| Gene | 24 h fibrogenic / other | 48 h fibrogenic / other | 72 h fibrogenic / other |
|---|---:|---:|---:|
| Col1a1 | 0.141 / 0.117 | 1.473 / 0.329 | 1.570 / 0.293 |
| Col1a2 | 0.220 / 0.068 | 1.852 / 0.526 | 1.848 / 0.517 |
| Col3a1 | 0.237 / 0.095 | 2.048 / 0.648 | 2.643 / 0.847 |
| Acta2 | 0.616 / 0.184 | 0.693 / 0.200 | 0.284 / 0.029 |
| Timp1 | 0.648 / 0.173 | 0.546 / 0.154 | 0.316 / 0.070 |
| Fn1 | 2.368 / 2.748 | 2.331 / 2.524 | 2.464 / 2.235 |

All six markers are present. The observed pattern supports exploring gene-specific temporal differences; it does not support requiring every extracellular-matrix marker to be higher in every annotated group.

## Fit to the proposal

- **Interactive map:** Coordinates and labels support full annotation maps. Gene-expression maps can currently show only 348 spots. Missing expression must remain missing rather than become zero. No tissue images or image-alignment files are present. Use separate sample panels; coordinate ranges differ substantially between samples, and physical distance units are undocumented locally.
- **Neighborhood explorer:** Spot inspection and label-group comparisons are possible. Reliable local neighborhoods need denser expression coverage. Spots across different samples/time points are not longitudinally matched locations.
- **Fibrogenic score:** Marker expression is available, but the formula and reference must be specified. A positive marker average does not automatically become zero for identical nonzero profiles. A centered score or a difference from an explicit reference could meet that baseline requirement, with zero-variance and zero-count cases handled explicitly. There is no uninjured control in these files; label 0 means non-fibrogenic annotation, not necessarily healthy tissue.
- **Scientific scope:** These measurements can examine spatial expression after injury. They do not directly establish early prediction before cell death, causation, or clinical fibrosis severity.

## Paper and validation

The [paper's spatial-processing methods](https://shalevlab.weizmann.ac.il/wp-content/uploads/2022/06/1-s2.0-S1934590922001618-main.pdf), page 24, describe collagen-fraction thresholding for fibrogenic annotation at 48/72 h, but manual annotation of necrotic regions at 24 h because collagen was not sufficiently elevated. If the local labels are these annotations, collagen enrichment against them is partly circular and label meaning differs across time. The local files alone cannot verify annotation provenance.

The [authors' Visium archive](https://zenodo.org/records/10901217) lists six sample archives and confirms two mice per time point. It is a candidate source for restoring full expression coverage and image context; it has not been downloaded or reconciled with the local files.

Recommended next steps:

1. Establish how the current 348 spots were selected and recover full expression coverage if feasible.
2. Document source versions, feature identities, coordinate units, preprocessing, and label provenance.
3. Define a modest computational model: explicit score, normalization, spatial neighborhood rule, and sample-level comparisons.
4. Keep collagen/annotation agreement as a reproduction check. Add checks using markers not used to define labels, ideally in held-out mice, while acknowledging only two mice per time point.
5. Retain the identical-profile synthetic check and add known-expression contrasts and barcode-alignment checks. Do not change the model merely to force an expected biological result.
