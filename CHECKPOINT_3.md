# Checkpoint 3: Deploy a complete first version — due November 20, 2026

Turn the [checkpoint 2 prototype](CHECKPOINT_2.md) into a usable deployed app with
checked results, clear methods, and a reproducible setup.

Plan for four sessions of roughly 60–90 minutes, about 4–6 hours total. Suggested
dates are November 12, 14, 16, and 18; the days between are unscheduled. Reserve
November 19–20 for fixes and submission. Each session includes verification,
explaining the changes, saving the required journal, and reviewing and committing.

## Session 1 — November 12: Address feedback and data gaps

- [ ] Review TA feedback if available; separate essential corrections from optional enhancements.
- [ ] Resolve any remaining full-data loading or scientific-model blockers from checkpoint 2 before adding features.
- [ ] Check all six samples and record the data coverage and exclusions actually used.
- [ ] Choose the deployment service and check its memory, dependency, and file-size constraints.
- [ ] Decide how the deployment obtains verified data without depending on ignored local ZIPs or temporary file paths.

## Session 2 — November 14: Make maps and comparisons clear

- [ ] Improve selector behavior, legends, units, and explanations of gene expression and score values.
- [ ] Use comparable color scales when comparing the same measurement across samples; label any rescaling explicitly.
- [ ] Handle missing genes, absent data, and unavailable comparisons clearly.
- [ ] Align a tissue image using the archive's pixel coordinates and scale factors, and visually check orientation against recognizable tissue boundaries.
- [ ] Keep the coordinate-only map usable if image alignment remains uncertain; document that limitation.

## Session 3 — November 16: Deploy and check the public workflow

- [ ] Deploy the app and record the public URL.
- [ ] Verify installation, data access, caching, and startup in the hosted environment.
- [ ] Open a fresh browser session and test the sample selectors, map modes, spot lookup, and comparison views.
- [ ] Compare a small set of displayed spot values and group summaries against calculations outside the app.
- [ ] Address slow interactions or memory problems that prevent normal use; measure before optimizing further.

## Session 4 — November 18: Finish methods and the demonstration outline

- [ ] Include the scientific question, data sources, normalization, score formula/reference, and limitations in the app.
- [ ] Explain differing label meanings, the lack of longitudinal spot tracking, and the limits of two mice per time point.
- [ ] Update README with installation, data retrieval, launch instructions, and the deployed URL.
- [ ] Draft a short demonstration outline showing the question, one map, one comparison, and one limitation.
- [ ] Review outstanding bugs and freeze the core feature set for the final checkpoint.

## November 19–20 — Buffer and checkpoint submission

- [ ] Fix deployment or scientific-correctness blockers and retest the affected workflow.
- [ ] Verify the public URL, repository, and journal files, then submit the required checkpoint materials.

**Done means:** The core scientific workflow is publicly usable, its main outputs
have been checked, and another person has instructions to run it locally.

## Optional work only after the core workflow passes

- [ ] Add a within-sample neighborhood explorer with an explicit distance or neighbor rule; avoid claims of cell-to-cell interaction or physical distances without calibration.
- [ ] Add a results download or modest interface improvements if time remains.

Do not let optional features consume the submission buffer. Use
[checkpoint 4](CHECKPOINT_4.md) for final findings, reproducibility, the video, and
submission rather than major new functionality.
