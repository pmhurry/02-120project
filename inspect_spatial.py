"""Build full-data QC, per-mouse spatial summaries, and subset comparison offline."""
import argparse
from array import array
import csv
import gzip
import hashlib
import json
from pathlib import Path

from data_loader import load_dataset
from sparse_loader import ARCHIVES, SparseDataset, load_full_dataset
from spatial_evidence import equal_mouse_summaries, normalized_count, summarize


def write_csv(path, rows):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'wt', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def compare_subset(full, libraries, full_rows, root):
    subset = load_dataset(root / 'spatial_matrix.csv', root / 'Visium_Meta_data.txt')
    if subset.genes != [f.symbol for f in full.features]:
        raise ValueError('Subset feature alignment differs')
    indices, values = [], []
    for j in range(len(subset.spots)):
        pairs = [(i, int(row[j])) for i, row in enumerate(subset.counts) if row[j]]
        indices.append(array('I', (i for i, _ in pairs)))
        values.append(array('Q', (v for _, v in pairs)))
    sparse = SparseDataset(full.features, subset.spots, indices, values, subset.metadata)
    subset_libraries, _, subset_rows = summarize(sparse)
    columns = {s.barcode: j for j, s in enumerate(full.spots)}
    checks = []
    for symbol in ('Col1a1', 'Col1a2', 'Col3a1', 'Alb'):
        i = full.feature_index(symbol)
        errors = []
        for j, spot in enumerate(subset.spots):
            k = columns[spot.barcode]
            if libraries[k] != subset_libraries[j] or full.count(i, k) != subset.counts[i][j]:
                raise ValueError('Shared spot library/count mismatch')
            a = normalized_count(full.count(i, k), libraries[k])
            b = normalized_count(subset.counts[i][j], subset_libraries[j])
            if a is not None and b is not None:
                errors.append(abs(a - b))
        for a, b in zip((r for r in full_rows if r['symbol'] == symbol),
                        (r for r in subset_rows if r['symbol'] == symbol)):
            checks.append(dict(feature_id=a['feature_id'], symbol=symbol, mouse=a['mouse'],
                               shared_spots=len(subset.spots), max_shared_normalization_error=max(errors, default=0),
                               full_annotated_n=a['annotated_n'], subset_annotated_n=b['annotated_n'],
                               full_other_n=a['other_n'], subset_other_n=b['other_n'],
                               full_difference=a['difference'], subset_difference=b['difference']))
    return checks


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=root / 'data/source')
    parser.add_argument('--output', type=Path, default=root / 'results/spatial')
    args = parser.parse_args()
    data = load_full_dataset(args.source, root / 'Visium_Meta_data.txt')
    libraries, qc, rows = summarize(data)
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / 'library_qc.csv', qc)
    write_csv(args.output / 'spot_libraries.csv.gz', [dict(barcode=s.barcode, mouse=s.mouse,
              annotated=s.fibrogenic, library_size=lib, retained=lib > 0) for s, lib in zip(data.spots, libraries)])
    write_csv(args.output / 'per_mouse.csv.gz', rows)
    write_csv(args.output / 'equal_mouse.csv.gz', equal_mouse_summaries(rows))
    write_csv(args.output / 'subset_comparison.csv', compare_subset(data, libraries, rows, root))
    manifest = dict(version='spatial-v1', dataset='full_metadata_matched_archives',
                    features=len(data.features), spots=len(data.spots),
                    archive_md5=ARCHIVES, normalization='ln(1 + 10000 * count / all-feature library)',
                    qc_rule='exclude zero-library spots only; no detection/mitochondrial thresholds',
                    missing_values='empty CSV cell; not zero', aggregation='equal mouse weight; require two mice per time',
                    source_sha256={name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                                   for name in ('Visium_Meta_data.txt', 'spatial_evidence.py', 'inspect_spatial.py')},
                    output_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(args.output.iterdir()) if p.suffix != '.json'})
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for row in qc:
        print(row)
    print(f'Saved {len(rows):,} feature/mouse rows; shared-spot normalization checked.')


if __name__ == '__main__':
    main()
