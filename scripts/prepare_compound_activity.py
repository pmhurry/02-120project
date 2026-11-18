"""Freeze the human galectin-3 assay dataset and scaffold splits offline."""
import argparse
import csv
import hashlib
import json
import tarfile
from collections import Counter, defaultdict
from math import isfinite, log10
from pathlib import Path
from statistics import median

from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold

from audit_compound_activity import standardized_parent


ROOT = Path(__file__).resolve().parents[1]
ASSAY = "CHEMBL5737905"
TARGET = "CHEMBL4531"
DOCUMENT = "CHEMBL5729012"
FRACTIONS = {"train": 0.70, "validation": 0.15, "test": 0.15}


def prepare(snapshot, output):
    with tarfile.open(snapshot) as archive:
        status = json.load(archive.extractfile("status.json"))
        assays = json.load(archive.extractfile(f"{TARGET}-assay.json"))
        activities = json.load(archive.extractfile(f"{TARGET}-activity.json"))
    assay, = [row for row in assays if row["assay_chembl_id"] == ASSAY]
    expected = {"assay_type": "B", "confidence_score": 9, "relationship_type": "D",
                "assay_tax_id": 9606, "target_chembl_id": TARGET,
                "document_chembl_id": DOCUMENT, "variant_sequence": None}
    if any(assay[key] != value for key, value in expected.items()):
        raise ValueError("Selected assay metadata differ from the frozen protocol")

    parents = defaultdict(list)
    excluded = Counter({"censored": 0})
    for row in activities:
        if row["assay_chembl_id"] != ASSAY:
            excluded["different assay"] += 1
            continue
        if row["standard_relation"] in {"<", ">", "<=", ">=", "≤", "≥"}:
            excluded["censored"] += 1
            continue
        if (row["standard_relation"], row["standard_type"], row["standard_units"],
            row["target_chembl_id"], row["document_chembl_id"], row["assay_type"],
            row["target_tax_id"]) != ("=", "IC50", "nM", TARGET, DOCUMENT, "B", "9606"):
            excluded["endpoint or provenance mismatch"] += 1
            continue
        if row["data_validity_comment"] or row["potential_duplicate"] == 1:
            excluded["validity flag or potential duplicate"] += 1
            continue
        try:
            value = float(row["standard_value"])
        except (TypeError, ValueError):
            value = float("nan")
        if not isfinite(value) or value <= 0:
            excluded["invalid activity"] += 1
            continue
        smiles, reason = standardized_parent(row["canonical_smiles"])
        if reason:
            excluded[reason] += 1
            continue
        parents[smiles].append((row["activity_id"], row["molecule_chembl_id"], value))

    groups = defaultdict(list)
    for smiles, measurements in sorted(parents.items()):
        scaffold = MurckoScaffold.MurckoScaffoldSmiles(smiles=smiles)
        measurements.sort()
        values = [item[2] for item in measurements]
        ic50 = median(values)
        groups[scaffold].append({
            "standardized_smiles": smiles, "murcko_scaffold": scaffold,
            "assay_chembl_id": ASSAY, "document_chembl_id": DOCUMENT,
            "source_molecule_ids": "|".join(sorted({item[1] for item in measurements})),
            "source_activity_ids": "|".join(str(item[0]) for item in measurements),
            "source_ic50_nm": "|".join(str(value) for value in values),
            "measurement_count": len(values), "ic50_nm": ic50,
            "pIC50": round(9 - log10(ic50), 10),
        })

    if len(parents) < 100 or sum(bool(scaffold) for scaffold in groups) < 20:
        raise ValueError("Assay falls below the predeclared compound/scaffold thresholds")
    # Largest groups first. Each goes to the split with the greatest
    # remaining target capacity. All acyclic structures share the empty scaffold.
    counts = Counter()
    by_split = defaultdict(list)
    for scaffold, rows in sorted(groups.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        split = max(FRACTIONS, key=lambda name: len(parents) * FRACTIONS[name] - counts[name])
        counts[split] += len(rows)
        for row in rows:
            by_split[split].append({"split": split, **row})

    if any(not by_split[split] for split in FRACTIONS):
        raise ValueError("Scaffold allocation left an empty split")
    all_rows = [row for split in FRACTIONS for row in by_split[split]]
    if max(row["pIC50"] for row in all_rows) - min(row["pIC50"] for row in all_rows) < 2:
        raise ValueError("Assay falls below the predeclared two-log-unit activity range")
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048, includeChirality=True)
    fingerprints = {
        split: [generator.GetFingerprint(Chem.MolFromSmiles(row["standardized_smiles"]))
                for row in rows]
        for split, rows in by_split.items()
    }
    summary = {}
    for split in FRACTIONS:
        rows = by_split[split]
        summary[split] = {
            "compounds": len(rows),
            "scaffold_groups": len({row["murcko_scaffold"] for row in rows}),
            "pIC50_range": [min(row["pIC50"] for row in rows), max(row["pIC50"] for row in rows)],
        }
        if split != "train":
            similarities = [max(DataStructs.BulkTanimotoSimilarity(fp, fingerprints["train"]))
                            for fp in fingerprints[split]]
            summary[split]["nearest_train_tanimoto"] = {
                "minimum": min(similarities), "median": median(similarities), "maximum": max(similarities),
            }

    output.mkdir(parents=True, exist_ok=True)
    dataset = output / "galectin3_dataset.csv"
    with dataset.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_rows)
    manifest = {
        "version": "galectin3-ic50-v1", "chembl_version": status["chembl_db_version"],
        "snapshot_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "target": TARGET, "uniprot": "P17931", "assay": ASSAY, "document": DOCUMENT,
        "rdkit": rdBase.rdkitVersion, "input_records": len(activities),
        "assay_metadata": expected,
        "endpoint": "HTRF competition IC50 (nM), exported as pIC50 = 9 - log10(IC50 in nM)",
        "parent_policy": "RDKit FragmentParent and Uncharger; canonical isomeric SMILES",
        "aggregation": "Median of exact nM values within the standardized parent and selected assay",
        "split_policy": "Size-descending Murcko groups, then scaffold SMILES; greatest remaining target count, ties in train/validation/test order",
        "excluded_from_prefiltered_snapshot": dict(excluded),
        "censored_upstream_count": None,
        "measurements_retained": sum(row["measurement_count"] for row in all_rows),
        "merged_parent_groups": sum(row["measurement_count"] > 1 for row in all_rows),
        "acyclic_compounds": len(groups.get("", [])),
        "split_fractions": FRACTIONS, "split_summary": summary,
        "similarity_fingerprint": {"radius": 2, "bits": 2048, "chirality": True},
    }
    (output / "galectin3_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=ROOT / "data/external/chembl/chembl37_shortlist.tar.gz")
    parser.add_argument("--output", type=Path, default=ROOT / "results/compound_activity")
    args = parser.parse_args()
    prepare(args.snapshot, args.output)
