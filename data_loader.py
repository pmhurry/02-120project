"""Load gene-by-spot counts and align metadata by full spot barcode."""

from array import array
import csv
from dataclasses import dataclass
import math
from pathlib import Path


@dataclass(frozen=True)
class Spot:
    barcode: str
    mouse: str
    time_hours: int
    fibrogenic: bool
    x: float
    y: float


@dataclass
class Dataset:
    genes: list[str]
    counts: list[array]
    spots: list[Spot]  # Same order as columns in every counts row.
    metadata: dict[str, Spot]  # Includes spots without expression measurements.


def load_dataset(matrix_path: Path, metadata_path: Path) -> Dataset:
    """Read counts without dropping duplicate gene symbols or filling missing spots.

    Count row i corresponds to genes[i]; count column j corresponds to spots[j].
    Missing expression is represented by absence from spots, never by zero counts.
    """
    metadata = {}
    required = {
        "Spot_barcode", "Mouse", "Time_point", "Fibrogenic_spot",
        "visium_coor_x", "visium_coor_y",
    }
    with metadata_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Metadata is missing required columns")
        for line, row in enumerate(reader, start=2):
            if any(not row.get(key) for key in required):
                raise ValueError(f"Missing metadata value on record {line}")
            barcode = row["Spot_barcode"]
            if barcode in metadata:
                raise ValueError(f"Duplicate metadata barcode: {barcode}")
            if row["Fibrogenic_spot"] not in {"0", "1"}:
                raise ValueError(f"Invalid fibrogenic label: {barcode}")
            spot = Spot(
                barcode, row["Mouse"], int(row["Time_point"]),
                row["Fibrogenic_spot"] == "1",
                float(row["visium_coor_x"]), float(row["visium_coor_y"]),
            )
            if spot.time_hours < 0 or not all(map(math.isfinite, (spot.x, spot.y))):
                raise ValueError(f"Invalid time or coordinates: {barcode}")
            metadata[barcode] = spot

    genes, counts = [], []
    with matrix_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        if len(header) < 2 or header[0] != "Gene_Name":
            raise ValueError("Matrix must start with Gene_Name and spot columns")
        barcodes = header[1:]
        if any(not barcode for barcode in barcodes) or len(set(barcodes)) != len(barcodes):
            raise ValueError("Matrix spot barcodes must be nonempty and unique")
        missing = set(barcodes) - metadata.keys()
        if missing:
            raise ValueError(f"{len(missing)} matrix spot(s) lack metadata: {sorted(missing)[:3]}")
        spots = [metadata[barcode] for barcode in barcodes]
        for line, row in enumerate(reader, start=2):
            if not row:
                continue
            if len(row) != len(header) or not row[0]:
                raise ValueError(f"Invalid matrix dimensions or gene on line {line}")
            values = array("d", map(float, row[1:]))
            if any(not math.isfinite(v) or v < 0 or not v.is_integer() for v in values):
                raise ValueError(f"Expected finite nonnegative integer counts on line {line}")
            genes.append(row[0])
            counts.append(values)
    if not genes:
        raise ValueError("Matrix contains no gene rows")
    return Dataset(genes, counts, spots, metadata)
