# October 30 checkpoint figures

`python3 plot_checkpoint.py` creates `results/spatial.svg`,
`results/group_comparison.svg`, and `results/group_summary.csv` without extra
packages. It reads the unchanged 348-spot subset. The default spatial view is
mouse `t_24h_m1`, gene `Col1a1`. Options: `--mouse`, `--gene`, `--output`.
A gene must match exactly one expression row; absent or ambiguous symbols fail.

The left map shows annotations for all metadata spots in one mouse. The right
map shows log1p(count / library size × 10,000) for the same mouse. Gray means
unmeasured or unscorable expression; pale yellow means measured zero. The color
maximum is shared across all six mice for the selected gene. Coordinates preserve
aspect ratio and use image orientation (y increases downward). These are spot
coordinate maps without a tissue-image overlay. Hovering a spot shows its barcode
and value. Separate runs for other mice should use distinct output folders to
retain previous figures.

The comparison shows the mean of individually log-normalized spot values for each
annotation within each mouse, not the logarithm of an average count. All six mice
are displayed separately, two per time point. The CSV records metadata, measured,
and scorable spot counts. Missing groups have no bar, rather than a zero mean.
No hypothesis tests or confidence intervals are claimed.

## Observed result

For Col1a1, fibrogenic versus other means are 1.941 versus 0.376 and 1.240 versus
0.285 at 48 hours, and 1.448 versus 0.303 and 1.875 versus 0.283 at 72 hours.
Both mice at each of these times show higher expression in the annotated group.
At 24 hours the directions differ: 0.121 versus 0.186 in mouse 1 and 0.165 versus
0.043 in mouse 2. These averages are in log1p counts-per-10,000 units, not fold
changes, physical concentrations, or collagen protein measurements.

Only 348 of 17,370 spots have expression in this workflow. Fibrogenic measured
spot counts at 48/72 hours are just 6, 12, 10, and 4. Subset estimates may change
with full coverage. Spots within a mouse do not constitute independent mice;
there are only two biological replicates per time point. Samples at different
times come from different mice. At 48/72 hours collagen expression helped create
the annotations, so this agreement is a consistency check. At 24 hours the
annotation used necrotic regions, which has a different biological meaning.
Full-data migration remains in checkpoint 2.

## Review still needed

The user should explain one result and its limits in their own words, review the
outputs and changes, save/review the session journal, and commit when ready.
The course requires Claude Code session logs according to the assignment context
recorded in `journal/session1.txt`; these existing text transcripts identify
that they are not native Claude Code exports. Today's code and figures alone
do not establish that the course journal requirement is satisfied.
