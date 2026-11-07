# Supporting data for exploratory drug-target prioritization

The expression dataset remains the six original mice. External annotations add
context for target hypotheses; they do not add biological replicates, untreated
controls, or drug-response measurements to this experiment.

## Collected sources

- [MGI homology report](https://www.informatics.jax.org/downloads/reports/index.html):
  mouse–human homology groups, gene symbols, MGI IDs, and HGNC IDs.
- [HGNC complete approved dataset](https://www.genenames.org/download/):
  human approved symbols and HGNC-to-Ensembl identifier mappings.
- [Open Targets API](https://platform-docs.opentargets.org/data-access/graphql-api):
  direct target associations for hepatic fibrosis (`HP_0001395`), cirrhosis of
  liver (`MONDO_0005155`), drug-induced liver injury (`MONDO_0005359`), and acute
  liver failure (`MONDO_0019542`). Acute conditions and chronic scarring conditions
  remain distinct. None is asserted to be equivalent to the mouse injury model.

For each disease-associated human target, the snapshot includes available mouse
homologues, homology type/confidence, tractability categories, reported safety
liabilities and their references, and drug/clinical-candidate records. Drug records
retain indications, clinical stages, trial links, and mechanisms of action where
available. Returned trial lists can vary between API responses; the collector
unions returned records and does not claim an exhaustive clinical-trial inventory. A compound's overall clinical stage does not establish approval for
liver injury; read the specific indication and supporting trial evidence.

## Reproducible files

`data/external/manifest.json` records the retrieval timestamp, API release, exact
GraphQL query, source URLs, and SHA-256 checksums. Compressed source snapshots and
derived CSVs live in `data/external/`; uncompressed working downloads are ignored.

| File | Contents |
| --- | --- |
| `mouse_human_homology.csv` | All mouse–human MGI group pairs, joined to HGNC human Ensembl IDs |
| `target_mouse_orthologs.csv` | Stable mouse feature IDs and human target IDs from Open Targets, with homology type/confidence |
| `disease_target_associations.csv` | Separate disease associations and scores by evidence source/type |
| `target_annotations.csv.gz` | Human targets with structured drug, tractability, and safety annotations stored as JSON fields |
| `feature_mapping_coverage.csv` | Every original feature, mapping method, ambiguity indicators, and collected evidence coverage |
| `coverage_summary.json` | Counts for the collected snapshot and feature mapping coverage |

Rebuild tables offline from the checked snapshots:

```sh
python3 gather_target_data.py
```

Refresh public sources, then rebuild (requires internet access and `curl`):

```sh
python3 gather_target_data.py --download
```

The script uses the Python standard library. It retrieves every association page
for the four specified terms, checks expected totals and unique target IDs, and
checks that the API release/count does not change during the download. Tied
association scores can reorder page boundaries: the collector merges overlapping
passes at different page sizes and requires the exact number of unique targets
reported by the API. It fails instead of accepting incomplete coverage.
Use `--download --resume` to reuse cached requests after an interrupted download;
a normal `--download` refreshes the sources.
The feature coverage report reads the feature table in `data/source/24_m1.zip`;
the full-data audit already verifies identical feature tables across six samples.

## Joining and interpretation rules

Prefer the stable mouse feature ID matched to an Open Targets mouse homologue.
Retain one-to-many mappings and confidence labels; do not silently select a human
gene. MGI exact-symbol mappings provide broader coverage but are marked
`mgi_exact_symbol_requires_review`: current symbols may differ from older dataset
annotations. Repeated symbols, unmapped features, and missing human IDs stay visible.
A homology group with one mouse and one human gene is a group-size observation,
not an independent confidence assessment.

Open Targets annotations are collected for the union of targets associated with
the four specified conditions, not every human gene or every liver condition.
Missing collected evidence means “not covered in this snapshot,” not “no biological
role,” “undruggable,” or “safe.” The association score is not a probability of
therapeutic success. Evidence-source scores stay separate so literature or animal
evidence cannot be mistaken for human genetic or clinical validation. External
evidence can include this study or related mouse studies and is not automatically
independent validation.

Reported safety events require context and are not predictions of a candidate
drug's toxicity. A listed mechanism of action concerns the listed drug–target
relationship; it does not establish the desirable intervention direction in this
injury model. Expression alone cannot resolve inhibition versus activation.

## Data still needed for stronger claims

The current project can proceed with these resources for exploratory prioritization.
Candidate-specific functional papers and trial outcomes must be reviewed after a
shortlist exists. Independent human expression studies, uninjured controls, and
gene/drug perturbation experiments would be needed for stronger translation or
efficacy claims. We have not added unmatched expression cohorts as extra mice or
claimed that public annotations supply the missing experimental controls.

## Snapshot coverage — November 6, 2026

Open Targets release 26.09 supplies 8,849 direct disease–target associations
covering 5,583 distinct human targets: 3,962 hepatic fibrosis associations, 3,940
cirrhosis associations, 103 drug-induced liver injury associations, and 844 acute
liver failure associations. The same target may appear for multiple conditions.

The MGI/HGNC table contains 24,590 homology pairs. Of the dataset's 32,285 features,
5,694 have stable-ID Open Targets mouse homologue mappings in the collected target
set; 12,610 have exact-symbol MGI fallback matches requiring review; 13,981 remain
unmapped by these sources. A human Ensembl ID is available for 18,295 features
across the two mapping methods. Of those, 5,993 link to collected disease evidence,
including provisional symbol-based links. These counts do not define a candidate
shortlist or demonstrate that any target is therapeutically useful.

The large target-annotation CSV is gzip-compressed to stay within GitHub file-size
limits. Python's `gzip.open(..., "rt")` and `csv.DictReader` can read it directly.

## Normal-human tissue expression — safety-review context

Added [Human Protein Atlas tissue data](https://www.proteinatlas.org/humanproteome/tissue/data),
version 25.1 (Ensembl 109): consensus RNA nTPM and normal-tissue IHC protein annotations.
The RNA file combines HPA/GTEx information and is a processed reference, not an
independent untreated control cohort for the mouse experiment. Preserve its nTPM
units; do not compare nTPM numerically with mouse log-normalized counts.

The checked download contains 20,162 RNA-profiled genes across 51 tissue names and
15,312 genes with protein annotation rows across 60 tissue names (including additional
IHC panels). Coverage varies by gene. Raw protein rows retain tissue, cell type,
level, and reliability. “N/A,” gradients (“Ascending”/“Descending”), and “Not
representative” stay distinct from measured “Not detected” and Low/Medium/High.

`tissue_manifest.json` records source URLs, release, retrieval time, ZIP checksums,
and licensing. `target_tissue_summary.csv` joins the 5,583 collected human targets
by Ensembl ID, with liver RNA, the maximum non-liver RNA and tied tissues, number
of non-liver tissues at >=1 nTPM, protein coverage, and reliability counts. The 1 nTPM
threshold is descriptive, not a toxicity threshold. Full profiles remain in the ZIPs.
`tissue_coverage_summary.json` reports actual source and target coverage.

```sh
python3 gather_tissue_data.py            # verify sources and rebuild offline
python3 gather_tissue_data.py --download # refresh public ZIPs and manifest
```

Human Protein Atlas attribution: Uhlén et al., *Tissue-based map of the human
proteome*, Science (2015), [doi:10.1126/science.1260419](https://doi.org/10.1126/science.1260419),
and [Human Protein Atlas](https://www.proteinatlas.org/). See the
[licence and citation terms](https://www.proteinatlas.org/about/licence), including
third-party terms for incorporated datasets. This is expression/safety-review
context; it does not establish on-target toxicity, off-target binding, or safe exposure.
