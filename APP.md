# Local target-evidence app — November 9, 2026

Python 3.11+ is needed for the pinned interface dependencies. The existing CLI
analysis still uses Python 3.10+ and the standard library.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/streamlit run app.py --server.address localhost
```

Open the local URL printed by Streamlit. The interface is local and read-only.
It reads `results/ranking/HP_0001395/` and checks the export hashes against the
saved manifest. No model is recalculated or external service queried by the app.
Restart Streamlit after regenerating exports or replacing data; its bounded caches
retain profiles and up to two loaded mouse archives during a running session.

Only the checked **hepatic fibrosis** export is offered. This chronic-disease
evidence is context for the acute-injury experiment. Complete priority ranks
combine 48/72 h with the saved S/T/D weights 0.60/0.25/0.15. Time/mouse controls
change the map and mouse evidence table, never silently reinterpret the ranking.
24 h remains separate necrotic-region context.

The three views show complete-evidence targets, the spatial-only screen, and the
all-feature mapping audit. Search mouse/human symbols or IDs literally, then select
the stable feature ID. Duplicate symbols stay separate. Filtering keeps original
ranks. The visible ranking table shows up to 250 matching rows; the selector and
CSV download include every match. Empty numeric cells mean unavailable; measured
zero components remain numeric zero. Exclusion reasons remain visible.

Each profile shows both mice at the selected time, their group means, differences,
detection fractions, and retained spot counts. Spot counts are not mouse replicate
counts. Annotation maps need only metadata. Expression maps load and checksum-check
one original full-data ZIP on demand from `data/source/` (see
[archive setup](DATA_PROVENANCE.md)). They normalize counts with **all features**
in each spot's library, never the historical 348-spot subset. Map data downloads
include full barcodes and coordinates, counts, library sizes, and normalized values.
Equal x/y scaling preserves aspect ratio; y increases downward. Color scales vary
by target/mouse, so compare numerical values when switching maps. Zero libraries
are missing and shown as gray crosses; measured zero counts use the zero color.
If an archive is unavailable, the app labels the failure and falls back to an
annotation map while keeping the rest of the target profile available.

Tissue summaries retain RNA/protein coverage and protein reliability counts.
Expandable evidence records provide liability references, drug mechanisms,
indications, clinical records, disease-source scores, and tractability. Source
buttons and the full profile JSON download preserve traceability. The app does
not calculate a safety score: absent reports cannot establish safety. Approved
Drug tractability does not establish an indication for liver injury or treatment
direction. Annotation-linked collagen markers have a circularity notice.

## Checks

```sh
python3 -m unittest discover -s tests -v
.venv/bin/python scripts/check_app.py
# Requires the 48_m4 source archive; also renders the real expression layer:
.venv/bin/python scripts/check_app.py --expression
```

The local Streamlit server launches and its health endpoint returns `ok`.
Thirty unit tests pass. Streamlit AppTest checks the top five displayed ranks
against `complete_ranking.csv`, Cd74/Lgals3/Ctss/Col3a1 scores and ranks, excluded
Lyz2, all three time selectors and both compatible mice, and an empty search.
The real 48 h m4 expression map was checked against saved per-mouse group summaries
for Cd74, Lgals3, Ctss, Col3a1, and Lyz2: 2,965 aligned full barcodes; retained
group sizes match; normalized means agree within 1e-12. A unit test separately
checks zero-library missingness versus measured zero and coordinate alignment.

AppTest exercises Streamlit rendering and interactions, not a real browser's visual
layout. Interactive visual review by the student remains part of session review.
Tomorrow's end-to-end/submission checklist remains in [checkpoint 2](CHECKPOINT_2.md).
