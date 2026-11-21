# Checkpoint 3 closeout · November 20, 2026

The frozen galectin-3 model was evaluated on 48 previously reserved compounds
from 29 Murcko scaffold groups. No test scaffold appeared in training or
validation. Measured pIC50 spanned 5.00–7.54. The Random Forest scored
0.482 RMSE, 0.361 MAE, and 0.341 R². The corresponding training-mean scores were
0.697, 0.541, and −0.378. The paired 95% bootstrap interval for the RMSE gain was
0.109–0.312 pIC50, using 5,000 whole-scaffold resamples. The interval describes
variation within this single-assay test set. The model and split stayed frozen.

Nine test compounds have a nearest-training Morgan fingerprint Tanimoto below
0.7013, the minimum similarity observed in validation. This cutoff is a
descriptive scope flag. Model performance for new assays and unrelated chemical
series is unresolved. The test compounds have measured IC50 values. Future
predictions for untested compounds still require experimental confirmation.

[Evaluation report](../results/compound_activity/heldout_evaluation.json) ·
[Predictions CSV](../results/compound_activity/heldout_predictions.csv) ·
[Predicted versus measured plot](../results/compound_activity/heldout_plot.svg)

## Demo script

1. Open the explorer and choose **Lgals3 / LGALS3**, priority rank **2** of 2,248,
   with a score of **52.18**. Show one expression map at 48 h and then the other
   48 h mouse. Compare the within-mouse annotated-versus-other region contrasts.
   The combined spatial component is 0.508. The 24 h necrotic annotation
   provides separate context. Spot counts show coverage and the mouse is the
   biological replicate.
2. Open the compound evidence and show TD139 (olitigaltin). The reviewed purified
   human Gal-3 binding experiment reported a Kd of 68 nM. TD139 also binds Gal-1.
   The mouse APAP knockout work measured liver injury and recovery, and the
   HBV transgenic study measured increased ALT after TD139. Explain why
   treatment timing, cell type, and the injury model affect interpretation.
   [Reviewed compound evidence and primary sources](../results/compound_activity/reviewed_compounds.csv)
3. Open **Predictions**. Explain that the model predicts pIC50 for HTRF competition
   in one assay. Show the measured-versus-predicted plot and a flagged compound.
   An increase of one pIC50 unit corresponds to a tenfold decrease in IC50.
   The 68 nM Kd from the TD139 study is a distinct endpoint.
4. Propose a controlled follow-up in an APAP liver-injury model to test whether
   post-injury Gal-3 intervention changes injury or repair. Compare vehicle and
   TD139 with uninjured controls and assess target engagement and Gal-1 activity.
   Measure injury and recovery at predefined times using ALT, necrotic area,
   and hepatocyte proliferation. A result with engagement and improved injury
   measures still needs follow-up on recovery and selectivity.

## Feature freeze

Checkpoint 3 fixes the ranking and reviewed shortlist and adds a read-only
held-out results view. Remaining limits include one biochemical assay for the
activity model, limited mice and differing region annotations, and hosted
expression maps for the three reviewed targets. Hosted Streamlit is a comparison
route with the Vercel WebSocket limitation described in [APP.md](../APP.md).

## Closeout

All 30 Python tests passed and the React production build succeeded. In Chrome,
the public plot rendered, all 48 displayed compound rows matched the saved
evaluation, and the downloaded CSV matched the checked file byte for byte.
Public ranking and compound exports also matched their local counterparts.
The [source dataset and sample checksums](https://zenodo.org/records/10901217)
were reviewed. The [production app](https://spatial-target-evidence.vercel.app/?view=predictions)
is ready for checkpoint submission. Canvas access and a submission receipt
were unavailable in this session.
