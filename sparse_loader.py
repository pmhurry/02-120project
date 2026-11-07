"""Stream verified Visium archives into compact sparse columns (standard library)."""

from array import array
from bisect import bisect_left
from dataclasses import dataclass
import csv
import gzip
import hashlib
import io
from pathlib import Path
import zipfile

from data_loader import Spot, load_metadata

ARCHIVES = {
    "24_m1": "e5c745814e430b83b32dc4641b5828f5",
    "24_m2": "c686c9f6982676131ddeae33280209df",
    "48_m4": "b29df9e20a484d7d9e06da267f7d6c78",
    "48_m5": "14e3d248a0bc8a40da6938acae25ee43",
    "72_m1": "531f76f5637359de201dba8bfb44f506",
    "72_m2": "418a06e1f562ab50ab80234d254d92f4",
}


@dataclass(frozen=True)
class Feature:
    feature_id: str
    symbol: str
    feature_type: str


@dataclass
class SparseDataset:
    features: list[Feature]
    spots: list[Spot]
    indices: list[array]  # Sorted feature indices, one array per spot.
    values: list[array]  # Corresponding positive integer counts.
    metadata: dict[str, Spot]

    def count(self, feature_index: int, spot_index: int) -> int:
        if not 0 <= feature_index < len(self.features):
            raise IndexError(feature_index)
        rows = self.indices[spot_index]
        pos = bisect_left(rows, feature_index)
        return self.values[spot_index][pos] if pos < len(rows) and rows[pos] == feature_index else 0

    def feature_index(self, identifier: str) -> int:
        """Prefer stable feature IDs; ambiguous symbols must be resolved explicitly."""
        matches = [i for i, f in enumerate(self.features) if f.feature_id == identifier]
        if not matches:
            matches = [i for i, f in enumerate(self.features) if f.symbol == identifier]
        if len(matches) != 1:
            raise ValueError(f"Feature {identifier!r} must resolve uniquely; found {len(matches)}")
        return matches[0]


def read_archive(path: Path, sample: str, metadata: dict[str, Spot], expected_md5: str):
    """Select only this sample's metadata barcodes; fail on incomplete coverage."""
    with path.open("rb") as handle:
        hasher = hashlib.md5()
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
        digest = hasher.hexdigest()
    if digest != expected_md5:
        raise ValueError(f"Checksum mismatch: {path}")
    mouse = "t_" + sample.replace("_", "h_", 1)
    selected = [s for s in metadata.values() if s.mouse == mouse]
    if not selected:
        raise ValueError(f"No metadata for {sample}")
    lookup = {s.barcode: j for j, s in enumerate(selected)}
    indices = [array("I") for _ in selected]
    values = [array("Q") for _ in selected]
    with zipfile.ZipFile(path) as archive:
        def compressed(suffix):
            matches = [n for n in archive.namelist()
                       if n.endswith("/raw_feature_bc_matrix/" + suffix)
                       and not n.startswith("__MACOSX/")]
            if len(matches) != 1:
                raise ValueError(f"Expected one raw matrix member {suffix}")
            return io.TextIOWrapper(gzip.GzipFile(fileobj=archive.open(matches[0])))

        with compressed("features.tsv.gz") as handle:
            rows = list(csv.reader(handle, delimiter="\t"))
        if not rows or any(len(r) != 3 or not all(r) for r in rows):
            raise ValueError("Invalid feature records")
        features = [Feature(*r) for r in rows]
        if len({f.feature_id for f in features}) != len(features):
            raise ValueError("Duplicate feature IDs")
        if any(f.feature_type != "Gene Expression" for f in features):
            raise ValueError("Expected gene-expression features only")
        with compressed("barcodes.tsv.gz") as handle:
            barcodes = [mouse + "_" + line.strip().replace("-", "_") for line in handle]
        if len(set(barcodes)) != len(barcodes):
            raise ValueError("Duplicate archive barcodes")
        if not lookup.keys() <= set(barcodes):
            raise ValueError(f"Missing metadata barcodes in {sample}")
        columns = {i + 1: lookup[b] for i, b in enumerate(barcodes) if b in lookup}
        with compressed("matrix.mtx.gz") as handle:
            if handle.readline().strip() != "%%MatrixMarket matrix coordinate integer general":
                raise ValueError("Expected integer coordinate Matrix Market")
            dimensions = next(line for line in handle if not line.startswith("%"))
            nrows, ncols, nnz = map(int, dimensions.split())
            if (nrows, ncols) != (len(features), len(barcodes)) or nnz < 0:
                raise ValueError("Matrix dimensions disagree with features/barcodes")
            seen = 0
            for line in handle:
                row, col, count = map(int, line.split())
                if not (1 <= row <= nrows and 1 <= col <= ncols) or count < 0:
                    raise ValueError("Invalid sparse coordinate or count")
                seen += 1
                j = columns.get(col)
                if j is not None and count:
                    indices[j].append(row - 1)
                    values[j].append(count)
            if seen != nnz:
                raise ValueError("Sparse entry count differs from header")
    for j, rows in enumerate(indices):
        # Matrix Market does not require sorted entries. Reject duplicate coordinates.
        pairs = sorted(zip(rows, values[j]))
        if any(a[0] == b[0] for a, b in zip(pairs, pairs[1:])):
            raise ValueError("Duplicate sparse coordinate")
        indices[j] = array("I", (r for r, _ in pairs))
        values[j] = array("Q", (v for _, v in pairs))
    return features, selected, indices, values


def load_full_dataset(source_dir: Path, metadata_path: Path) -> SparseDataset:
    metadata = load_metadata(metadata_path)
    features, spots, indices, values = [], [], [], []
    for sample, checksum in ARCHIVES.items():
        current, selected, rows, counts = read_archive(
            source_dir / f"{sample}.zip", sample, metadata, checksum)
        if features and current != features:
            raise ValueError(f"Feature IDs/symbols/order differ in {sample}")
        features = current
        spots.extend(selected)
        indices.extend(rows)
        values.extend(counts)
    if {s.barcode for s in spots} != metadata.keys() or len(spots) != len(metadata):
        raise ValueError("Full-data coverage differs from metadata")
    return SparseDataset(features, spots, indices, values, metadata)
