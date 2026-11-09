# Target ranking — checkpoint 2, session 3 (November 8, 2026)

Run offline with Python 3.10 or newer, standard library only:

```sh
python3 inspect_ranking.py
python3 -m unittest discover -s tests -v
```

The default external disease is hepatic fibrosis (`HP_0001395`), a chronic-fibrosis
context for this acute-injury experiment. Use `--disease MONDO_0019542` for acute
liver failure, `MONDO_0005359` for drug-induced liver injury, or `MONDO_0005155`
for cirrhosis. Each disease writes to its own directory; no sources are downloaded.
The default disease export is the checked deliverable for this session.

## Calculations and gates

For each time point, take the smaller of the two mouse contrasts, truncate negative
values to zero, and transform with `x/(1+x)`. Average the 48- and 72-hour components
with equal weight to get S. Missing mice/groups make the component missing. The
24-hour necrotic-region evidence remains in each profile as separate context.

T is the maximum true small-molecule tier using the fixed values in
[ENGINE_DESIGN.md](ENGINE_DESIGN.md). An explicit complete all-false tier record
is zero; absent records are missing. Unexpected or partial tier schemas fail.
D is the selected disease's association score. Missing associations stay missing.
The score is `100 * (0.60*S + 0.25*T + 0.15*D)`; no weights are renormalized.

The human-target ranking requires exactly one stable-ID human match, high
confidence, one-to-one homology, and no competing mouse stable ID in the collected
snapshot. This tests uniqueness within the snapshot, not all possible orthologues
in every database. MGI symbol fallbacks remain provisional. At least one later
time point must have positive contrasts in both mice. No detection threshold was
selected after looking at outcomes. Each profile retains detection and spot counts.

Exact score ties are resolved by ascending feature ID. The spatial-only screen
includes every feature with available S, including zeros, inconsistent contrasts,
and features excluded by mapping. The complete ranking requires mapping eligibility,
reproducible enrichment, and all three components. The component table lists all
applicable exclusion reasons, which overlap and must not be summed as unique genes.
Provisional mapping IDs remain visible but do not authorize entry to the ranking.

## Outputs and coverage

`results/ranking/HP_0001395/` contains:

- `components.csv`: all features, mapping audit, components, ranks, missingness,
  annotation-linked marker flags, and alternative-weight/time ranks.
- `spatial_screen.csv`: all available S values sorted by spatial rank.
- `complete_ranking.csv`: eligible complete-evidence rows sorted by priority.
- `evidence_profiles.jsonl.gz`: one profile per feature with each mouse's values,
  disease evidence-source/type scores, all tractability modalities, reported
  liabilities/references, drug mechanisms/indications/trial records, tissue summary,
  source links, and paths to full RNA/protein profiles with reliability annotations.
- `manifest.json`: fixed configuration, source versions, input/output hashes,
  coverage, and exclusion counts. External tables are rebuilt from checksum-checked
  snapshots; spatial output hashes are checked before ranking.

All **32,285** features have S. **11,753** have positive contrasts in both mice
at one or both later times. **4,789** pass the mapping gate; **2,248** enter the
complete hepatic-fibrosis ranking. No feature has a missing spatial component in
this dataset. The manifest reports each mapping/evidence exclusion separately.

The spatial and complete top tens have **zero overlap**. The spatial leaders
include Lyz2 (excluded from the human-target ranking because of homology ambiguity),
Col3a1 and Col1a2 (annotation-linked markers with explicit T=0), and Tmsb10 (only
provisional symbol mapping). This is a substantial coverage/knowledge bias: the
complete ranking favors mapped and previously studied targets. It does not show
that the excluded spatial leaders are biologically unimportant.

## Selected source-to-export checks

Checked Cd74, Lgals3, Ctss, Col3a1, and Lyz2 against the per-mouse spatial table,
orthology rows, tractability flags, and selected-disease association table. The
calculation can be followed with these unrounded source values:

| Feature | S | T | D | Priority | Complete rank |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cd74 | 0.475950609 | 1.0 | 0.024489389 | 53.924377374 | 1 |
| Lgals3 | 0.507754706 | 0.8 | 0.114035484 | 52.175814617 | 2 |
| Ctss | 0.510915358 | 0.8 | 0.014644507 | 50.874589102 | 3 |
| Col3a1 | 0.606381321 | 0.0 | 0.027193829 | 36.790786707 | 47 |
| Lyz2 | 0.612998078 | 0.4 | 0.003511009 | unavailable: mapping gate | unavailable |

These are hypotheses for follow-up, not validated treatment targets. In particular,
a true Approved Drug tier is a target-level tractability annotation, not approval
for liver injury or proof that inhibiting that target helps recovery. External
associations can contain animal/literature evidence; annotation-linked collagen
patterns are not independent validation.

Alternative ranks use spatial-heavy weights `(0.80, 0.15, 0.05)`, equal component
weights, and each later time point separately. A per-time ranking requires
reproducible positivity at that particular time; a blank rank can therefore mean
ineligibility rather than a numerical fall in rank. Weights were fixed before the
ranking and were not tuned to target identities. For example, Cd74 moves from default rank 1 to spatial-heavy rank 2; Ctss
moves from 3 to equal-component rank 12. Cd74 ranks 4 at 48 h and 1 at 72 h.
Deeper robustness review remains part of checkpoint 3.

## Validation and interpretation

All 29 unit tests pass, including hand calculations, opposite-sign mice, missing
mice/groups, ambiguous/low-confidence mappings, explicit-zero versus missing
tractability, missing disease values, and deterministic ties. A synthetic priority
example gives `S=.5, T=.8, D=.2 -> 53`. Safety records are never inputs to the score;
removing one cannot improve a score or rank.

Liability labels distinguish reported records, none reported in collected sources,
and unavailable data. Human tissue expression is contextual evidence, not a toxicity
prediction. Full profiles retain protein reliability and unusual measurement labels.
Absence of reports does not establish safety. Expression cannot determine whether
to inhibit or activate a target, and there are no healthy controls or perturbation
outcomes in this experiment. Student explanation/review was completed November 9; answers and corrections
are recorded in journal/checkpoint2_session3_notes.md.
