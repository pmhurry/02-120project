"""Summarize ChEMBL activity snapshots before selecting a modeling endpoint."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from math import isfinite
from pathlib import Path
from statistics import median

from rdkit import Chem, rdBase
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem.Scaffolds import MurckoScaffold


TARGETS = {"CD74": "CHEMBL4692", "LGALS3": "CHEMBL4531", "CTSS": "CHEMBL2954"}
UNCHARGER = rdMolStandardize.Uncharger()


def audit(activities, assays, selected_assay_ids=None):
    """Group accepted activity by assay and standardized parent compound."""
    groups = defaultdict(lambda: defaultdict(list))
    exclusions = Counter()
    assay_ids = {row["assay_chembl_id"] for row in assays}
    if selected_assay_ids is not None:
        assay_ids &= selected_assay_ids
    for row in activities:
        assay_id = row["assay_chembl_id"]
        if assay_id not in assay_ids:
            exclusions["assay outside scope"] += 1
            continue
        if row["data_validity_comment"] or row["potential_duplicate"] == 1:
            exclusions["validity flag or potential duplicate"] += 1
            continue
        smiles = row["canonical_smiles"]
        molecule = Chem.MolFromSmiles(smiles) if smiles else None
        if molecule is None:
            exclusions["missing or invalid structure"] += 1
            continue
        parent = UNCHARGER.uncharge(rdMolStandardize.FragmentParent(molecule))
        if parent.GetNumAtoms() == 0:
            exclusions["empty parent"] += 1
            continue
        value = float(row["standard_value"])
        if not isfinite(value) or value <= 0:
            exclusions["invalid activity"] += 1
            continue
        groups[assay_id][Chem.MolToSmiles(parent, isomericSmiles=True)].append(value)
    return groups, exclusions


def summarize(groups, by_assay=False):
    compounds = {smiles for group in groups.values() for smiles in group}
    scaffolds = Counter()
    for smiles in compounds:
        scaffold = MurckoScaffold.MurckoScaffoldSmiles(smiles=smiles)
        scaffolds[scaffold] += 1
    values = [median(values) for group in groups.values() for values in group.values()]
    result = {
        "assays": len(groups),
        "compound_count": len(compounds),
        "nonempty_scaffolds": len(scaffolds) - ("" in scaffolds),
        "acyclic_compounds": scaffolds.get("", 0),
        "largest_scaffold_group": max(scaffolds.values(), default=0),
        "assay_compound_median_range_nm": [min(values), max(values)] if values else None,
    }
    if by_assay:
        result["accepted_measurements"] = sum(
            len(values) for group in groups.values() for values in group.values()
        )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--assays", nargs="+", help="Restrict to named comparable assay IDs")
    args = parser.parse_args()
    report = {"rdkit": rdBase.rdkitVersion, "targets": {}}
    for symbol, target in TARGETS.items():
        sources = [args.snapshot / f"{target}-{kind}.json" for kind in ("activity", "assay")]
        activities, assays = [json.loads(source.read_text()) for source in sources]
        groups, exclusions = audit(activities, assays, set(args.assays) if args.assays else None)
        descriptions = {row["assay_chembl_id"]: row["description"] for row in assays}
        largest = sorted(groups, key=lambda key: (-len(groups[key]), key))[:5]
        report["targets"][symbol] = {
            "chembl_id": target,
            "input_sha256": {source.name: hashlib.sha256(source.read_bytes()).hexdigest()
                             for source in sources},
            "preliminary_records": len(activities),
            "excluded": dict(exclusions),
            **summarize(groups, by_assay=True),
            "largest_assays": {
                key: {"description": descriptions[key], **summarize({key: groups[key]})}
                for key in largest
            },
        }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
