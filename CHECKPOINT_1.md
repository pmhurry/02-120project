# Checkpoint 1: Due November 1, 2026, at 11:59 p.m. (America/New_York)

**Historical checkpoint — retained as completed work.** The November 6 project
pivot is the [Spatial Target Prioritization Engine](ENGINE_DESIGN.md). The subset
loader, collagen score, figures, and provenance below are a reproducibility baseline;
they are not the new target-ranking model. Current plans are in checkpoints 2–4.
No past work or submission status is changed by this pivot.

The deadline was extended from October 30 to November 1. Keep the October 27–30
work record below; use November 1 to finish review and submission.

The original plan covered four sessions of roughly 45–60 minutes, October 27–30.
Use an additional 45–60-minute session on November 1 for the checks and scientific
summary below. These are effort targets, not a guarantee that data recovery will
finish in one session. Each session includes explaining the work and reviewing
changes before committing.

## October 27 — Load and check the supplied data

- [x] Inspect file structure, coverage, time points, samples, and marker availability.
- [x] Implement barcode-based loading with count and metadata validation.
- [x] Preserve duplicate gene symbols and distinguish missing expression from zero.
- [x] Add a runnable coverage summary and synthetic alignment checks.
- [x] Run the summary yourself and explain how expression columns match metadata.
- [x] Review changes and commit with a message in your own words.

## October 28 — Investigate coverage and provenance

- [x] Investigate how the 348 spots were selected; record unknowns if no history exists.
- [x] Inspect the authors' archive and determine which files provide full counts and images.
- [x] Obtain and reconcile full data if practical, keeping source/version information.
- [x] Confirm annotation provenance and coordinate units or record them as unresolved.
- [x] Decide whether checkpoint 1 uses full data or an explicitly limited subset.

October 28 findings and reproducible audit: [DATA_PROVENANCE.md](DATA_PROVENANCE.md).
The project owner confirmed that every 50th spot was retained to fit GitHub's
file-size limit, rather than selected by biological quality.
Checkpoint 1 will retain the explicitly limited 348-spot workflow for normalization
and scoring checks. Recovered full archives are kept separately; switching to full
coverage requires a sparse-data loader and validation before app development.

## October 29 — Define normalization and the score

- [x] Explain library size and implement an explicit normalization method.
- [x] Choose a small marker panel for a scientific reason, before testing its outcome.
- [x] Define the score, its reference, and its interpretation in writing.
- [x] Check identical profiles, known contrasts, and zero-count/zero-variance behavior.
- [x] Explain why agreement with collagen-derived annotations is not independent validation.

October 29 implementation and explanation: [SCORING.md](SCORING.md). The panel
was fixed before today’s score run, but had already been explored on October 27;
it is not a blinded selection. All eight tests pass. Learning quiz and user review
remain for this session.

## October 30 — Plot, review, and finish the checkpoint

- [x] Plot annotations and one gene for an individual mouse.
- [x] Produce a normalized group comparison with sample/spot counts.
- [x] Mark missing expression clearly and keep samples spatially separate.
- [x] Explain one result and the limitations in your own words.
- [x] Update README, review the journal requirements, and keep the repository current.

Keep the dataset unchanged until provenance is clear. If recovery takes longer than planned, finish a checked subset workflow and track full coverage as follow-up work. This checklist is a plan; it does not replace the course-required Claude Code session logs.

October 30 outputs: run `python3 plot_checkpoint.py`. Figures and per-mouse
counts are in `results/`; interpretation and journal requirements are in
[PLOTTING.md](PLOTTING.md). The user confirmed that all October 30 tasks,
including the explanation, README update, journal review, and repository upkeep,
are complete.

## November 1 — Final review and submission by 11:59 p.m.

- [x] Run `python3 inspect_data.py`, `python3 inspect_scores.py`, and `python3 -m unittest discover -s tests -v`; review any failures before submission.
- [x] Regenerate the checkpoint figures with `python3 plot_checkpoint.py` and confirm that the maps, legends, and group counts match the documented subset workflow.
- [x] Check one mouse/gene group mean and spot count from `results/group_summary.csv` against the displayed comparison.
- [x] Write a short checkpoint summary in your own words: the scientific question, what was built, one numerical finding, and the subset, annotation, and sample-size limitations.
- [x] Review the normalization and score formulas with one small hand-calculated example; explain what a score of zero means.
- [x] Record the next priorities for checkpoint 2: sparse full-data loading, barcode/count reconciliation, and full-coverage model checks before building the interface.
- [x] Set up the build journal, export the four previous Codex sessions, and commit and push the setup.
- [x] Review README and checkpoint materials for completeness; review the readable journal exports.
- [x] Commit and push any final checkpoint changes so the journal refreshes.
- [x] Submit the required checkpoint materials and repository link on Canvas by 11:59 p.m. (America/New_York), and verify submission status.

The build journal is now configured: raw Codex logs are in `journal/codex/` and
readable transcripts are in `journal/readable/`. The pre-commit hook refreshes
them automatically. Keep `journal/chat_links.md` current if using a chat app.

November 1 completion notes: the user reported finishing the first three checks.
The scientific summary, feedback, and normalization/score explanation are saved
in [journal/session5.txt](journal/session5.txt). Both hand-calculated normalized
counts were 100 before the logarithm; a score of zero means average standardized
panel expression relative to the reference, not absent collagen. Checkpoint 2
priorities are sparse full-data loading, barcode/count reconciliation, and
full-coverage model checks before interface development (see [CHECKPOINT_2.md](CHECKPOINT_2.md)).
The completed checklist above records the student's report of final review,
commit/push, and Canvas submission; the submission receipt was not independently checked.
