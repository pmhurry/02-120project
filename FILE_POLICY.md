# File decisions for the Spatial Target Prioritization Engine

Decisions made November 6, 2026. Keep original data and historical evidence;
remove disposable downloads/debug artifacts after verified snapshots exist.

| Files | Decision and purpose |
| --- | --- |
| `sparse_loader.py`, `inspect_full_data.py`, `tests/test_sparse_loader.py` | Keep: validated full-data loading and coverage/count reconciliation |
| `Visium_Meta_data.txt`, `data/source/*.zip` | Keep: original metadata and verified raw source archives; ZIPs remain ignored by Git |
| `spatial_matrix.csv`, `data_loader.py`, `inspect_data.py`, `inspect_archive.py` | Keep: supplied subset, shared metadata validation, and regression/provenance checks |
| `scoring.py`, `inspect_scores.py`, `SCORING.md`, `tests/test_scoring.py` | Keep as checkpoint 1 collagen-context baseline; not the engine ranking model |
| `plot_checkpoint.py`, `PLOTTING.md`, `results/spatial.svg`, `results/group_comparison.svg`, `results/group_summary.csv` | Keep as clearly labeled historical subset outputs and teaching examples |
| `gather_target_data.py`, `gather_tissue_data.py`, related tests | Keep: reproducible external annotation acquisition and offline rebuilds |
| `data/external/*.gz`, `data/external/hpa_*.zip`, manifests, derived tables/coverage summaries | Keep: compact snapshots and auditable model inputs; use compression for large tables |
| `DATA_PROVENANCE.md`, `DATA_INSPECTION.md`, `provenance/*.txt` | Keep: source history, limitations, and recovered-count audits |
| `ENGINE_DESIGN.md`, `TARGET_DATA.md`, `README.md`, `CHECKPOINT_1.md`–`CHECKPOINT_4.md` | Keep/update: authoritative model design, data docs, current roadmap, and historical checkpoint record |
| All `journal/` files and journal hooks/settings | Keep: work/learning history; preserve original dates and pending review/export steps |
| `data/external/raw/` working downloads, cached pages, and schema/debug probes | Delete after snapshot and offline rebuild validation; they duplicate the retained compressed inputs |
| `data/external/*query.json` scratch request files | Delete: the actual acquisition query templates and variables are documented in code/manifests |
| `.venv/` | Ignore: local app dependency environment; reproducible through `requirements.txt` |
| Generated `__pycache__/` / `*.pyc` | Ignore; disposable, not scientific inputs |

No historical source, student-authored journal, or existing user edit is deleted.
The old subset workflow stays runnable; the new app will use explicit full-data
outputs. Do not create fresh subset copies or rename historical files without a
need. New ranking outputs should use `results/engine/` with a configuration and
source-version manifest; they do not exist yet.

The app, ranking implementation, sensitivity analysis, and candidate-specific
functional review remain future sessions. Unrelated model types, molecule-generation
assets, docking inputs, and new large training datasets are outside this scope.

November 9: keep `app.py`, `app_data.py`, `requirements.txt`, `APP.md`,
`tests/test_app_data.py`, and `scripts/check_app.py` for the local interface and its
checks. The implemented ranking outputs live in `results/ranking/HP_0001395/`,
superseding the proposed `results/engine/` location above. Ranking and the local
interface are implemented; deployment and deeper sensitivity review remain future work.
