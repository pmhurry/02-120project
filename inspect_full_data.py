"""Validate full recovery and compare every supplied subset count, including zeros."""

import argparse
from collections import Counter
import csv
from pathlib import Path

from data_loader import load_dataset
from sparse_loader import load_full_dataset


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=root / "data/source")
    parser.add_argument("--output", type=Path, default=root / "results/full_data_coverage.csv")
    args = parser.parse_args()
    full = load_full_dataset(args.source, root / "Visium_Meta_data.txt")
    subset = load_dataset(root / "spatial_matrix.csv", root / "Visium_Meta_data.txt")
    if [f.symbol for f in full.features] != subset.genes:
        raise ValueError("Subset feature order differs")
    full_columns = {s.barcode: j for j, s in enumerate(full.spots)}
    for j, spot in enumerate(subset.spots):
        k = full_columns[spot.barcode]
        # Materialize only one spot at a time, never the full dense matrix.
        recovered = dict(zip(full.indices[k], full.values[k]))
        if any(row[j] != recovered.get(i, 0) for i, row in enumerate(subset.counts)):
            raise ValueError(f"Subset count mismatch at {spot.barcode}")
    metadata = Counter(s.mouse for s in full.metadata.values())
    measured = Counter(s.mouse for s in full.spots)
    original = Counter(s.mouse for s in subset.spots)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["mouse", "metadata_spots", "full_expression_spots", "subset_spots_verified"])
        for mouse in sorted(metadata):
            writer.writerow([mouse, metadata[mouse], measured[mouse], original[mouse]])
            print(f"{mouse}: {measured[mouse]}/{metadata[mouse]} recovered; {original[mouse]} subset spots identical")
    print(f"Features: {len(full.features):,}; spots: {len(full.spots):,}")
    print(f"Duplicate symbols preserved: {len(full.features) - len({f.symbol for f in full.features}):,}")
    print(f"Stored nonzero counts: {sum(map(len, full.values)):,}")
    print("All archive checksums and all subset counts verified; no expression QC filtering applied.")


if __name__ == "__main__":
    main()
