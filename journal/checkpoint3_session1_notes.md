# Checkpoint 3 ranking review — November 17, 2026

The review uses the checked-in `ranking-v1` hepatic fibrosis (HP_0001395)
component tables and per-mouse evidence profiles. The existing default is
60% spatial, 25% tractability, and 15% disease association. All 30 unit tests passed.

| Variant | Eligible features | Shared with default top 10 | CD74 rank | LGALS3 rank | CTSS rank |
| --- | ---: | ---: | ---: | ---: | ---: |
| Default | 2,248 | 10 | 1 | 2 | 3 |
| Spatial-heavy (80/15/5) | 2,248 | 5 | 2 | 3 | 4 |
| Equal components | 2,248 | 7 | 1 | 3 | 12 |
| 48 h only | 1,997 | 7 | 4 | 3 | 5 |
| 72 h only | 2,059 | 9 | 1 | 2 | 4 |

The 48 h and 72 h top tens share six features. Their rankings use the corresponding
time point's positive-replication gate, so eligible pools differ. Across 32,285
features, Pearson correlations between mice's annotated-minus-other differences
were 0.956 at 48 h and 0.977 at 72 h. The mice disagreed on whether a contrast
was strictly positive for 4,149 and 3,697 features, respectively. The 24 h
necrotic-region contrasts provide separate context.

Applying an exploratory minimum of 10% detection in the annotated region of
each 48/72 h mouse retained 1,395 of 2,248 complete-ranked features and all of
the default top ten. This was a sensitivity check. Excluding the three
annotation-linked genes (COL1A1, COL3A1, COL1A2, ranked 19, 47, and 51) also
preserved the default top ten.

Only 4,789 of 32,285 features passed the orthology gate. Among the spatial
top ten, Lyz2 and Tmsb10 failed that gate, and C1qb lacked tractability.
Across all features, 28,386 lack a selected-disease association and 26,802
lack tractability. These overlapping counts include unmapped features.
Coverage limits which strong spatial signals can enter the combined ranking.

## Initial compound-audit shortlist

Selection rule: retain the first three default complete-ranking rows in order.
Each meets the stable-ID orthology, positive spatial evidence, tractability, and
selected-disease gates. Sensitivity results and existing drug records did not
change selection.

| Rank | Target | Human Ensembl ID | Open Targets drug or clinical candidate records |
| --- | --- | --- | --- |
| 1 | CD74 | ENSG00000019582 | 2 (repotrectinib, milatuzumab) |
| 2 | LGALS3 | ENSG00000131981 | 3 (davanat, belapectin, olitigaltin) |
| 3 | CTSS | ENSG00000163131 | 1 (petesicatib) |

The counts are from the saved Open Targets 26.09 evidence profiles. Compound
mechanisms and relevance require source review. ChEMBL's target API returned
human Cathepsin S (UniProt P25774) as single-protein target CHEMBL2954.
The preliminary API query returned 2,059 activity rows labeled IC50 under
ChEMBL assay type B, with positive exact values in nM. This is a row count
before direct-assignment, comparability, and compound-level checks.
The cleaned counts and modeling decision are recorded below.

Checkpoint 3 was rescheduled for daily work from November 17 through the
November 20 due date, including final verification and submission on November 20.

## TA feedback and responses

- **How was the injury caused?** The source study induced acute liver injury in
  mice by injecting acetaminophen (APAP). The Visium liver samples used here
  were collected 24, 48, and 72 hours later, with two mice per time point.
- **Which molecule does tractability measure against?** The ranking uses
  Open Targets small-molecule tractability evidence for the mapped human
  protein. It assigns the highest reported tier, drawing on evidence such as
  known drugs, ligands, or binding pockets. The score is target-level and
  modality-specific. It does not measure the potency of any one compound.
- **Which cells are annotated?** The labels apply to Visium spots, which can
  contain RNA from multiple cells. The published methods describe manual
  segmentation of pericentral necrotic regions at 24 h and a collagen RNA
  fraction threshold for fibrogenic spots at 48/72 h. Our analysis uses the
  supplied binary labels without independently reconstructing them. The
  comparison spots are other spots on the same injured liver section.

Source for injury and annotation methods:
[The spatiotemporal program of zonal liver regeneration following acute injury](https://weizmann.elsevierpure.com/ws/portalfiles/portal/111312424/is_Stem-Cell-Stem_The%20spatiotemporal%20program_AM_%2022.pdf).
The TA feedback also covered the dataset dimensions, UMI count interpretation,
and the student explanation of normalization and ranking. The feedback shared
in this session prompted documentation clarifications. The team retained and
froze ranking-v1 (60/25/15). All 30 tests passed and the rebuilt components,
complete ranking, spatial screen, and evidence profiles matched byte for byte.

### Compound feasibility criteria

The first model will use direct human single-protein biochemical IC50 in nM.
Audit exact positive measurements only, require ChEMBL target confidence 9,
and exclude flagged records. Keep assay families separate until their
experimental descriptions support pooling. Review usable structures, the
activity range, and whether scaffold group sizes support meaningful separate
training, validation, and test sets. Require at least 100 standardized
compounds, 20 nonempty scaffolds, and a two-log-unit activity range as initial
project thresholds. Inspect whether groups can produce informative splits
before training. These are feasibility thresholds for this project.

### Audit results and modeling decision

ChEMBL 37 mapped CD74 to P04233/CHEMBL4692, LGALS3 to P17931/CHEMBL4531,
and CTSS to P25774/CHEMBL2954. Initial activity criteria were assay type B,
positive exact IC50, and standardized nM units. The cleaned counts below
require a confidence-9 assay, a valid structure, and no validity or potential
duplicate flag. RDKit 2026.3.3 standardizes the fragment parent and neutralizes
where possible while preserving stereochemistry in canonical identifiers.
Counts are unique parents and distinct nonempty Murcko scaffolds. Ranges use
per-assay compound medians. Cross-assay rows are a coverage check.

| Target | Initial rows | Accepted rows | Assays with accepted data | Unique compounds | Scaffolds | Range (nM) |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| CD74 | 25 | 25 | 1 | 25 | 7 | 410–4,400 |
| LGALS3 | 496 | 450 | 9 | 430 | 112 | 5–11,110 |
| CTSS | 2,059 | 1,483 | 94 | 1,313 | 581 | 0.029–78,000 |

Select **human galectin-3 (LGALS3, original rank 2)** and the IC50 for
inhibition of recombinant galectin-3 binding to biotinylated asialofetuin,
measured by HTRF competition. Use only CHEMBL5737905, from CHEMBL5729012.
The one assay provides 325 accepted records, 322 standardized compounds,
84 nonempty scaffolds, no acyclic compounds, and a range of 8.7–11,110 nM
(about 3.11 log units). Three parent compounds have two measurements each,
with nM pairs of 83/90, 380/530, and 39/39. The audit takes the within-assay
median in nM. A group-size-only check found a possible scaffold-disjoint
allocation of 225/48/49 compounds and 26/29/29 scaffolds. The actual split
and activity distribution checks belong to dataset preparation.

CD74 missed the feasibility thresholds. CTSS has more records across
assays, but its largest individual assay has 83 compounds. LGALS3 is the
highest-ranked target with enough data from one documented assay. BindingDB
was unnecessary for this initial audit. The model endpoint is specific to
the assay. Model fitting and evaluation are scheduled separately.

Reproduce the audit with RDKit 2026.3.3 and the preserved
[ChEMBL snapshot](../data/external/chembl/chembl37_shortlist.tar.gz).
From the repository root, extract the archive to a temporary directory and run
`python3 scripts/audit_compound_activity.py <directory>`. Add
`--assays CHEMBL5737905` to reproduce the chosen assay's counts. See the
[audit summary](../results/compound_activity/feasibility.json) for input hashes.
[ChEMBL assay](https://www.ebi.ac.uk/chembl/explore/assay/CHEMBL5737905).

### TA practice quiz

The student identified APAP, UMI counts, and the three sampling times.
Feedback supplied the matrix dimensions, two different mice per time point,
and the interpretation of spot-level counts. The student identified
glutathione's role and correctly distinguished necrotic regions at 24 h from
collagen-linked labels at 48/72 h. Feedback clarified CYP2E1 and NAPQI, why
injury concentrates near central veins, and why the labels describe Visium
spots rather than individual cells or a severity scale.

The student correctly recognized equal normalized expression for 10/1,000
and 20/2,000, recognized disagreement between mice in the example contrast,
and selected the 0.6 tractability tier. Feedback distinguished the
within-mouse means from the across-mouse minimum, and clarified that the
tractability score applies to the mapped human protein. The galectin-3
selection and assay-specific endpoint were explained after the student
asked for the rationale.
