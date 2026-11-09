# Checkpoint 2: Local Spatial Target Prioritization Engine — due November 10, 2026

Build a checked local scoring/ranking prototype following [ENGINE_DESIGN.md](ENGINE_DESIGN.md).
Question: which genes show reproducible injury-region expression patterns and
warrant investigation as human therapeutic-target hypotheses?

Keep five sessions, November 6–10 (America/New_York), roughly 60–90 minutes each.
Work one session at a time. Session 1 covers data preparation and planning;
ranking and app implementation belong to sessions 3 and 4. Save the required journal, explain the
calculations, and review/commit each session. Dates are effort targets; reduce
interface polish if the core model needs more time. There is no extra buffer day.

| Session | Date | Focus |
| --- | --- | --- |
| 1 | November 6 | Validated full data, external evidence, and revised scope |
| 2 | November 7 | Spatial evidence and mouse-level QC/normalization |
| 3 | November 8 | Implement and validate the ranking model |
| 4 | November 9 | Minimal Streamlit ranking and target-evidence interface |
| 5 | November 10 | End-to-end checks, TA preparation, and submission |

## Session 1 — November 6: Data and design

- [x] Review the checkpoint 1 normalization/score and preserve it as a baseline.
- [x] Add a sparse loader preserving feature IDs and duplicate symbols.
- [x] Verify all 17,370 metadata barcodes and every count in the 348-spot subset.
- [x] Gather MGI/HGNC mappings and Open Targets liver-condition associations, drugs, tractability, and reported liabilities.
- [x] Gather and check normal-human tissue RNA/protein data, including missingness and reliability.
- [x] Define the engine's components, mapping gates, missing-data rules, and limits in ENGINE_DESIGN.md.
- [x] Update the roadmap and document keep/delete decisions in FILE_POLICY.md.
- [x] Review the implementation and document why tissue expression is not a toxicity prediction.
- [x] Save the available Codex session export (raw and readable); current course setup explicitly supports Codex (verified November 7).
- [x] Complete the guided explanation/review quiz; revisit biological replicates, cross-species inference, and annotation circularity using the feedback in journal/session6.txt.
- [x] Commit the reviewed implementation and planning changes (guided student review recorded in journal/session6.txt).

## Session 2 — November 7: Spatial evidence

- [x] Review library sizes and zero-library spots by mouse; report retained/excluded counts and any QC rules.
- [x] Apply ln(1 + 10,000 × count/library) using all features in each library total.
- [x] Calculate per-feature, per-mouse annotation-group means, differences, detection fractions, and group counts.
- [x] Keep 24 h necrotic-region context distinct from 48/72 h annotation-based rankings.
- [x] Save all-feature spatial summaries; give mice equal weight and show each mouse.
- [x] Verify hand-calculated normalization, alignment, identical profiles, known contrasts, zero libraries, and missing groups.
- [x] Compare selected full-data values with the checked subset; explain coverage/reference effects.

Session 2 outputs and validation: [SPATIAL_EVIDENCE.md](SPATIAL_EVIDENCE.md).
- [x] Complete the guided student explanation/review; corrections are recorded in journal/checkpoint2_session2_notes.md.
- [x] Refresh the raw/readable journal exports.
- [x] Commit and push the reviewed session 2 work.

The original collagen score is optional contextual output, not a prerequisite for
the new ranking model. Keep it unchanged until any full-data reference is explicitly
computed and saved. Never switch dataset versions silently.

## Session 3 — November 8: Scoring and ranking

- [x] Implement the stable-ID, high-confidence one-to-one mapping gate and report all exclusion reasons.
- [x] Compute the documented spatial S, tractability T, selected-disease D, and weighted priority score.
- [x] Produce both a spatial-only screen and a complete-evidence ranking; keep incomplete evidence visible.
- [x] Attach tissue-expression context, reported liabilities, mechanism/indication evidence, and source links without inventing a safety score.
- [x] Save reproducible component tables, ranks, configuration, source versions, and coverage counts.
- [x] Verify components on synthetic examples, mapping ambiguity, missingness, deterministic ties, and that missing safety evidence confers no benefit.
- [x] Check a few exported targets manually; do not tune weights to preferred outcomes.

Session 3 outputs and validation: [RANKING.md](RANKING.md).
- [x] Complete the student explanation/review (November 9); answers and corrections are recorded in journal/checkpoint2_session3_notes.md.
- [x] Refresh journal exports and commit/push the reviewed session (November 9).

## Session 4 — November 9: Minimal interface

- [ ] Build a local Streamlit app with ranked targets, component explanations, and explicit disease/time context.
- [ ] Add target lookup, evidence profile, and mouse/time selectors compatible with each other.
- [ ] Map annotations or selected target expression for one mouse at a time; preserve aspect ratio and distinguish missing from zero.
- [ ] Show each mouse's group difference and sample/spot counts, plus tissue-expression and liability context.
- [ ] Provide source links, known drug mechanisms/indications, missing-data labels, and an evidence-table download.
- [ ] Compare several displayed ranks, barcodes, and values with saved CLI outputs.

## Session 5 — November 10: Review, TA preparation, and submission

- [ ] Run data checks, model checks, and the complete local workflow; fix blockers.
- [ ] Verify that the app reproduces exported components/ranks and states the weights and source versions.
- [ ] Confirm that “none reported” and “missing” are never presented as “safe.”
- [ ] Update README with launch commands, actual coverage, current outputs, and known limitations.
- [ ] Prepare an explanation of the question, one candidate hypothesis, model calculations, and one follow-up experiment.
- [ ] Arrange/prepare for the TA check-in during November 4–13; record actual feedback when received.
- [ ] Review course submission/journal instructions, review and commit changes, and submit required materials.

**Done means:** a checked local engine ranks hypotheses with traceable components,
shows spatial and safety-review evidence, and can be explained. All-feature coverage
and excluded-target counts are explicit. Deployment and deeper sensitivity review
belong to [checkpoint 3](CHECKPOINT_3.md); no efficacy or safety claim is implied.
