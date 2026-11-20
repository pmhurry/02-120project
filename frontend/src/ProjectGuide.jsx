const repository = 'https://github.com/pmhurry/02-120project';
const file = (name) => `${repository}/blob/main/${name}`;

export default function ProjectGuide() {
  return <main className="guide">
    <header className="guide-heading">
      <h1>Project guide</h1>
      <p>We use mouse spatial transcriptomics after acetaminophen-induced liver injury to prioritize human gene targets for follow-up. The site lets you trace each rank back to the mouse data and published evidence.</p>
      <a className="guide-action" href="/">Explore ranked targets</a>
    </header>

    <section className="card guide-section" aria-labelledby="development">
      <h2 id="development">How the project developed</h2>
      <ol className="guide-steps">
        <li><strong>Rebuilt and checked the spatial dataset.</strong> The first checkpoint used a 348-spot sample to test barcode alignment, normalization, and plotting. The current analysis uses 17,370 matched spots and 32,285 original features from six mice, two per time point. <a href={file('DATA_PROVENANCE.md')}>Data provenance</a></li>
        <li><strong>Built the ranking engine.</strong> The engine combines replicated mouse expression contrasts with evidence for human orthologs, small-molecule tractability, and hepatic fibrosis. The default ranking contains 2,248 eligible features. <a href={file('ENGINE_DESIGN.md')}>Ranking design</a></li>
        <li><strong>Reviewed compound evidence.</strong> We froze the first three targets in ranking order, CD74, LGALS3, and CTSS, before reviewing published studies. Profiles distinguish a compound’s action, what the experiment measured, and whether the result supports follow-up in acute injury. <a href="/exports/compounds">Download reviewed compounds</a></li>
        <li><strong>Deployed a React evidence explorer.</strong> The site combines searchable rankings, filters, score breakdowns, spatial maps, tissue and liability context, and downloads. FastAPI serves the same versioned outputs to React and the <a href="/streamlit/">Streamlit comparison</a>.</li>
      </ol>
    </section>

    <section className="card guide-section" aria-labelledby="methods">
      <h2 id="methods">How the ranking works</h2>
      <div className="guide-methods">
        <article><h3>Spatial contrast</h3><p>Normalize each spot as <code>ln(1 + 10,000 × gene count ÷ library size)</code>, using counts across all features for the library size. Zero-library spots are excluded from expression calculations. Within each mouse, subtract the other-region mean from the annotated-region mean.</p></article>
        <article><h3>Mouse replication</h3><p>At 48 and 72 hours, use the smaller contrast from the two mice, clip it at zero, transform it as <code>x ÷ (1 + x)</code>, and average the two time points. Both mice must show a positive contrast at one of these times. The 24-hour annotation describes necrotic regions and is shown separately.</p></article>
        <article><h3>Human evidence and weights</h3><p>Ranking requires a high-confidence, one-to-one mouse–human mapping using stable IDs. Priority is 100 times the weighted sum of spatial contrast (60%), small-molecule tractability (25%), and hepatic fibrosis association (15%). Missing components prevent a complete rank. Tissue and liability data provide context.</p></article>
      </div>
      <p className="guide-takeaway"><strong>Sensitivity check.</strong> A spatial-heavy weighting shared 5 of the default top 10 targets. Equal weighting shared 7. The 48- and 72-hour rankings shared 6 of their top 10, so the ordering depends on both weights and time point. <a href={file('journal/checkpoint3_session1_notes.md')}>Read the sensitivity results</a></p>
    </section>

    <section className="card guide-section" aria-labelledby="compound-model">
      <h2 id="compound-model">Galectin-3 compound activity model</h2>
      <p>A separate Random Forest predicts human galectin-3 activity for one ChEMBL competition assay. It uses 2,048-bit Morgan fingerprints and a scaffold-based split to group compounds with the same core structure. The endpoint is pIC50, where a one-unit difference corresponds to a tenfold difference in measured concentration.</p>
      <div className="score-grid guide-validation">
        <div className="metric"><span>Training compounds</span><strong>226</strong></div>
        <div className="metric"><span>Validation compounds</span><strong>48</strong></div>
        <div className="metric"><span>Reserved test compounds</span><strong>48</strong></div>
      </div>
      <p>On validation, the model achieved <strong>0.449 pIC50 RMSE</strong> versus <strong>0.683</strong> for the training-mean baseline. These validation results guided model selection. Final test evaluation and a prediction view are pending. Compounds in the held-out sets already have assay measurements for comparison.</p>
      <div className="source-links"><a href={file('results/compound_activity/galectin3_model_manifest.json')}>Model manifest</a><a href={file('results/compound_activity/galectin3_validation.csv')}>Validation predictions</a></div>
    </section>

    <section className="card guide-section" aria-labelledby="deliverables">
      <h2 id="deliverables">Deliverables</h2>
      <ul className="guide-deliverables">
        <li><a href="/">Evidence explorer</a><span>Explore rankings, inspect target profiles, and export filtered results, spatial spots, and profile JSON.</span></li>
        <li><a href="/exports/ranking">Default ranking CSV</a><span>Get component scores, rank, and mapping fields for every eligible target.</span></li>
        <li><a href="/exports/compounds">Compound evidence CSV</a><span>Get reviewed compounds, activity measurements, action direction, limitations, and source citations.</span></li>
        <li><a href={file('results/compound_activity/galectin3_dataset.csv')}>Galectin-3 dataset</a><span>Get measured activity values, compound structures, and the frozen split assignments.</span></li>
        <li><a href={repository}>Source code and build journal</a><span>Find the analysis scripts, versioned manifests, reproducibility checks, and checkpoint documentation.</span></li>
      </ul>
    </section>

    <section className="card guide-section" aria-labelledby="limits">
      <h2 id="limits">What the evidence supports</h2>
      <p>The ranks are exploratory hypotheses. The experiment has two mice per time point, no uninjured controls, no target perturbations, and spots that can contain mixed cell types. Orthology and external evidence coverage affect which features can rank. The 48- and 72-hour region labels are collagen-linked, so enrichment of collagen markers does not independently validate the annotation.</p>
      <p>A high rank alone gives no basis for choosing inhibition or activation. Published results can depend on species, injury model, intervention, and timing. Normal-human tissue records and missing liability reports cannot establish safety. The galectin-3 model predicts a lab measurement. Liver recovery, clinical benefit, and safety require separate experiments.</p>
    </section>
  </main>;
}
