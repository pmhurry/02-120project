"""Library-size normalization and an exploratory, reference-centered collagen score."""

from dataclasses import dataclass
import math

from data_loader import Dataset

MARKERS = ("Col1a1", "Col1a2", "Col3a1")


@dataclass
class ScoreResult:
    library_sizes: list[float]
    normalized_markers: dict[str, list[float]]
    reference_means: dict[str, float]
    reference_sds: dict[str, float]
    scores: list[float | None]  # None means an unscorable zero-library spot.


def score_dataset(data: Dataset, markers: tuple[str, ...] = MARKERS) -> ScoreResult:
    """Return log1p(count/library*10,000) and mean marker population z-scores.

    The reference is all measured spots with positive library size in this input.
    Fit once on the full analysis dataset, before filtering mouse/time/group views.
    Constant markers contribute exactly zero; zero libraries remain missing.
    Ambiguous or absent marker symbols raise rather than silently choosing rows.
    """
    if not markers or len(set(markers)) != len(markers):
        raise ValueError("Markers must be nonempty and unique")
    if not data.spots or len(data.genes) != len(data.counts):
        raise ValueError("Dataset must contain aligned genes, counts, and spots")
    libraries = [0.0] * len(data.spots)
    for row in data.counts:
        if len(row) != len(libraries):
            raise ValueError("Count row does not match spot count")
        for j, count in enumerate(row):
            if not math.isfinite(count) or count < 0 or not float(count).is_integer():
                raise ValueError("Expected finite nonnegative integer counts")
            libraries[j] += count
    valid = [j for j, total in enumerate(libraries) if total > 0]
    if not valid:
        raise ValueError("No positive-library spots available for a reference")
    normalized, means, sds = {}, {}, {}
    totals = [0.0] * len(libraries)
    for marker in markers:
        indices = [i for i, gene in enumerate(data.genes) if gene == marker]
        if len(indices) != 1:
            raise ValueError(f"Marker {marker} must match exactly one gene row; found {len(indices)}")
        row = data.counts[indices[0]]
        values = [math.log1p(row[j] / libraries[j] * 10000) if libraries[j] else math.nan
                  for j in range(len(libraries))]
        # Handle constant profiles explicitly to guarantee exact zero scores.
        constant = all(values[j] == values[valid[0]] for j in valid)
        mean = values[valid[0]] if constant else math.fsum(values[j] for j in valid) / len(valid)
        sd = 0.0 if constant else math.sqrt(math.fsum((values[j] - mean) ** 2 for j in valid) / len(valid))
        normalized[marker], means[marker], sds[marker] = values, mean, sd
        if sd:
            for j in valid:
                totals[j] += (values[j] - mean) / sd
    scores = [totals[j] / len(markers) if libraries[j] else None for j in range(len(libraries))]
    return ScoreResult(libraries, normalized, means, sds, scores)
