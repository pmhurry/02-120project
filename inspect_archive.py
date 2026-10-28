"""Compare one authors' Visium ZIP with the supplied files without extracting it.

Usage: python3 inspect_archive.py /path/to/24_m1.zip --sample 24_m1
Uses only the standard library. Does not modify either dataset.
"""

import argparse
import csv
import gzip
import hashlib
import io
from pathlib import Path
import zipfile

from data_loader import load_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--sample", required=True, help="For example, 24_m1")
    parser.add_argument("--expected-md5", help="Checksum published by the source archive")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    data = load_dataset(root / "spatial_matrix.csv", root / "Visium_Meta_data.txt")
    print("Expression barcodes equal metadata[::50]:",
          [s.barcode for s in data.spots] == list(data.metadata)[::50])
    digest = hashlib.md5(args.archive.read_bytes()).hexdigest()
    print("Archive MD5:", digest)
    if args.expected_md5 and digest != args.expected_md5:
        raise ValueError("Archive checksum differs from the published checksum")
    mouse = "t_" + args.sample.replace("_", "h_", 1)
    prefix = mouse + "_"

    with zipfile.ZipFile(args.archive) as archive:
        def member(suffix):
            matches = [n for n in archive.namelist()
                       if n.endswith(suffix) and not n.startswith("__MACOSX/")]
            if len(matches) != 1:
                raise ValueError(f"Expected one {suffix}; found {matches}")
            return matches[0]

        def compressed_text(suffix):
            return io.TextIOWrapper(gzip.GzipFile(fileobj=archive.open(member(suffix))))

        with compressed_text("barcodes.tsv.gz") as handle:
            barcodes = [line.strip() for line in handle]
        with compressed_text("features.tsv.gz") as handle:
            features = list(csv.reader(handle, delimiter="\t"))
        symbols = [row[1] for row in features]
        if symbols != data.genes:
            raise ValueError("Feature symbols/order differ; count comparison would be ambiguous")
        if len(set(barcodes)) != len(barcodes):
            raise ValueError("Archive barcodes are not unique")
        # Local export replaces the 10x '-1' suffix with '_1'.
        local_ids = [prefix + b.replace("-", "_") for b in barcodes]
        metadata_ids = {b for b, s in data.metadata.items() if s.mouse == mouse}
        print(f"Features: {len(features):,}; raw barcodes: {len(barcodes):,}")
        print(f"Metadata barcodes recovered: {len(metadata_ids & set(local_ids)):,}/{len(metadata_ids):,}")
        selected = {s.barcode: j for j, s in enumerate(data.spots) if s.mouse == mouse}
        columns = {i + 1: selected[b] for i, b in enumerate(local_ids) if b in selected}
        # Initialize zeros so absent sparse entries are compared as well.
        recovered = {j: [0] * len(features) for j in columns.values()}
        with compressed_text("matrix.mtx.gz") as handle:
            dimensions = next(line for line in handle if not line.startswith("%"))
            rows, cols, entries = map(int, dimensions.split())
            if (rows, cols) != (len(features), len(barcodes)):
                raise ValueError("Matrix dimensions do not match features/barcodes")
            seen = 0
            for line in handle:
                i, j, value = map(int, line.split())
                seen += 1
                if j in columns:
                    recovered[columns[j]][i - 1] += value
            if seen != entries:
                raise ValueError("Matrix entry count does not match header")
        mismatches = sum(value != data.counts[i][j]
                         for j, values in recovered.items() for i, value in enumerate(values))
        print(f"Compared subset spots: {len(recovered)}/{len(selected)}; count mismatches: {mismatches:,}")
        if len(recovered) != len(selected) or mismatches or not metadata_ids.issubset(local_ids):
            raise ValueError("Archive failed barcode/count reconciliation")
        with io.TextIOWrapper(archive.open(member("tissue_positions_list.csv"))) as handle:
            positions = {prefix + r[0].replace("-", "_"): r for r in csv.reader(handle)}
        matching = [b for b in metadata_ids if b in positions]
        # Legacy Space Ranger columns: barcode, in_tissue, array_row,
        # array_col, pxl_row_in_fullres, pxl_col_in_fullres.
        xy_match = sum((data.metadata[b].x, data.metadata[b].y) ==
                       (float(positions[b][5]), float(positions[b][4])) for b in matching)
        print(f"Coordinates equal full-resolution pixel (column, row): {xy_match}/{len(metadata_ids)}")
        print(f"Metadata spots flagged in tissue: {sum(positions[b][1] == '1' for b in matching)}/{len(metadata_ids)}")
        print("Spatial files:")
        for name in archive.namelist():
            if "/spatial/" in name and not name.endswith("/") and not name.startswith("__MACOSX/"):
                print(" ", name)


if __name__ == "__main__":
    main()
