const assets = '/assets/heldout_';

export default function Predictions({report, error}) {
  return <main className="guide">
    <header className="guide-heading">
      <h1>Galectin-3 activity predictions</h1>
      <p>Human galectin-3 · ChEMBL assay CHEMBL5737905 · HTRF competition IC50</p>
    </header>
    {report ? <>
      <section className="card guide-section">
        <h2>Held-out performance</h2>
        <p>{report.version} · {report.test_count} compounds across {report.test_scaffolds} test scaffolds.
          Measured pIC50 ranged from {report.measured_pIC50_range.map(value => value.toFixed(2)).join(' to ')}.
          Test scaffolds were absent from training and validation.</p>
        <table className="prediction-table">
          <thead><tr><th scope="col">Predictor</th><th scope="col">RMSE</th><th scope="col">MAE</th><th scope="col">R²</th></tr></thead>
          <tbody>{[['Random Forest', report.rf], ['Training mean', report.baseline]].map(([label, scores]) =>
            <tr key={label}><th scope="row">{label}</th>{['rmse', 'mae', 'r2'].map(metric =>
              <td key={metric}>{scores[metric].toFixed(3)}</td>)}</tr>)}</tbody>
        </table>
        <p>The paired 95% bootstrap interval for the RMSE improvement was {report.bootstrap_rmse_gain_95.map(value => value.toFixed(3)).join(' to ')} pIC50,
          using whole-scaffold resampling. It reflects variation within this test set from one assay.</p>
        <img className="prediction-plot" src={assets + 'plot.svg'} alt="Random Forest predictions versus measured pIC50, with an agreement diagonal and training-mean baseline."/>
      </section>
      <section className="card guide-section">
        <h2>Compound predictions</h2>
        <p>pIC50 = 9 − log₁₀(IC50 in nM). A one-unit increase represents tenfold lower IC50.</p>
        <p>Nearest-training Tanimoto measures Morgan fingerprint similarity. {report.below_cutoff} compounds fall below the minimum observed in validation ({report.similarity_cutoff.toFixed(4)}).
          Treat those estimates as extrapolations. The flag describes chemical resemblance and carries no calibrated probability or interval.</p>
        <p><a href={assets + 'predictions.csv'} download>Download prediction CSV</a> · <a href={assets + 'evaluation.json'} download>Download evaluation JSON</a></p>
        <div className="prediction-scroll" tabIndex={0} role="region" aria-label="Held-out compound predictions">
          <table className="prediction-table">
            <thead><tr>{['ChEMBL compound', 'Measured pIC50', 'Predicted pIC50', 'Nearest training similarity', 'Similarity flag'].map(label =>
              <th scope="col" key={label}>{label}</th>)}</tr></thead>
            <tbody>{report.predictions.map(row => <tr key={row.smiles}>
              <th scope="row">{row.compound_ids}</th><td>{row.measured_pIC50.toFixed(3)}</td>
              <td>{row.rf_predicted_pIC50.toFixed(3)}</td><td>{row.nearest_train_tanimoto.toFixed(4)}</td>
              <td>{row.similarity_flag}</td>
            </tr>)}</tbody>
          </table>
        </div>
        <p>Held-out compounds have experimental measurements for evaluation. Predictions for genuinely untested compounds remain hypotheses.
          This biochemical assay cannot establish the desired direction of intervention, liver benefit, or safety.</p>
      </section>
    </> : <p role="status">{error || 'Loading held-out evaluation…'}</p>}
  </main>;
}
