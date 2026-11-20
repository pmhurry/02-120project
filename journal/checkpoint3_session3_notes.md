# November 19 — Deployment preparation and frozen validation model

## Spatial app

The student selected Vercel. A FastAPI ASGI adapter mounts the existing
Streamlit app with its startup and shutdown lifecycle. An archive-free local
copy held 40.5 MiB of code and data, rendered its first AppTest page in 1.10
seconds, and reached 309.1 MiB peak RSS with AppTest while switching targets
and maps. The six original archives occupy about 297 MiB.
[Hosting setup](../APP.md) · [Vercel FastAPI documentation](https://vercel.com/docs/frameworks/backend/fastapi)

The package contains 18 SHA-256-checked expression maps for CD74, LGALS3 and
CTSS across all six mice. It is tied to the ranking manifest and uses
full-feature spot libraries. The clean bundle uses Git-versioned files and
renders annotations for other targets. Local ZIP-backed expression is available
for other targets when the corresponding original archive is present.

All 18 maps match CLI spot libraries, annotation flags, and per-mouse group
sizes, means and detection fractions. The app integration check compared
displayed ranks with the CLI, exercised filters and lookup, checked expression
CSV rows against the original archive, and verified reviewed compound IDs,
action, measurement units, evidence direction, counter-evidence and citations.
Tissue and liability displays and the profile JSON matched saved profiles.
The compound CSV download matched the reviewed CSV byte for byte. All 30 unit
tests passed. Headless Chrome with a fresh local profile rendered the ranking,
tissue section, compound evidence and download controls. Hosted verification status is recorded below.

## Model training and validation

Use Python 3.14.7 with the pinned [model dependencies](../requirements-model.txt).

```sh
.venv/bin/python -m pip install -r requirements-model.txt
.venv/bin/python scripts/train_compound_activity.py
```

The model predicts human galectin-3 competition-assay pIC50 for ChEMBL assay
CHEMBL5737905. It uses the frozen [dataset and split manifest](../results/compound_activity/galectin3_manifest.json),
2,048-bit radius-2 Morgan fingerprints with chirality, and RDKit 2026.3.3.
Fit four Random Forest settings on 226 training compounds and selected the
lowest RMSE on the 48 scaffold-held-out validation compounds. The selected
forest used 256 trees, seed 19, three samples per leaf and 25% of features per
split. The baseline predicted the training mean of 6.833 for every compound.

| Validation predictor | RMSE | MAE | R² |
| --- | ---: | ---: | ---: |
| Training mean | 0.683 | 0.584 | −0.001 |
| Random Forest | 0.449 | 0.361 | 0.566 |

A second run with the same dependencies reproduced the
[artifact](../results/compound_activity/galectin3_rf.joblib),
[model manifest](../results/compound_activity/galectin3_model_manifest.json),
and [validation CSV](../results/compound_activity/galectin3_validation.csv)
byte for byte. The validation CSV gives measured and predicted pIC50 in
distinct columns. The final 48 test compounds were excluded from fingerprint
generation, fitting, prediction and model selection today. Validation estimates
were used for model selection. Final test evaluation remains scheduled for
November 20.

## Vercel deployment verification

A fresh local Chrome session opened the FastAPI entry point, rendered an
expression map, and downloaded the reviewed compound CSV byte for byte.
All 30 unit tests passed after the hosting change.

The anonymous Vercel build using `requirements.txt` reported a 378.04 MB
optimized function bundle and stopped at its 225 MB temporary-deployment
limit. Vercel documents a 500 MB standard Python Function limit. The student authorized Vercel sign-in and the authenticated build deployed.

The first production deployment responded to health checks, but some images
and downloads returned 404 because Streamlit kept those files in memory on
the WebSocket's function instance. The redeployment sends map images inline
and implements HTTP export routes that reconstruct results from versioned files.
A fresh Chrome profile opened the public app, rendered the expression layer,
and downloaded the exact reviewed compound CSV. Full and filtered ranking,
expression-map, profile JSON, and compound downloads matched local outputs.
All 30 unit tests and the app integration check passed.
[Verified public Vercel app](https://spatial-target-evidence.vercel.app)
[Vercel Python runtime limits](https://vercel.com/docs/functions/runtimes/python#controlling-what-gets-bundled)
