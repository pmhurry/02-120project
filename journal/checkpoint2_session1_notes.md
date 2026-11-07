# Checkpoint 2, session 1 — November 6, 2026

Work notes, not a conversation export or evidence of student explanation.

The project direction is now exploratory spatial drug-target prioritization after
liver injury. Today stayed within data loading and validation.

Implemented a standard-library sparse archive loader preserving feature IDs and
symbols, explicit metadata barcode selection, and checksum validation. The audit
recovered all 17,370 spots and 32,285 features and reproduced all original counts
for the 348-spot subset. It stores 47,885,960 positive counts without expanding the
whole matrix. All 12 unit tests pass. Source files and subset results are unchanged.

Next session: library-size QC, full-data normalization and the fixed collagen score,
reference comparison, and saved sample summaries. Human gene mappings and external
target evidence remain future work.

Discussion prompts for the student:
- Why does more expression coverage not increase the number of biological replicates?
- Why preserve feature IDs when gene symbols can repeat?
- Why does regional enrichment not establish whether a drug should inhibit a gene?

Still required: student review and explanation, session export, and commit.

## Additional data gathering requested

Collected public MGI homology groups and HGNC identifier mappings, plus Open Targets
associations for hepatic fibrosis, cirrhosis, drug-induced liver injury, and acute
liver failure. Added reproducible snapshots, checksum verification, mapping coverage,
and source documentation in TARGET_DATA.md. The API's tied-score pagination omitted
some targets while repeating others; collection was changed to union overlapping
page-size passes and require exact unique-target totals. Returned trial subsets are
unioned, without claiming exhaustive trial coverage. No candidate ranking or new
expression comparison was performed.

## Engine pivot and file decisions

The user authorized the Spatial Target Prioritization Engine design, remaining
required data acquisition, checkpoint updates, and file cleanup. Added HPA 25.1
normal-human tissue RNA and protein snapshots, checksum manifests, an offline
summary builder, and checks for missing RNA versus measured zero. Protein gradient,
unavailable, and nonrepresentative annotations are retained separately from levels.

ENGINE_DESIGN.md specifies the future scoring rubric and safety-review constraints.
All checkpoints and README now reflect this direction; checkpoint 1 remains historical.
FILE_POLICY.md records retained baselines and disposable generated files. Today
still excludes implementation of the engine ranking/app and candidate analysis.
Student explanation, review, required session export, and commit remain pending.

Final preparation checks: all 18 unit tests pass; both external-data rebuilds work
offline; retained source checksums pass. Human tissue context covers 5,448 of the
5,583 collected targets with RNA and 4,362 with measured protein levels. Removed
only generated duplicate caches/scratch queries and the unused incomplete .venv.
Original data, all historical outputs, journals, and user edits were retained.

## Session closeout and explanation

The initial next-session paragraph above predates the engine pivot. The current
plan is authoritative in CHECKPOINT_2.md: November 7 builds mouse-level spatial
summaries; November 8 implements ranking; November 9 builds the interface; November
10 validates and prepares the checkpoint. Full-data collagen scoring is optional
context rather than the new target-ranking model.

Today's preparation gives us the following inputs:
- Full expression: 17,370 spots and 32,285 feature rows from the same six mice.
- External evidence: 8,849 disease associations for 5,583 distinct human targets.
- Normal-human context: RNA profiles for 5,448 collected targets and measured
  protein levels for 4,362, retaining missingness and reliability labels.

Why tissue expression is not a toxicity prediction: expression shows where a gene
is active or a protein is detected. It does not tell us what happens when a drug
changes its activity. Harm also depends on target function, inhibition versus
activation, dose, tissue exposure, and off-target drug effects. Missing evidence
cannot establish safety. These data support review flags and experiments, not
clinical safety claims.

The engine will rank hypotheses using visible spatial, tractability, and selected-
disease evidence components. Safety evidence remains alongside the rank; we do
not create a numerical safety guarantee. The planned initial weights are 60%, 25%,
and 15%, respectively, with sensitivity checks in checkpoint 3. No ranks exist yet.

The November 6 raw/readable Codex export was saved using the existing project
exporter. It is not a native Claude Code export. Student explanation/review and
confirmation of course journal acceptance cannot be performed on the student's
behalf. Implementation review and final verification are recorded separately.

Final full-data audit re-run: all six sample checksums pass, all 17,370 spots are
recovered, and every supplied subset count still matches. All 18 unit tests pass.
The implementation/planning changes are being saved in a local commit; no push
or course submission is performed. Pre-existing student edits in CHECKPOINT_1.md
are excluded from that commit; only the added historical-pivot notice is staged.
