# Spatial liver injury explorer

Class project exploring annotated fibrogenic regions and extracellular matrix gene expression at 24, 48, and 72 hours after acute liver injury.

The project is at the data-loading stage. An interactive app and fibrogenic score have not yet been implemented.

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
