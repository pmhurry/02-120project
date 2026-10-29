# Normalization and exploratory collagen score — October 29, 2026

## Scope and panel

Checkpoint 1 uses the supplied 348 measured spots, not the recovered full dataset.
The panel is fixed as Col1a1, Col1a2, and Col3a1 because they encode collagen
components relevant to the project's extracellular matrix question. This is a
narrow collagen activity score, not a comprehensive measure of fibrogenesis.
These markers were already explored on October 27: this is not a blinded or
prospective selection, and their earlier group differences are not validation.
No markers are selected or weighted using today's score results or labels.

## Calculation

For measured spot j, library size L_j is the sum of raw counts across **all**
gene rows, including preserved duplicate symbols. For each panel gene g:

    x_gj = ln(1 + 10,000 * count_gj / L_j)
    z_gj = (x_gj - mean_g) / sd_g
    score_j = (z_Col1a1,j + z_Col1a2,j + z_Col3a1,j) / 3

The logarithm is natural. Normalizing reduces differences due to total measured
counts; it does not remove cell mixture, technical effects, or all sampling noise.
The reference is all positive-library measured spots in the input dataset,
pooled across six mice and three time points. Each spot has equal reference
weight, so this reference is not balanced by mouse. SD uses the population
formula (divide squared deviations by reference spot count).

Fit the reference once before filtering the displayed mouse, time, or group.
Zero means average standardized panel activity relative to this reference;
positive means higher and negative means lower. Zero does not mean no collagen,
healthy tissue, or zero raw expression. Different marker deviations can cancel.
The score is dimensionless and not a probability or significance test.

## Edge cases and reference changes

- A constant marker contributes exactly 0.0, retaining the three-gene denominator.
  Identical profiles at every spot therefore yield exactly 0.0 scores.
- A measured zero for one gene normalizes to zero if its library is positive.
- A zero-library spot has undefined normalization: normalized values are NaN
  and its score is None. It is excluded from reference fitting. All-zero inputs
  raise an error because no reference exists.
- Metadata-only spots never enter scoring and must remain missing in maps.
- Each selected marker must match exactly one gene row; missing or ambiguous
  symbols raise an error. Other duplicate gene rows remain preserved.
- The full-data migration must recompute and record its reference. Subset scores
  and full-data scores use different baselines and are not directly interchangeable.

## Checks and interpretation limits

Run `python3 -m unittest discover -s tests -v` and `python3 inspect_scores.py`.
Synthetic checks verify identical nonzero profiles, proportional depth scaling,
a known low/high contrast, zero libraries, and missing/duplicate marker handling.
The supplied subset has 348 positive-library spots; scores range from -0.7369 to
2.9541 with mean approximately zero by construction. This mean is not evidence
of biological accuracy.

As recorded in DATA_INSPECTION.md, collagen expression helped define the authors'
48/72 h annotations; agreement is therefore a consistency check, not independent
validation. The 24 h annotations instead describe manually marked necrotic regions.
RNA activity does not directly measure collagen protein or accumulated scar tissue.
Only two mice per time point are available; spots are not independent biological
replicates, and different time points do not track the same spots longitudinally.
