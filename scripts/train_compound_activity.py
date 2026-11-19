"""Select a galectin-3 Random Forest on validation and freeze its training fit."""
import argparse
import csv
import hashlib
from importlib.metadata import version
import json
import platform
from pathlib import Path

import joblib
import numpy as np
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

DATA = Path(__file__).resolve().parents[1] / 'results/compound_activity'
FINGERPRINT = {'radius': 2, 'fpSize': 2048, 'includeChirality': True}
FIXED_SETTINGS = {'n_estimators': 256, 'random_state': 19, 'n_jobs': 1}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(measured, predicted):
    return {
        'rmse': root_mean_squared_error(measured, predicted),
        'mae': mean_absolute_error(measured, predicted),
        'r2': r2_score(measured, predicted),
    }


def arrays(rows):
    generator = rdFingerprintGenerator.GetMorganGenerator(**FINGERPRINT)
    features = [generator.GetFingerprintAsNumPy(Chem.MolFromSmiles(row['standardized_smiles']))
                for row in rows]
    return np.stack(features), np.array([float(row['pIC50']) for row in rows])


def train(output):
    dataset = DATA / 'galectin3_dataset.csv'
    source_manifest = DATA / 'galectin3_manifest.json'
    source = json.loads(source_manifest.read_text())
    if sha256(dataset) != source['dataset_sha256']:
        raise ValueError('Frozen compound dataset checksum mismatch')
    with dataset.open(newline='') as handle:
        development = [row for row in csv.DictReader(handle)
                       if row['split'] in ('train', 'validation')]
    x_train, y_train = arrays([row for row in development if row['split'] == 'train'])
    x_val, y_val = arrays([row for row in development if row['split'] == 'validation'])
    baseline = float(y_train.mean())
    val_baseline = np.full(len(y_val), baseline)

    trials = []
    best = None
    best_rmse = float('inf')
    for min_leaf in (3, 1):
        for max_features in ('sqrt', 0.25):
            settings = dict(FIXED_SETTINGS, min_samples_leaf=min_leaf, max_features=max_features)
            model = RandomForestRegressor(**settings).fit(x_train, y_train)
            validation = metrics(y_val, model.predict(x_val))
            trials.append(dict(settings=settings, validation=validation))
            if validation['rmse'] < best_rmse:
                best_rmse = validation['rmse']
                best = model

    output.mkdir(parents=True, exist_ok=True)
    artifact = output / 'galectin3_rf.joblib'
    joblib.dump(best, artifact, compress=3)
    predictions = joblib.load(artifact).predict(x_val)
    np.testing.assert_array_equal(predictions, best.predict(x_val))
    with (output / 'galectin3_validation.csv').open('w', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['standardized_smiles', 'measured_pIC50', 'rf_predicted_pIC50',
                         'training_mean_predicted_pIC50'])
        rows = (row for row in development if row['split'] == 'validation')
        writer.writerows((row['standardized_smiles'], actual, predicted, baseline)
                         for row, actual, predicted in zip(rows, y_val, predictions, strict=True))
    report = {
        'version': 'galectin3-rf-v1',
        'dataset_version': source['version'],
        'dataset_sha256': source['dataset_sha256'],
        'dataset_manifest_sha256': sha256(source_manifest),
        'artifact_sha256': sha256(artifact),
        'validation_predictions_sha256': sha256(output / 'galectin3_validation.csv'),
        'endpoint': source['endpoint'],
        'target': source['target'],
        'assay': source['assay'],
        'fingerprint': FINGERPRINT,
        'selection': 'Lowest validation RMSE; first candidate wins a tie; final artifact fit on training only',
        'train_count': len(y_train),
        'validation_count': len(y_val),
        'training_mean_pic50': baseline,
        'baseline_validation': metrics(y_val, val_baseline),
        'rf_validation': metrics(y_val, predictions),
        'trial_settings': trials,
        'selected_settings': best.get_params(),
        'python': platform.python_version(),
        'dependencies': {pkg: version(pkg) for pkg in
                         ('rdkit', 'numpy', 'scipy', 'scikit-learn', 'joblib',
                          'threadpoolctl', 'narwhals', 'cloudpickle')},
    }
    (output / 'galectin3_model_manifest.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DATA)
    train(parser.parse_args().output)
