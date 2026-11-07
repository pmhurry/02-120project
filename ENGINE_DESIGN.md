# Spatial Target Prioritization Engine — version 1 plan

Status: design agreed November 6, 2026; ranking implementation and validation are
scheduled for later checkpoint 2 sessions. No ranked targets have been produced.

## Goal and workflow

Prioritize testable therapeutic-target hypotheses after acute liver injury using
spatial RNA evidence, mouse–human mapping, tractability, and safety-review evidence.

Spatial evidence → human mapping → tractability assessment → safety evidence review
→ an explainable ranked list and candidate evidence profiles.

The output recommends follow-up experiments, not drugs for patients. The model is
an explicit scoring rubric, not a trained efficacy predictor or reinforcement
learning model. “Tractable” does not imply an oral pill; “no reported concern” does
not imply safety. Inhibiting an injury-associated gene could disrupt useful repair.

## Analysis population and comparisons

- Load all 17,370 metadata-matched spots and 32,285 original features from six mice.
- Fit no labels or weights using desired target identities. Preserve feature IDs.
- Start with all features for the spatial screen, not only known drug targets.
- Normalize each spot as ln(1 + 10,000 × count / all-feature library size).
  Exclude zero-library spots from expression calculations and report counts.
- For each feature and mouse, report annotated/other spot counts, mean normalized
  expression, raw-count detection fractions, and the annotated-minus-other mean
  difference. This difference is in log-normalized expression units, not log fold change.
- Keep mice separate and give mice equal weight. Do not calculate significance by
  pretending spots are independent animals. No healthy-versus-injured contrast exists.
- Use 48 h and 72 h for the main region-associated ranking, separately and with an
  equal-weight combined view. Show 24 h as necrotic-region context, not a third
  equivalent fibrosis label or longitudinal measurement.
- Do not call collagen/annotation agreement independent validation. Keep collagen
  genes visible and flagged as annotation-linked contextual markers.

## Eligibility and explicit missingness

Keep an audit table for every screened feature with eligibility/exclusion reasons.
The default human-target ranking requires a stable-ID, high-confidence one-to-one
mouse–human orthology match, uniquely resolved in the collected snapshot. Flag
one-to-many and lower-confidence mappings separately. MGI exact-symbol fallbacks
require manual review before entering the default human-target ranking.

A feature is eligible for the injury-region-enriched view when its difference is
positive in both mice at at least one of 48 h or 72 h. Negative or inconsistent
patterns remain available in the all-feature screen; they may be biologically
interesting and are not evidence of an irrelevant target.

Report low detection and spot counts. Do not add an outcome-selected detection
threshold. Any later QC threshold must be documented and applied before ranking.
Missing groups, missing annotations, ambiguous mappings, and missing external data
must remain distinct from measured zeros or explicit negative tractability flags.

## Initial transparent ranking rubric

For a time point t, let d_t be the smaller of the two within-mouse expression
differences for a feature. Define:

    S_t = max(0, d_t) / (1 + max(0, d_t))
    S = (S_48 + S_72) / 2

This conservative spatial component rewards an effect observed in both mice; it
is descriptive, bounded from 0 to 1, and is not a probability or confidence interval.
A missing mouse/group makes its time-point component unavailable, not zero.

For the default small-molecule tractability component T, take the highest reported
true tier from Open Targets: Approved Drug = 1.0; Advanced Clinical = 0.8;
Phase 1 Clinical = 0.7; High-Quality Ligand = 0.6; Structure with Ligand = 0.4;
High-Quality Pocket or Med-Quality Pocket = 0.3; Druggable Family = 0.2.
An explicit all-false record is 0; an unavailable record is missing. These are
project-defined heuristic weights, not experimentally calibrated success rates.
Show other modalities separately; do not assume oral bioavailability.

D is the Open Targets association score for one explicitly selected disease.
Default context: hepatic fibrosis (HP_0001395), clearly labeled as external chronic
fibrosis context for an acute-injury experiment. Keep acute liver failure,
drug-induced liver injury, and cirrhosis scores separately selectable. Preserve
source/type scores; do not describe the aggregate as purely human clinical evidence.
Absence from the collected disease table is missing, not proof of no association.

For records with complete S, T, and D:

    priority = 100 × (0.60 × S + 0.25 × T + 0.15 × D)

Display all components and the selected disease next to the rank. Show a spatial-only
list for features without complete external evidence. Do not silently renormalize
weights when a component is missing. Resolve exact ties by stable feature ID.
The model favors previously studied, mapped genes: explicitly compare its shortlist
with the spatial-only list and report this coverage/knowledge bias.

## Safety review remains visible beside every rank

Do not add a fabricated “safety probability” or reward missing safety reports.
Display Open Targets reported liabilities with source references, known compound
mechanisms/indications and trial links, and Human Protein Atlas normal-tissue RNA
and protein expression. Join human tissue data by human Ensembl ID.

Show liver nTPM, maximum measured non-liver nTPM and its tissue(s), the number of
non-liver tissues at or above the predeclared descriptive 1 nTPM threshold, and a
full tissue profile. This threshold is a display convention, not a toxicity cutoff.
Show protein levels and reliability; keep gradient/unavailable/nonrepresentative
annotations separate from Low/Medium/High/Not detected.

Use labels such as “reported liabilities present,” “none reported in collected
sources,” and “data unavailable,” with coverage indicators. Never label a target
“safe.” Tissue expression is a reason for follow-up, not demonstrated on-target
toxicity; it is also distinct from off-target drug binding and dose/exposure effects.
Any user safety filter must be explicit, reversible, and show excluded counts.

## Required checks and sensitivity analysis

- Barcode/feature alignment, sparse zeros versus missingness, and hand-calculated
  normalization; identical profiles; known contrasts; zero libraries; missing groups.
- Exact mouse-level contrasts and component scores on small synthetic examples.
- Mapping ambiguity/confidence gates, null handling, deterministic ties, and ranking
  agreement between CLI exports and the app. Adding a missing safety record must
  never improve rank or create a “safe” label.
- Show rank changes under spatial-heavy (0.80, 0.15, 0.05) and equal-component
  (1/3, 1/3, 1/3) weights, and under each individual time point.
- Review the effect of annotation-linked collagen markers and external evidence
  coverage. Do not tune the model to make a preferred drug or gene rank highly.

## Final deliverable

A Streamlit app with an auditable ranked table, per-target evidence profile,
within-mouse maps/comparisons, normal-human tissue context, downloadable evidence,
and explicit methods/limitations. Aim to review up to 5–10 candidates; fewer are
acceptable. Each profile states what is observed, what remains unknown, and one
functional experiment that could test the hypothesis and intervention direction.

Tissue-image overlays, ligand docking, molecule generation, new training datasets,
RL, and clinical toxicity/efficacy prediction are outside the required scope.
