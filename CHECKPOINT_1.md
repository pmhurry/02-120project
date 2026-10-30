# Checkpoint 1: October 27–30, 2026

Plan for four sessions of roughly 45–60 minutes. These are effort targets, not a guarantee that data recovery will finish in one session. Each session includes explaining the work and reviewing changes before committing.

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
- [ ] Explain one result and the limitations in your own words.
- [ ] Update README, review the journal requirements, and keep the repository current.

Keep the dataset unchanged until provenance is clear. If recovery takes longer than planned, finish a checked subset workflow and track full coverage as follow-up work. This checklist is a plan; it does not replace the course-required Claude Code session logs.

October 30 outputs: run `python3 plot_checkpoint.py`. Figures and per-mouse
counts are in `results/`; interpretation and journal requirements are in
[PLOTTING.md](PLOTTING.md). README is updated. User explanation, journal
saving/review, and committing remain; these have not been marked complete.
