# Spatial Target Prioritization Engine

An interpretable scoring and ranking tool for therapeutic-target hypotheses after
acute liver injury. It combines spatial expression evidence, human target mapping,
tractability, and a visible safety-evidence review. RNA enrichment does not establish
causality, treatment direction, drug efficacy, oral delivery, or clinical safety.

**Workflow:** spatial evidence → human mapping → tractability → safety review →
ranked hypotheses for experimental follow-up.

**Current status (November 8):** full-data spatial summaries and the fixed ranking
model are implemented and validated. The default hepatic-fibrosis export screens
32,285 features and ranks 2,248 complete-evidence hypotheses. Mapping exclusions,
incomplete evidence, tissue context, and reported liabilities remain visible.
The Streamlit interface is scheduled for November 9.

- [Engine design and scoring rubric](ENGINE_DESIGN.md)
- [Supporting data, coverage, and source limitations](TARGET_DATA.md)
- [File keep/delete decisions](FILE_POLICY.md)
- [Checkpoint 1: historical baseline](CHECKPOINT_1.md)
- [Checkpoint 2: local engine, November 10](CHECKPOINT_2.md)
- [Checkpoint 3: deployment and robustness, November 20](CHECKPOINT_3.md)
- [Checkpoint 4: evidence review and final submission, December 1](CHECKPOINT_4.md)

See the [build journal](journal/README.md) for the work days, including
[November 6's conversation and quiz](journal/session6.txt), readable Codex exports,
and conversation copies.

## Historical subset checks

Use Python 3.10 or newer. The current loader uses only the standard library; no packages need to be installed.

```sh
python3 inspect_data.py
python3 -m unittest discover -s tests -v
```

The loader reads `spatial_matrix.csv` and the comma-delimited `Visium_Meta_data.txt`. Expression rows are genes and columns are spots. Metadata are aligned by full barcode, not file order. Duplicate gene symbols are preserved as separate rows pending feature clarification.

The original CSV workflow contains only 348 of 17,370 metadata spots. The separate full-data workflow below loads all metadata-matched spots from the recovered archives. Unmeasured spots must not be interpreted as having zero expression. There are two mouse samples per time point; time points do not track the same cells.

See [data inspection](DATA_INSPECTION.md) for findings and scientific limitations, and the [October 27–30 checklist](CHECKPOINT_1.md) for the first build checkpoint.

See [coverage and provenance](DATA_PROVENANCE.md) for the October 28 recovery
investigation and the archive reconciliation command. The supplied expression
barcodes are exactly every 50th metadata barcode. The project owner confirmed
this reduction was made to fit GitHub's file-size limit. Recovered full archives
are kept outside Git in `data/source/`; checkpoint 2 adds sparse loading for full-data analysis. Existing checkpoint 1 commands still explicitly read the subset CSV.

## Historical collagen-context score

Run `python3 inspect_scores.py` for the 348-spot subset. See [the score definition](SCORING.md) for the fixed collagen panel, formulas, reference, edge cases, and interpretation limits. The collagen score remains optional context; the new target-ranking model follows
[ENGINE_DESIGN.md](ENGINE_DESIGN.md).

## Checkpoint 1 figures

Run `python3 plot_checkpoint.py` (standard library only). Open
[the spatial map](results/spatial.svg) and [the per-mouse comparison](results/group_comparison.svg)
in a browser; [the CSV](results/group_summary.csv) provides exact means and counts.
Use `--mouse t_48h_m4 --gene Col3a1 --output /tmp/liver-plots` for another view.
The default is `t_24h_m1` and `Col1a1`. See [plot interpretation](PLOTTING.md)
for limitations and outstanding checkpoint review.

## Full expression coverage — checkpoint 2, session 1

Use Python 3.10 or newer; the sparse loader needs no third-party packages.
Download the six original ZIPs to `data/source/` using the sample names and
published MD5 checksums in [DATA_PROVENANCE.md](DATA_PROVENANCE.md). For example:

```sh
mkdir -p data/source
curl --fail --location https://zenodo.org/records/10901217/files/24_m1.zip --output data/source/24_m1.zip
```

Repeat for `24_m2`, `48_m4`, `48_m5`, `72_m1`, and `72_m2`. Keep the repository's
`Visium_Meta_data.txt` and `spatial_matrix.csv` unchanged. Then run:

```sh
python3 inspect_full_data.py
python3 -m unittest discover -s tests -v
```

The audit verifies all six ZIP checksums, matches every metadata barcode, checks
feature identities/order across samples, and compares every original subset count
including zeros. It writes `results/full_data_coverage.csv`; parsing takes time
because the raw matrices are streamed. No whole-matrix dense conversion occurs.

For analysis, call `sparse_loader.load_full_dataset(source_dir, metadata_path)`.
Use `data.feature_index("Col1a1")` or a stable feature ID, then
`data.count(feature_index, spot_index)`. Duplicate symbols remain separate features;
ambiguous symbol lookups raise an error. Spot order is explicit in `data.spots`.
A missing archive/barcode causes an error rather than filling missing data with zeros.

This expands expression coverage, not biological replication: there are still six
mice, two per time point. Session 2 applied zero-library QC (none excluded) and full-data normalization,
saved separately in `results/spatial/`. The subset figures and score outputs
have not been regenerated with full data.

Supporting mouse–human mapping and external target-evidence snapshots are documented
in [TARGET_DATA.md](TARGET_DATA.md). Their coverage and mapping uncertainties are
explicit; they are integrated into the CLI ranking. The app is pending. This dataset
contains no uninjured controls or treatment response measurements; region enrichment
cannot establish causality, drug efficacy, or the desired direction of intervention.

## External evidence and normal-human tissue context

The versioned snapshots in `data/external/` include mouse–human homology, HGNC
identifiers, Open Targets disease associations/tractability/drug/liability records,
and Human Protein Atlas normal-tissue RNA/protein profiles. These add annotations,
not extra biological replicates or missing experimental controls.

Rebuild the checked tables offline:

```sh
python3 gather_target_data.py
python3 gather_tissue_data.py
```

Use `--download` with either script to refresh its public sources. See
[TARGET_DATA.md](TARGET_DATA.md) for attribution, checksums, coverage, and caveats.
Normal-human tissue expression helps identify follow-up questions; it is not a
prediction that a target or drug is toxic. Missing records remain unknown.

## Full-data spatial evidence — checkpoint 2, session 2

```sh
python3 inspect_spatial.py
python3 -m unittest discover -s tests -v
```

This offline command verifies the source archives, normalizes using all-feature
library totals, and saves every feature's group means, detection fractions, and
within-mouse differences. It also saves equal-mouse summaries, QC, a subset
comparison, and a provenance manifest in `results/spatial/`. The 24-hour context
remains separate from 48/72 hours. See [methods and results](SPATIAL_EVIDENCE.md)
for the QC table, formulas, coverage effects, missingness, and validation.

## Target ranking — checkpoint 2, session 3

```sh
python3 inspect_ranking.py
python3 -m unittest discover -s tests -v
```

See [ranking methods, coverage, and checked examples](RANKING.md). Outputs in
`results/ranking/HP_0001395/` include an all-feature mapping/component audit,
spatial-only screen, complete ranking, compressed evidence profiles, and a
versioned manifest. The default weights are S/T/D = 0.60/0.25/0.15. Alternative
weight and individual-time ranks are explicit columns. These are experimental
hypotheses; the model does not score safety or infer treatment direction.
