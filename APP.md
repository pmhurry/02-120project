# Spatial target evidence app

## React app

The [React app](https://spatial-target-evidence.vercel.app/) is the default.
The [Streamlit comparison](https://spatial-target-evidence.vercel.app/streamlit/)
uses the same ranking and filter functions, profile JSON, and versioned spot
and compound CSVs. React shows the target list, score
components, spatial evidence, curated compounds and tissue context. The
profile JSON includes the full underlying clinical and source records.

To build and open the React app locally with Node.js and the app dependencies:

```sh
npm ci --prefix frontend
npm run build --prefix frontend
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8522
```

Open `http://127.0.0.1:8522/`. The former `/preview` URL redirects to the main app.
Vercel’s build command produces the same static frontend from the package lockfile.

## Run Streamlit locally

Python 3.11+ is needed for the pinned interface dependencies. The existing CLI
analysis still uses Python 3.10+ and the standard library.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/streamlit run app.py --server.address localhost
```

Open the local URL printed by Streamlit. The interface is read-only.
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
counts. Annotation maps need only metadata. CD74, LGALS3, and CTSS have packaged
expression maps for all six mice. Other expression maps use a checksum-checked
local ZIP on demand from `data/source/` (see [archive setup](DATA_PROVENANCE.md)).
Both paths normalize counts with **all features**
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
layout. The student confirmed completion of browser review on November 10.
November 10 checks passed; see [session 5 notes](journal/checkpoint2_session5_notes.md)
and remaining review/submission tasks in [checkpoint 2](CHECKPOINT_2.md).

## November 18 evidence review controls

The optional filters are applied before text search and never recompute rank.
The tractability filter excludes missing scores when enabled above zero. The
tissue filter requires a measured normal-human liver RNA value, including a
measured zero. Both filters report exclusions, and neither is a safety filter.

The reviewed compound section displays published measurements and separate
target-direction judgments for CD74, LGALS3, and CTSS. The downloadable CSV
keeps experimental context, compound action, selectivity, liabilities, and
the reasons each case remains unresolved or warrants follow-up. The previously
collected clinical records retain each drug's overall stage, listed indications,
and individual records. Stage alone gives no evidence of efficacy for APAP injury.
Expression-map scales start at zero and are specific to the selected mouse
and gene. Compare the exported numeric values when judging differences across maps.


## Hosting the reviewed app

[Open the public app](https://spatial-target-evidence.vercel.app)

Vercel runs the Python app as a FastAPI function. The [ASGI entry point](main.py)
serves React at the root, exposes the data and export routes, and mounts
Streamlit at `/streamlit/`.
Import `pmhurry/02-120project` on `main` as a FastAPI project with Fluid
compute. The [Vercel configuration](vercel.json) excludes journals, source
archives, and the model artifact from the function bundle.
[Vercel FastAPI guide](https://vercel.com/docs/frameworks/backend/fastapi)

To test the same entry point locally after installing `requirements.txt`:

```sh
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8520
```

Vercel WebSockets remain tied to a function instance for the duration of the
connection. The hosted app sends map images inline and serves downloads through
HTTP routes that can run on any instance. Fresh Chrome verification covered
the expression view and compound download. Hosted ranking, spot, profile, and
compound exports were compared with the versioned data.
[Vercel WebSocket documentation](https://vercel.com/kb/guide/do-vercel-serverless-functions-support-websocket-connections)

The Git revision pins the ranking, tissue and compound tables, annotation
metadata, and 18 compressed expression maps. At runtime the app verifies the
ranking export, tissue summary, and each requested packaged map by SHA-256.
Run `python3 scripts/package_expression_maps.py` with the six original archives
to rebuild maps. Public deployments can display annotations for every feature
and expression for the three reviewed targets. The app also supports local
archives for expression maps of other targets.

The local archive-free test used 40.5 MiB of app files and data, rendered in
1.10 seconds, and peaked at 309.1 MiB RSS including AppTest during target
switching. Hosted memory and startup latency were not separately measured. The production
release was published using the Vercel CLI from the reviewed app files.
