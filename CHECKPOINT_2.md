# Checkpoint 2: Working scientific prototype — due November 10, 2026

Build on [checkpoint 1](CHECKPOINT_1.md) to make a local Streamlit prototype that
answers the project question: how do annotated regions and ECM expression differ
across 24, 48, and 72 hours after injury?

Plan for five sessions of roughly 60–90 minutes, about 5–7.5 hours total. Dates
are suggested work slots, not daily requirements; move them to fit your schedule.
October 31, November 2, 4, and 6 are unscheduled. November 10 is a final buffer,
not a planned feature-building day. Each session includes checking the result,
explaining it in your own words, saving the required journal, and reviewing and
committing changes.

## Session 1 — November 1: Load the recovered data

- [ ] Review checkpoint 1's normalization, score definition, and remaining issues.
- [ ] Add a sparse-data loader for the recovered archives without expanding the entire matrix into a dense table.
- [ ] Select metadata-matched spots explicitly; preserve feature IDs alongside gene symbols and define how duplicate symbols are handled.
- [ ] Verify all 17,370 metadata barcodes and reproduce the supplied subset's counts.
- [ ] Document dependencies and how to download and verify source files on a fresh machine.

## Session 2 — November 3: Check the model on full coverage

- [ ] Apply the documented normalization and score to the recovered data; retain the predefined marker panel rather than tune it to the results.
- [ ] Review library sizes and zero-total spots by sample; document any filtering and show retained/excluded counts.
- [ ] Verify barcode alignment, normalization on a hand-calculated example, identical-profile scores, a known contrast, and zero-count/zero-variance behavior.
- [ ] Compare a few full-data results with the subset and explain why changing coverage can change summaries or a data-derived reference.
- [ ] Save a reproducible sample-level summary to check against the app later.

If full-data integration runs over, use the next work session for it and reduce
interface polish. Keep the checked subset runnable and explicitly labeled until
full-data checks pass; never silently switch between data versions.

## Session 3 — November 5: Build the map interface

- [ ] Create the Streamlit app with compatible time-point and mouse selectors.
- [ ] Add annotation, individual-gene, and score map modes with a clear legend.
- [ ] Keep samples spatially separate, preserve aspect ratio, and distinguish missing expression from measured zero.
- [ ] Add spot selection or barcode lookup showing its sample, annotation, coordinates, and selected measurement.
- [ ] Check several plotted barcodes and values against the loader output.

## Session 4 — November 7: Add scientific comparisons

- [ ] Compare annotated groups within each mouse using normalized expression and the defined score.
- [ ] Show temporal summaries alongside each mouse's result, with spot and mouse counts.
- [ ] Keep comparisons descriptive: there are two mice per time point, and spots are not independent biological replicates.
- [ ] Explain that 24 h labels describe manually annotated necrotic regions, while later labels have collagen-based provenance.
- [ ] Examine predefined markers beyond collagen without presenting annotation agreement as independent validation.

## Session 5 — November 9: Review and prepare for the TA

- [ ] Run the complete local workflow and fix errors that prevent its use.
- [ ] Confirm displayed values agree with the saved summaries and that labels state normalization and score reference.
- [ ] Update README with launch instructions, current data coverage, and known limits.
- [ ] Prepare a short explanation of the question, data, normalization, score, one result, and one limitation.
- [ ] Arrange or prepare for the TA check-in during the November 4–13 window; record questions and feedback when it happens.
- [ ] Review the checkpoint submission instructions and required journal files.

## November 10 — Buffer and checkpoint submission

- [ ] Fix remaining blockers, review the repository, and submit the required checkpoint materials.

**Done means:** A checked local prototype supports map exploration, spot lookup,
and sample-level comparisons, and you can explain its calculations. Full coverage
is the target; any subset fallback must state its coverage and remaining work.
Deployment and tissue-image overlays belong to [checkpoint 3](CHECKPOINT_3.md).
