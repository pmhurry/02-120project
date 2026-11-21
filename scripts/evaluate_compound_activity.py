"""Reproduce the held-out assessment of the frozen galectin-3 model."""
import csv
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np

from train_compound_activity import DATA, arrays, metrics, sha256


def evaluate():
    model_manifest = DATA / 'galectin3_model_manifest.json'
    manifest = json.loads(model_manifest.read_text())
    dataset = DATA / 'galectin3_dataset.csv'
    split_manifest = DATA / 'galectin3_manifest.json'
    artifact = DATA / 'galectin3_rf.joblib'
    for path, key in ((dataset, 'dataset_sha256'),
                      (split_manifest, 'dataset_manifest_sha256'),
                      (artifact, 'artifact_sha256')):
        if sha256(path) != manifest[key]:
            raise ValueError(f'Frozen checksum mismatch for {path.name}')

    with dataset.open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    train = [row for row in rows if row['split'] == 'train']
    validation = [row for row in rows if row['split'] == 'validation']
    test = [row for row in rows if row['split'] == 'test']
    scaffolds = np.array([row['murcko_scaffold'] for row in test])
    if set(scaffolds) & {row['murcko_scaffold'] for row in train + validation}:
        raise ValueError('Test scaffolds overlap development scaffolds')

    x_train, _ = arrays(train)
    x_test, measured = arrays(test)
    predicted = joblib.load(artifact).predict(x_test)
    baseline = np.full(len(test), manifest['training_mean_pic50'])
    train_bits = x_train.astype(bool)
    nearest = []
    for fingerprint in x_test.astype(bool):
        intersection = np.count_nonzero(train_bits & fingerprint, axis=1)
        union = np.count_nonzero(train_bits | fingerprint, axis=1)
        nearest.append(float(np.max(intersection / union)))
    cutoff = json.loads(split_manifest.read_text())['split_summary']['validation'][
        'nearest_train_tanimoto']['minimum']

    predictions = [
        dict(compound_ids=row['source_molecule_ids'], smiles=row['standardized_smiles'],
             scaffold=row['murcko_scaffold'], measured_pIC50=actual,
             rf_predicted_pIC50=estimate, training_mean_predicted_pIC50=reference,
             nearest_train_tanimoto=similarity,
             similarity_flag=('Within validation similarity range or higher'
                              if similarity >= cutoff else 'Below validation similarity range'))
        for row, actual, estimate, reference, similarity in
        zip(test, measured, predicted, baseline, nearest, strict=True)
    ]
    groups = [np.flatnonzero(scaffolds == name) for name in sorted(set(scaffolds))]
    rng = np.random.default_rng(19)
    differences = []
    for _ in range(5000):
        sample = np.concatenate([groups[i] for i in rng.integers(len(groups), size=len(groups))])
        reference_rmse = np.sqrt(np.mean((measured[sample] - baseline[sample]) ** 2))
        model_rmse = np.sqrt(np.mean((measured[sample] - predicted[sample]) ** 2))
        differences.append(reference_rmse - model_rmse)
    report = dict(
        version=manifest['version'], dataset_version=manifest['dataset_version'],
        model_manifest_sha256=sha256(model_manifest), target=manifest['target'],
        assay=manifest['assay'], endpoint=manifest['endpoint'],
        test_count=len(test), test_scaffolds=len(groups), development_scaffold_overlap=0,
        measured_pIC50_range=[float(measured.min()), float(measured.max())],
        rf=metrics(measured, predicted), baseline=metrics(measured, baseline),
        bootstrap_rmse_gain_95=np.quantile(differences, [0.025, 0.975]).tolist(),
        bootstrap_method='5000 paired resamples of whole test scaffolds, seed 19',
        similarity_cutoff=cutoff,
        below_cutoff=sum(similarity < cutoff for similarity in nearest),
        predictions=predictions,
    )
    (DATA / 'heldout_evaluation.json').write_text(json.dumps(report, indent=2) + '\n')
    with (DATA / 'heldout_predictions.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            'target', 'assay', 'endpoint', 'model_version', *predictions[0]], lineterminator='\n')
        writer.writeheader()
        writer.writerows(dict(target=report['target'], assay=report['assay'],
                              endpoint=report['endpoint'], model_version=report['version'], **row)
                         for row in predictions)

    plt.rcParams.update({'svg.hashsalt': 'galectin3-rf-v1', 'svg.fonttype': 'none'})
    fig, ax = plt.subplots(figsize=(6, 5), layout='constrained')
    limits = (4.8, 7.8)
    ax.plot(limits, limits, ':', color='#64748b', label='Perfect agreement')
    ax.axhline(baseline[0], color='#a04429', linestyle='--', label='Training mean')
    ax.scatter(measured, predicted, color='#16676a', alpha=0.75, label='Random Forest')
    ax.set(xlim=limits, ylim=limits, aspect='equal', xlabel='Measured pIC50',
           ylabel='Predicted pIC50', title=f'Galectin-3 held-out set ({len(test)} compounds)')
    ax.legend(loc='lower right')
    plot = DATA / 'heldout_plot.svg'
    fig.savefig(plot, metadata={'Date': None})
    plot.write_text(''.join(line.rstrip() + '\n' for line in plot.read_text().splitlines()))
    plt.close(fig)


if __name__ == '__main__':
    evaluate()
