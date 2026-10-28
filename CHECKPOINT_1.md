# Checkpoint 1: October 27–30, 2026

Plan for four sessions of roughly 45–60 minutes. These are effort targets, not a guarantee that data recovery will finish in one session. Each session includes explaining the work and reviewing changes before committing.

## October 27 — Load and check the supplied data

- [x] Inspect file structure, coverage, time points, samples, and marker availability.
- [x] Implement barcode-based loading with count and metadata validation.
- [x] Preserve duplicate gene symbols and distinguish missing expression from zero.
- [x] Add a runnable coverage summary and synthetic alignment checks.
- [ ] Run the summary yourself and explain how expression columns match metadata.
- [ ] Review changes and commit with a message in your own words.

## October 28 — Investigate coverage and provenance

- [ ] Investigate how the 348 spots were selected; record unknowns if no history exists.
- [ ] Inspect the authors' archive and determine which files provide full counts and images.
- [ ] Obtain and reconcile full data if practical, keeping source/version information.
- [ ] Confirm annotation provenance and coordinate units or record them as unresolved.
- [ ] Decide whether checkpoint 1 uses full data or an explicitly limited subset.

## October 29 — Define normalization and the score

- [ ] Explain library size and implement an explicit normalization method.
- [ ] Choose a small marker panel for a scientific reason, before testing its outcome.
- [ ] Define the score, its reference, and its interpretation in writing.
- [ ] Check identical profiles, known contrasts, and zero-count/zero-variance behavior.
- [ ] Explain why agreement with collagen-derived annotations is not independent validation.

## October 30 — Plot, review, and finish the checkpoint

- [ ] Plot annotations and one gene for an individual mouse.
- [ ] Produce a normalized group comparison with sample/spot counts.
- [ ] Mark missing expression clearly and keep samples spatially separate.
- [ ] Explain one result and the limitations in your own words.
- [ ] Update README, review the journal requirements, and keep the repository current.

Keep the dataset unchanged until provenance is clear. If recovery takes longer than planned, finish a checked subset workflow and track full coverage as follow-up work. This checklist is a plan; it does not replace the course-required Claude Code session logs.
