# Checkpoint 3: Connect top genes to compounds and deploy — due November 20, 2026

Turn the [checkpoint 2 engine](CHECKPOINT_2.md) into a public, interpretable target
prioritization tool that also identifies compounds worth testing for its top genes.
Follow [ENGINE_DESIGN.md](ENGINE_DESIGN.md) for the existing gene ranking.

Predictive question: can a model trained on experimentally tested compounds
predict how strongly a compound excluded from training affects one selected
protein? Predict one clearly defined laboratory measurement, not liver-treatment
benefit. Begin with one target and one simple model.

New question: which compounds acting on the proteins made by our highest-ranked
genes have enough published evidence to justify a follow-up experiment?
Here, evaluating compounds means reviewing existing experiments; this project
does not perform laboratory tests or establish that a compound treats liver injury.

Work on the project every day from November 17 through the November 20 due
date, with one scheduled session per day. Each session includes checks,
explanation, journal export, and review/commit. Reduce presentation polish if core
model validation needs more time; tissue overlays are optional. Start with three
top genes and one or two compounds per gene; expand toward five genes only if time
and evidence allow. Record genes with no suitable compound rather than silently
replacing them. Compound evidence remains separate from the existing gene score.
Prioritize the prediction task over expanding the shortlist or presentation polish.
Reserve time on November 20 for final verification and submission.

## Predictive workflow and scope

Core deliverable: a reproducible dataset and honest held-out evaluation for one
protein and one activity endpoint. First audit ChEMBL using the selected UniProt
mapping; use BindingDB if needed and check for overlapping source measurements.
Choose a target for biological relevance and usable chemical diversity, not test
performance. Record feasibility criteria before training; no universal compound
count guarantees that a dataset is sufficient.

Use RDKit to standardize structures, then a Murcko scaffold split, 2,048-bit Morgan
fingerprints, and a Random Forest regressor. Compare against the training-mean
predictor. Screening a virtual library is conditional future work in checkpoint 4;
weak test performance remains a valid reported result. Preserve evaluation time
by reducing interface polish or shortlist breadth if necessary.

## Session 1 — November 17: Feedback and robustness

- [x] Review TA feedback and resolve model/data blockers before adding features.
- [x] Compare default, spatial-heavy, and equal-component weights; report rank changes and top-list overlap.
- [x] Compare 48 h and 72 h rankings and inspect agreement between mice; retain 24 h as distinct context.
- [x] Check effects of low detection, orthology exclusions, annotation-linked genes, and external-data coverage bias.
- [x] Freeze and version the reviewed rubric; record changes and rerun affected validation.
- [x] Freeze the initial top-gene list before reviewing compounds; record eligibility, ranks, and selection rules.
- [x] Check existing drug records for those genes and identify accessible sources of measured compound activity; record coverage gaps before committing to extra data collection.
- [x] Audit ChEMBL activity records for the initial targets, using BindingDB only if needed. Count usable unique compounds, distinct Murcko scaffolds, comparable experiments, and the range of measured activities after cleaning. Existing drug lists alone are not a training dataset.
- [x] Select one target and one measurement type (for example, inhibition concentration from comparable experiments). Record target species, assay scope, units, and feasibility criteria before training. If top targets lack adequate data, document that result; any broader-ranked fallback must be explicitly justified and retain its original rank. If no suitable dataset exists, report the prediction task as blocked by data rather than claiming an ML result.

November 17 results are recorded in the [ranking review and activity audit](journal/checkpoint3_session1_notes.md).

## Session 2 — November 18: Find and compare compounds for top genes

- [x] Show component scores, weights, eligibility, missingness, and source versions next to each rank.
- [x] Add a normal-human tissue profile with RNA units and protein reliability, and traceable reported-liability details.
- [x] Keep drugs' overall clinical stages separate from indication-specific evidence and intervention direction.
- [x] Make tissue/tractability review filters explicit and reversible, with excluded counts; missing safety evidence remains unknown.
- [x] Check map scales and annotation meanings, and compare exported and displayed values.
- [x] Review candidate-specific functional literature for a manageable initial shortlist, recording supporting and contradictory evidence.
- [x] Identify one or two compounds per selected gene with evidence that they act on its protein; record compound identifiers, source links, and whether they block, activate, or otherwise affect it.
- [x] Review experiments that blocked, removed, or activated each target and measured injury or healing. Expression alone cannot establish whether a gene causes damage or supports repair.
- [x] Assign each target an evidence label: "blocking may help", "activation may help", "mixed/context-dependent", or "unknown". Record citations, experimental action, measured outcome, species, cell type, injury model, and timing; distinguish acute injury from chronic fibrosis and retain contradictory findings.
- [x] Check each compound's action against that target evidence. Keep mismatched, mixed, and unknown cases visible as unresolved; do not recommend blocking a target solely because it ranks highly or is more expressed.
- [x] Save published activity measurements with units, experiment type, tested species/cell system, dose, and duration where available. Distinguish binding to a protein from changing a cell or tissue outcome.
- [x] Compare evidence of activity against the intended protein, effects on other proteins, relevant liver experiments, and reported liabilities. Use explicit evidence categories and unknowns rather than an unsupported efficacy or safety score.
- [x] Export a small compound-evidence table with source versions and reasons each compound merits follow-up or remains unresolved; check every initial entry against its source.
- [x] Prepare a separate model dataset with chemical structures, experimental values, assay identifiers, and source versions. Standardize units and compound identities; document duplicate/conflicting measurements, exclusions, and handling of values reported only as greater/less than a limit. Do not mix binding and inhibition measurements or treat unmeasured compounds as inactive.
- [x] Clean structures with RDKit: validate SMILES, apply a documented salt/parent and charge policy, preserve relevant stereochemistry, and save standardized compound identifiers. Canonical SMILES alone is not complete chemical standardization. Resolve duplicates and document conflicting measurements before splitting; aggregate only comparable replicates under a fixed rule.
- [x] Prefer one endpoint (for example, IC50) from comparable assays on the same species/protein, using high-confidence direct target assignments where applicable. Do not automatically pool IC50 potency with Ki/Kd affinity or cellular response measurements. Preserve assay identifiers, validity flags, source provenance, and exclusion counts.
- [x] For the initial regression dataset, retain positive exact numerical measurements with verified units. Exclude and count censored inequalities such as >10,000 nM; these contain bounds, not exact labels. Convert to pActivity = −log10(value in molar units), equivalently 9 − log10(value in nM), or use verified ChEMBL pChEMBL values for the chosen endpoint. Higher values mean greater measured potency/affinity. Log transformation does not guarantee normality; Random Forest does not require normally distributed targets.
- [x] Freeze training, validation, and final test groups using RDKit Murcko scaffolds, keeping standardized duplicate compounds together. Document split fractions, seed/assignment algorithm, handling of acyclic compounds with empty scaffolds, group sizes, and activity ranges. Verify no compound/scaffold overlap; inspect cross-group similarity because different scaffolds can still represent related chemistry. Fit data-dependent preprocessing on training groups only and keep final test results out of target/model selection.

November 18 results are recorded in the [evidence review and split notes](journal/checkpoint3_session2_notes.md).

## Session 3 — November 19: Deploy and verify

- [ ] Choose hosting based on measured memory/storage/startup requirements.
- [ ] Package verified derived spatial summaries and evidence tables; avoid loading all raw archives at every app startup.
- [ ] Document how the deployment obtains versioned data; do not depend on ignored local files.
- [ ] Deploy, record the URL, and test a fresh browser session.
- [ ] Verify ranking, filters, target lookup, maps, tissue/liability views, and downloads against CLI outputs.
- [ ] Add a compound section to selected target profiles and a downloadable evidence table; verify compound identity, action direction, measurements, and citations against the saved table.
- [ ] Show target action labels and their supporting/contradictory evidence in the app and download. Keep these separate from gene rank; verify that missing evidence stays unknown and a compound's action is not confused with whether that action helps.
- [ ] Resolve performance or data-access issues that prevent normal use.
- [ ] Compute 2,048-bit Morgan fingerprints with a documented radius (initially 2), chirality policy, and RDKit version; train a Random Forest regressor to predict the selected pActivity endpoint. Compare with a baseline that always predicts the training-set mean; choose settings using training/validation groups only.
- [ ] Save the training script, cleaned-data manifest, split assignments, model settings, dependency versions, and model artifact. Check deterministic rebuilding and separate measured values from model predictions in all outputs.

## Session 4 — November 20: Methods, demonstration, and submission

- [ ] Explain normalization, spatial contrasts, mapping gates, component weights, missing-data policy, and sensitivity findings in the app.
- [ ] State sample size, differing annotations, cell mixtures, lack of controls/perturbations, and limitations of tissue/safety annotations.
- [ ] Update README with install, data retrieval, launch, deployed URL, and validated output versions.
- [ ] Explain how compounds were selected, what published experiments actually measured, and why a highly ranked gene does not automatically justify blocking it.
- [ ] Draft a demo following one top gene from spatial signal to a compound, published evidence, unresolved questions, and a proposed laboratory experiment.
- [ ] Evaluate the frozen model once on the untouched test compounds. Report RMSE, MAE, and R² for both the Random Forest and training-mean predictor on the same test set, plus test size, scaffold coverage, activity range, and a predicted-versus-measured plot. Explain that a one-unit pActivity difference corresponds to a tenfold concentration ratio; report uncertainty in performance where practical without treating correlated compounds as independent. Retain weak or negative results; do not retune against the final test.
- [ ] Add a compact prediction view and downloadable results showing the target, predicted measurement and units/scale, model version, and whether the compound resembles training examples. Flag compounds outside the model's demonstrated scope; a similarity flag is not a calibrated confidence interval. Verify displayed predictions against saved outputs.
- [ ] Explain that held-out compounds already have experimental measurements used to evaluate the model; predictions for genuinely untested compounds remain unverified hypotheses. Predicting target activity does not establish blocking/activation direction, liver benefit, or safety.
- [ ] Freeze core features and list remaining correctness issues.

- [ ] Fix correctness/deployment blockers and rerun affected checks.
- [ ] Verify URL, repository, sources, and required journals; submit checkpoint materials.

**Done means:** the public engine reproduces the reviewed rankings, makes trade-offs
and unknowns visible, and connects selected top genes to a traceable compound
shortlist for experimental follow-up. Lack of suitable evidence is an explicit result.
The compound-activity model has a reproducible held-out evaluation against a
simple baseline, or an explicit data-feasibility failure with supporting counts.
A feasibility failure does not count as a completed predictive model.

Optional after core checks: tissue-image overlays or modest interface improvements.
Expression-signature comparison is a stretch goal only after core work: check
access and relevant cell systems first, keep mice separate, and describe the result
as opposing a region-associated pattern rather than restoring healthy tissue.
RL remains future work requiring experimental feedback. Before implementing it,
define measured outcomes for reduced injury, preserved liver function, and healing,
with time points and controls. Do not use reduced target expression or the existing
gene ranking as proof of benefit or as a substitute for experimental feedback.
Published evidence labels guide review; they are not measured rewards. If relevant
outcome data are unavailable, document the gap and keep RL as a proposed extension.
Docking, molecule
generation, and clinical safety/efficacy prediction are outside the core scope.
