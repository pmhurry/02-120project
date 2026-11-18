# Checkpoint 4: Compound shortlist, final evidence, and submission — due December 1, 2026

Finish the [deployed engine](CHECKPOINT_3.md), evaluate compounds associated with
its top genes using published experiments, and submit the app, code, video, and
required documentation. The final product is a shortlist of compounds worth
testing, with evidence and open questions for each.
It also includes a model predicting one selected protein's measured response to
compounds from their chemical structures, evaluated on compounds withheld from
training, subject to the checkpoint 3 data-feasibility gate.

Three sessions of roughly 60–90 minutes on November 22, 24, and 30. November 23
and 25 are movable catch-up slots. Keep November 26–29 free of essential work;
December 1 is a submission buffer. Save journals and review/commit each session.

## Conditional virtual screening

The core predictive result is the frozen scaffold-held-out evaluation from
checkpoint 3, including weak or negative results. Before opening the final test,
document what performance relative to the mean baseline and what chemical coverage
would justify screening. Feasible data alone do not establish useful predictions.
Only proceed if the held-out evidence supports the intended use; otherwise report
the limitation and retain experimental evidence review as the shortlist basis.

## Session 1 — November 22: Findings and reproducibility

- [ ] Resolve correctness/usability issues without adding major features.
- [ ] Review the three initial top-gene profiles and their compounds; expand toward five genes only if evidence and time permit. Retain missing-compound and unresolved cases in the report.
- [ ] For each candidate, state spatial observations, replicate agreement, tractability, tissue context, reported liabilities, and unresolved intervention direction.
- [ ] Review functional evidence and contradictions with citations; explain a concrete experiment to test the hypothesis.
- [ ] Audit each target's "blocking may help", "activation may help", "mixed/context-dependent", or "unknown" label against the cited experiments. Explain potential damage-versus-repair roles and whether evidence matches the injury stage and liver model; preserve uncertainty rather than forcing a harmful/helpful classification.
- [ ] For each shortlisted compound, explain what it affects, what published experiments show, whether the desired action is supported, and what remains unknown. Separate measured observations from predictions.
- [ ] Compare compounds using the documented evidence categories; avoid comparing raw activity numbers across incompatible experiments or treating approval for another condition as evidence of benefit here.
- [ ] Propose a follow-up experiment for the strongest supported gene–compound pair: relevant liver model, compound dose range and duration, untreated/solvent control, injury-related outcome, and cell-survival measurement. If no pair is adequately supported, explain what evidence is needed first.
- [ ] Include early injury and later recovery measurements in the proposed experiment so reduced damage can be distinguished from delayed healing; specify liver-function or repair outcomes where appropriate. Account for effects on other proteins before attributing a compound's result to the selected gene.
- [ ] State that reviewing only top genes cannot show that the ranking outperforms other selection methods. If feasible, review one or two lower-ranked genes with the same rules as an illustrative comparison, without claiming statistical validation.
- [ ] Report ranking sensitivity and compare with the spatial-only screen, including coverage and knowledge bias.
- [ ] Distinguish hypotheses from causal, clinical efficacy, or toxicity claims; collagen-label agreement is not independent validation.
- [ ] Test clean setup/offline rebuild using README, checksums, and exported configuration; verify hosted results agree.
- [ ] Reproduce the frozen model's test predictions and baseline comparison without selecting new settings from test results. Report RMSE, MAE, and R² against the training-mean baseline on the same test compounds, sample sizes, Murcko scaffold split rules, fingerprint radius/size, exclusions, and limitations; distinguish target-activity prediction from liver-injury outcomes.
- [ ] Decide whether held-out performance and chemical coverage meet the screening criteria documented before final evaluation. A dataset passing feasibility checks is insufficient on its own. If performance is weak or data inadequate, document the result and leave virtual screening unperformed.
- [ ] If justified, choose a small versioned virtual library of untested or unsynthesized candidates with traceable identifiers, structures, provenance, and any known activity records. Remove training/evaluation compounds and standardize structures with the same RDKit policy used for modeling.
- [ ] Score the eligible library with the frozen Morgan-fingerprint/Random Forest pipeline, rank by predicted pActivity, and record filtering rules and all exclusion counts. Do not tune the model using the desired shortlist.
- [ ] Export a diverse candidate shortlist with predicted endpoint/scale, model version, nearest-training-compound Tanimoto similarity, scaffold, and experimental-evidence status. Flag unfamiliar chemistry; similarity is not a calibrated confidence interval. Avoid filling the shortlist with near-identical high scorers and keep predictions separate from measured activity.
- [ ] Explain that candidates are hypotheses for experimental testing; predicted potency/affinity does not establish intervention direction, selectivity, synthesis feasibility, safety, or liver benefit. Retain published-evidence candidates even when screening is not supported.

## Session 2 — November 24: Demonstration and materials

- [ ] Finalize narration: question, dataset, gene ranking, one gene–compound example, published experimental evidence, model predictions versus held-out measurements and baseline, proposed next experiment, sensitivity, and limitations. State any model feasibility failure plainly.
- [ ] Record a narrated demonstration of at most five minutes and check duration, audio, and legibility.
- [ ] Upload to a course-accepted location, verify access, and link from README and the app.
- [ ] Assemble submission links using actual course requirements and review the required journals.
- [ ] Keep historical logs intact; do not reconstruct missing work as if recorded contemporaneously.

Use November 25 for any recording retry rather than reserving essential video work
for the deadline.

## Session 3 — November 30: Final review

- [ ] Test the deployment, downloads, source links, and video in a fresh browser session.
- [ ] Confirm repository, versioned model configuration, data manifests, citations, and known limitations are current.
- [ ] Verify compound-table downloads, source links, action directions, measurement units, and evidence labels against the reviewed records.
- [ ] Verify the model version, prediction downloads, measurement scale, training-similarity labels, and agreement between displayed and saved predictions; confirm reproducible setup includes the required chemistry/model dependencies.
- [ ] Verify code/docs are committed and pushed and the deployment uses the same reviewed version.
- [ ] Practice explaining barcode alignment, normalization, mouse-level contrasts, mapping uncertainty, weights, and why missing safety data are not evidence of safety.
- [ ] Practice explaining why high gene expression does not establish that blocking its protein helps, and why a compound shortlist is not a demonstrated treatment. Describe RL as a future way to choose experiments as results arrive.
- [ ] Document the future RL feedback requirements: experimental outcomes, timing, controls, and an evaluation against fixed ranking and random selection. Explain why expression changes and literature labels alone cannot establish treatment benefit; do not claim an RL result without implementing and evaluating it on suitable data.
- [ ] Prepare for demo day and the December 3 assessment; submit early if possible.

## December 1 — Submission buffer

- [ ] Fix submission blockers only and recheck affected outputs/links.
- [ ] Submit all course-required materials and verify the submission receipt/status.

**Done means:** the engine, auditable results, gene–compound evidence table,
justified shortlist (or documented evidence gaps), proposed follow-up experiment, video, sources,
and journals are accessible and submitted, and the model's assumptions and limits
can be explained. The predictive component has an honest held-out evaluation
against a baseline, or an explicitly reported unmet objective due to inadequate
data. RL remains a future extension. No essential work depends on Thanksgiving break.
