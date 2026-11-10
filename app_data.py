"""Read the saved engine exports and align one mouse's expression by full barcode."""
import csv
import gzip
import hashlib
import json
from pathlib import Path

from data_loader import load_metadata
from sparse_loader import ARCHIVES, SparseDataset, read_archive
from spatial_evidence import normalized_count

ROOT = Path(__file__).resolve().parent
RANKING = ROOT / 'results/ranking/HP_0001395'


def verify_exports():
    """Refuse changed/mixed ranking files rather than silently displaying them."""
    manifest = json.loads((RANKING / 'manifest.json').read_text())
    for name, expected in manifest['output_sha256'].items():
        with (RANKING / name).open('rb') as handle:
            hasher = hashlib.sha256()
            for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                hasher.update(chunk)
            digest = hasher.hexdigest()
        if digest != expected:
            raise ValueError(f'Ranking checksum mismatch: {name}')
    return manifest


def read_components():
    with (RANKING / 'components.csv').open(newline='') as handle:
        return list(csv.DictReader(handle))


def read_profile(feature_id):
    with gzip.open(RANKING / 'evidence_profiles.jsonl.gz', 'rt') as handle:
        for line in handle:
            row = json.loads(line)
            if row['feature_id'] == feature_id:
                return row
    raise ValueError(f'No saved evidence profile for {feature_id}')


def load_mouse(mouse):
    sample = mouse.removeprefix('t_').replace('h_', '_')
    metadata = load_metadata(ROOT / 'Visium_Meta_data.txt')
    features, spots, indices, values = read_archive(
        ROOT / 'data/source' / f'{sample}.zip', sample, metadata, ARCHIVES[sample])
    return SparseDataset(features, spots, indices, values, metadata)


def spot_rows(data, feature_id):
    """Zero libraries are missing; measured zero counts normalize to real zero."""
    i = data.feature_index(feature_id)
    return [dict(barcode=s.barcode, mouse=s.mouse, time_hours=s.time_hours,
                 x=s.x, y=s.y, annotated=s.fibrogenic,
                 count=data.count(i, j), library_size=sum(data.values[j]),
                 expression=normalized_count(data.count(i, j), sum(data.values[j])))
            for j, s in enumerate(data.spots)]
