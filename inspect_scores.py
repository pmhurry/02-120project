"""Run the checkpoint-1 score on the supplied subset without changing data."""
from pathlib import Path
from data_loader import load_dataset
from scoring import score_dataset


def main():
    root = Path(__file__).resolve().parent
    data = load_dataset(root / "spatial_matrix.csv", root / "Visium_Meta_data.txt")
    result = score_dataset(data)
    valid = [value for value in result.scores if value is not None]
    print(f"Subset only: {len(data.spots)} measured / {len(data.metadata)} metadata spots")
    print(f"Reference: {len(valid)} positive-library spots across all six samples")
    print(f"Unscorable zero-library spots: {len(data.spots) - len(valid)}")
    print(f"Score range: {min(valid):.4f} to {max(valid):.4f}; mean: {sum(valid)/len(valid):.6f}")
    print("Marker reference statistics (log1p counts per 10,000; population SD):")
    for marker in result.reference_means:
        print(f"  {marker}: mean={result.reference_means[marker]:.6f}, SD={result.reference_sds[marker]:.6f}")


if __name__ == "__main__":
    main()
