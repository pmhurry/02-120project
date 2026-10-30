# Spatial liver injury explorer

Class project exploring annotated fibrogenic regions and extracellular matrix gene expression at 24, 48, and 72 hours after acute liver injury.

The project has a checked subset loader, library-size normalization, an exploratory collagen score, and static spatial and group-comparison figures. An interactive app has not yet been implemented.

## Run the data checks

Use Python 3.10 or newer. The current loader uses only the standard library; no packages need to be installed.

```sh
python3 inspect_data.py
python3 -m unittest discover -s tests -v
```

The loader reads `spatial_matrix.csv` and the comma-delimited `Visium_Meta_data.txt`. Expression rows are genes and columns are spots. Metadata are aligned by full barcode, not file order. Duplicate gene symbols are preserved as separate rows pending feature clarification.

Currently, only 348 of 17,370 metadata spots have expression measurements. Unmeasured spots must not be interpreted as having zero expression. There are two mouse samples per time point; time points do not track the same cells.

See [data inspection](DATA_INSPECTION.md) for findings and scientific limitations, and the [October 27–30 checklist](CHECKPOINT_1.md) for the first build checkpoint.

See [coverage and provenance](DATA_PROVENANCE.md) for the October 28 recovery
investigation and the archive reconciliation command. The supplied expression
barcodes are exactly every 50th metadata barcode. The project owner confirmed
this reduction was made to fit GitHub's file-size limit. Recovered full archives
are kept outside Git in `data/source/`; checkpoint 2 will add validated sparse
loading for full-data analysis. The current loader still reads the subset CSV.

## Normalization and score

Run `python3 inspect_scores.py` for the 348-spot subset. See [the score definition](SCORING.md) for the fixed collagen panel, formulas, reference, edge cases, and interpretation limits. Full-data scoring remains scheduled for checkpoint 2.

## Checkpoint 1 figures

Run `python3 plot_checkpoint.py` (standard library only). Open
[the spatial map](results/spatial.svg) and [the per-mouse comparison](results/group_comparison.svg)
in a browser; [the CSV](results/group_summary.csv) provides exact means and counts.
Use `--mouse t_48h_m4 --gene Col3a1 --output /tmp/liver-plots` for another view.
The default is `t_24h_m1` and `Col1a1`. See [plot interpretation](PLOTTING.md)
for limitations and outstanding checkpoint review.
