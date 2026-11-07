"""Snapshot and summarize normal human tissue expression for target safety review."""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import zipfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data/external"
SOURCES = {
    "hpa_rna_tissue_consensus.tsv.zip": "https://www.proteinatlas.org/download/tsv/rna_tissue_consensus.tsv.zip",
    "hpa_normal_ihc_data.tsv.zip": "https://www.proteinatlas.org/download/tsv/normal_ihc_data.tsv.zip",
}


def archive_rows(path, required):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError(f"Corrupt ZIP: {path}")
        members = [n for n in archive.namelist() if n.endswith(".tsv")]
        if len(members) != 1:
            raise ValueError("Expected one tissue TSV")
        with io.TextIOWrapper(archive.open(members[0])) as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if not required <= set(reader.fieldnames or []):
                raise ValueError("Missing tissue columns")
            yield from reader


def collect_rna(rows):
    values = defaultdict(dict)
    for row in rows:
        gene, tissue = row["Gene"], row["Tissue"].lower()
        value = float(row["nTPM"])
        if not gene or not tissue or not math.isfinite(value) or value < 0:
            raise ValueError("Invalid tissue RNA value")
        if tissue in values[gene]:
            raise ValueError("Duplicate gene/tissue RNA measurement")
        values[gene][tissue] = value
    return values


def rna_summary(values):
    non_liver = {t: v for t, v in values.items() if t != "liver"}
    maximum = max(non_liver.values()) if non_liver else None
    return {"rna_tissues_measured": len(values), "liver_ntpm": values.get("liver"),
            "max_non_liver_ntpm": maximum,
            "max_non_liver_tissues": "|".join(sorted(t for t, v in non_liver.items() if v == maximum)),
            "non_liver_tissues_ge_1_ntpm": sum(v >= 1 for v in non_liver.values()) if non_liver else None}


def record_download():
    files = []
    for name, url in SOURCES.items():
        path = OUT / name
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"Corrupt ZIP: {name}")
        files.append({"file": name, "source_url": url,
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (OUT / "tissue_manifest.json").write_text(json.dumps({
        "retrieved_at": datetime.now(ZoneInfo("America/New_York")).isoformat(),
        "release": "Human Protein Atlas 25.1; Ensembl 109",
        "release_source": "https://www.proteinatlas.org/humanproteome/tissue/data",
        "licence": "https://www.proteinatlas.org/about/licence",
        "files": files,
    }, indent=2) + "\n")


def build():
    manifest = json.loads((OUT / "tissue_manifest.json").read_text())
    for entry in manifest["files"]:
        if hashlib.sha256((OUT / entry["file"]).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Tissue checksum failed: {entry['file']}")
    rna = collect_rna(archive_rows(OUT / "hpa_rna_tissue_consensus.tsv.zip", {"Gene", "Tissue", "nTPM"}))
    protein = defaultdict(list)
    levels, reliability = Counter(), Counter()
    for row in archive_rows(OUT / "hpa_normal_ihc_data.tsv.zip",
                            {"Gene", "Tissue", "Cell type", "Level", "Reliability"}):
        if not row["Gene"] or not row["Tissue"]:
            raise ValueError("Missing protein gene/tissue")
        if row["Level"] not in {"Not detected", "Low", "Medium", "High", "N/A", "Ascending", "Descending", "Not representative"}:
            raise ValueError(f"Unknown protein level: {row['Level']!r}")
        protein[row["Gene"]].append(row)
        levels[row["Level"]] += 1
        reliability[row["Reliability"]] += 1
    targets = {}
    with (OUT / "disease_target_associations.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            targets[row["human_ensembl_id"]] = row["human_symbol"]
    results = []
    for gene, symbol in sorted(targets.items()):
        p = protein.get(gene, [])
        detected = sorted({row["Tissue"] for row in p
                           if row["Tissue"].lower() != "liver" and row["Level"] in {"Low", "Medium", "High"}})
        results.append({"human_ensembl_id": gene, "human_symbol": symbol,
            "rna_coverage": "available" if gene in rna else "missing",
            **rna_summary(rna.get(gene, {})),
            "protein_coverage": "available" if any(r["Level"] in {"Not detected", "Low", "Medium", "High"} for r in p) else "missing",
            "protein_rows_measured": sum(r["Level"] in {"Not detected", "Low", "Medium", "High"} for r in p),
            "protein_rows": len(p), "protein_non_liver_detected_tissues": "|".join(detected),
            "protein_reliability_counts": json.dumps(dict(Counter(row["Reliability"] for row in p)), sort_keys=True)})
    with (OUT / "target_tissue_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    summary = {"rna_genes": len(rna), "rna_rows": sum(map(len, rna.values())),
        "rna_tissues": len({t for values in rna.values() for t in values}),
        "protein_genes": len(protein), "protein_rows": sum(map(len, protein.values())),
        "protein_tissues": len({row['Tissue'] for rows in protein.values() for row in rows}),
        "protein_levels": dict(levels), "protein_reliability": dict(reliability),
        "annotated_targets": len(targets), "targets_with_rna": sum(g in rna for g in targets),
        "targets_with_protein_rows": sum(g in protein for g in targets),
        "targets_with_measured_protein": sum(r["protein_coverage"] == "available" for r in results)}
    (OUT / "tissue_coverage_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--record-download", action="store_true", help="Record manually downloaded source ZIPs")
    args = parser.parse_args()
    if args.download:
        OUT.mkdir(parents=True, exist_ok=True)
        for name, url in SOURCES.items():
            subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error",
                            "--retry", "2", "--max-time", "120", url, "-o", str(OUT / name)], check=True)
    if args.download or args.record_download:
        record_download()
    build()
