# Checkpoint 3, session 2 — November 18, 2026

## Compound evidence

The initial ranks remain CD74, LGALS3, and CTSS. The
[reviewed compound export](../results/compound_activity/reviewed_compounds.csv)
cites primary experiments and records one agent per target. These are observations
from different experiments. A purified-protein binding Kd and an enzyme
inhibition IC50 are separate endpoints.

- **CD74 — mixed/context-dependent.** Antagonizing MIF in acute APAP injury
  preserved hepatic dendritic cells. CD74 knockdown reduced an inflammatory
  signal in mouse hepatocytes in a separate study. MIF signaling through CD74
  protected hepatocytes in metabolic models. Milatuzumab is a human CD74 antibody
  comparator. Its effect on the hepatic pathway and its engagement in mice are
  unresolved. The source snapshot also links repotrectinib through CD74–ROS1
  fusion inhibition. The reviewed evidence did not establish a suitable
  direct small-molecule CD74 candidate for acute APAP follow-up.
- **LGALS3 — mixed/context-dependent.** Whole-body loss supported less late APAP
  hepatotoxicity and increased hepatocyte proliferation during mouse recovery.
  TD139 engages Gal-3 and Gal-1, and it increased ALT in an HBV transgenic mouse
  study. Acute APAP evidence supports testing a Gal-3 inhibition hypothesis.
  The knockout cannot establish the effect of dosing TD139 after injury.
- **CTSS — unknown in acute APAP.** Macrophage-specific CTSS loss and LY3000328
  supported a role for CTSS inhibition in chronic CCl4 fibrosis. The study
  measured stellate cell activation, matrix endpoints and ALT after prolonged
  injury. Relevance to acute APAP injury and repair is unresolved. Human
  pharmacodynamic measurements also showed rebound CTSS activity following
  initial inhibition.

The app displays the reviewed evidence separately from the rank and exposes
normal-human tissue context, reported liabilities, and the source snapshot.
Tractability and measured liver RNA coverage filters preserve original ranks
and report their effect on the current view before text search.

## Frozen dataset

[Dataset](../results/compound_activity/galectin3_dataset.csv) ·
[Manifest](../results/compound_activity/galectin3_manifest.json) ·
[Builder](../scripts/prepare_compound_activity.py).

Run `python3 scripts/prepare_compound_activity.py` with RDKit 2026.3.3.
The only endpoint is IC50 for inhibition of recombinant human galectin-3
binding to biotinylated asialofetuin in ChEMBL assay CHEMBL5737905
(document CHEMBL5729012). The input is the ChEMBL 37 snapshot.
There were 496 prefiltered LGALS3 rows, 334 in the chosen assay, and 325
accepted measurements. Nine assay records had a validity or duplicate flag.
The snapshot had already been filtered to exact nM IC50, so the upstream count
of censored values is unavailable. The builder rejects any censored rows it
encounters. Activity IDs and raw measured nM values are retained for each parent.

RDKit validates SMILES, chooses the fragment parent, and uncharges it where
possible. Canonical isomeric SMILES retain specified stereochemistry. The
within-assay nM median combines the three pairs of duplicate parent measurements
(83/90, 380/530, and 39/39 nM), then the builder computes pIC50 = 9 − log10(IC50 in nM).
The three pairs span at most 1.40-fold. No measurements from another assay are pooled.

The 70/15/15 split sorts Murcko scaffold groups by descending size and then
scaffold SMILES, assigning each to the split with the largest remaining target
count. Ties use train, validation, then test order. The algorithm uses group sizes
and identities. Every acyclic parent would share one empty-scaffold group;
there were none in this dataset.

| Split | Compounds | Scaffold groups | pIC50 range | Nearest-training Tanimoto, median |
| --- | ---: | ---: | --- | ---: |
| Train | 226 | 27 | 4.954–8.060 | — |
| Validation | 48 | 28 | 5.351–7.959 | 0.769 |
| Test | 48 | 29 | 5.000–7.538 | 0.780 |

Similarities use 2,048-bit, radius-2 Morgan fingerprints with chirality. Some
different-scaffold pairs still have high similarity (held-out maximum 0.987).
The frozen test rows are present in the exported dataset for reproducibility.
Model choice must use only training and validation. No model was evaluated today.

## Verification

All 30 repository unit tests passed. The app integration check matched
displayed ranks to the CLI export, exercised reversible filters and time/mouse
selectors, checked known and unknown compound evidence, and matched the actual
48 h CD74 map CSV to the full-source spot rows. The app's compound download
matched the reviewed CSV byte for byte. An offline rebuild reproduced both
model dataset files byte for byte. All 322 parent identities are unique, and
each of the 84 scaffold groups stays in one split.
