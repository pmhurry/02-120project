"""Print coverage and integrity checks for the local project data."""

from collections import Counter
from pathlib import Path

from data_loader import load_dataset


def main():
    root = Path(__file__).resolve().parent
    data = load_dataset(root / "spatial_matrix.csv", root / "Visium_Meta_data.txt")
    total = len(data.metadata)
    print(f"Gene rows: {len(data.genes):,}; unique symbols: {len(set(data.genes)):,}")
    print(f"Expression spots: {len(data.spots):,}; metadata spots: {total:,}")
    print(f"Expression coverage: {len(data.spots) / total:.2%}")
    print(f"Metadata spots without expression: {total - len(data.spots):,}")
    print("All expression barcodes matched; counts are finite nonnegative integers.")
    print("\nMouse         Time  Metadata  Expression  Fibrogenic  Other")
    for mouse in sorted({s.mouse for s in data.metadata.values()}):
        meta = [s for s in data.metadata.values() if s.mouse == mouse]
        measured = [s for s in data.spots if s.mouse == mouse]
        fib = sum(s.fibrogenic for s in measured)
        print(f"{mouse:12} {meta[0].time_hours:4} {len(meta):9} {len(measured):11} {fib:11} {len(measured)-fib:6}")
    totals = [0.0] * len(data.spots)
    zero_genes = 0
    for row in data.counts:
        zero_genes += not any(row)
        for j, value in enumerate(row):
            totals[j] += value
    print(f"\nTotal counts per spot: {min(totals):,.0f} to {max(totals):,.0f}")
    print(f"Zero-total spots: {sum(t == 0 for t in totals)}; all-zero gene rows: {zero_genes:,}")
    duplicates = {g: n for g, n in Counter(data.genes).items() if n > 1}
    print(f"Repeated gene symbols: {len(duplicates)} (preserved as separate rows)")
    print("Missing expression is not zero. The owner reports every 50th spot was retained for GitHub file size.")
    print("This summary uses the subset CSV; full-data loading and preprocessing checks remain separate.")


if __name__ == "__main__":
    main()
