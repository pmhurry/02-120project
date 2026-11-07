# Checkpoint 3: Deploy and stress-test the engine — due November 20, 2026

Turn the [checkpoint 2 engine](CHECKPOINT_2.md) into a public, interpretable target
prioritization tool. Follow [ENGINE_DESIGN.md](ENGINE_DESIGN.md).

Four sessions of roughly 60–90 minutes on November 12, 14, 16, and 18.
Reserve November 19–20 for blockers/submission. Each session includes checks,
explanation, journal export, and review/commit. Reduce presentation polish if core
model validation needs more time; tissue overlays are optional.

## Session 1 — November 12: Feedback and robustness

- [ ] Review TA feedback and resolve model/data blockers before adding features.
- [ ] Compare default, spatial-heavy, and equal-component weights; report rank changes and top-list overlap.
- [ ] Compare 48 h and 72 h rankings and inspect agreement between mice; retain 24 h as distinct context.
- [ ] Check effects of low detection, orthology exclusions, annotation-linked genes, and external-data coverage bias.
- [ ] Freeze and version the reviewed rubric; record changes and rerun affected validation.

## Session 2 — November 14: Complete candidate evidence profiles

- [ ] Show component scores, weights, eligibility, missingness, and source versions next to each rank.
- [ ] Add a normal-human tissue profile with RNA units and protein reliability, and traceable reported-liability details.
- [ ] Keep drugs' overall clinical stages separate from indication-specific evidence and intervention direction.
- [ ] Make tissue/tractability review filters explicit and reversible, with excluded counts; missing safety evidence remains unknown.
- [ ] Check map scales and annotation meanings, and compare exported and displayed values.
- [ ] Review candidate-specific functional literature for a manageable initial shortlist, recording supporting and contradictory evidence.

## Session 3 — November 16: Deploy and verify

- [ ] Choose hosting based on measured memory/storage/startup requirements.
- [ ] Package verified derived spatial summaries and evidence tables; avoid loading all raw archives at every app startup.
- [ ] Document how the deployment obtains versioned data; do not depend on ignored local files.
- [ ] Deploy, record the URL, and test a fresh browser session.
- [ ] Verify ranking, filters, target lookup, maps, tissue/liability views, and downloads against CLI outputs.
- [ ] Resolve performance or data-access issues that prevent normal use.

## Session 4 — November 18: Methods and demonstration outline

- [ ] Explain normalization, spatial contrasts, mapping gates, component weights, missing-data policy, and sensitivity findings in the app.
- [ ] State sample size, differing annotations, cell mixtures, lack of controls/perturbations, and limitations of tissue/safety annotations.
- [ ] Update README with install, data retrieval, launch, deployed URL, and validated output versions.
- [ ] Draft a demo following one target from spatial signal through tractability and safety-review evidence to a testable hypothesis.
- [ ] Freeze core features and list remaining correctness issues.

## November 19–20 — Buffer and submission

- [ ] Fix correctness/deployment blockers and rerun affected checks.
- [ ] Verify URL, repository, sources, and required journals; submit checkpoint materials.

**Done means:** the public engine reproduces the reviewed rankings, makes trade-offs
and unknowns visible, and provides evidence for experimental follow-up.

Optional after core checks: tissue-image overlays or modest interface improvements.
No RL, docking, molecule generation, or clinical safety/efficacy prediction is required.
