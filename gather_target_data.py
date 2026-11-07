"""Download public target-evidence snapshots; rebuild derived tables offline by default.

Run --download to acquire/refresh sources. No expression analysis or candidate ranking.
"""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data/external"
API = "https://api.platform.opentargets.org/api/v4/graphql"
SOURCES = {
    "HOM_MouseHumanSequence.rpt": "https://www.informatics.jax.org/downloads/reports/HOM_MouseHumanSequence.rpt",
    "hgnc_complete_set.txt": "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt",
}
DISEASES = {
    "HP_0001395": "Hepatic fibrosis",
    "MONDO_0005155": "cirrhosis of liver",
    "MONDO_0005359": "drug-induced liver injury",
    "MONDO_0019542": "acute liver failure",
}
TARGET_FIELDS = """id approvedSymbol approvedName
 homologues {speciesId targetGeneId targetGeneSymbol homologyType isHighConfidence}
 tractability {label modality value}
 safetyLiabilities {event datasource url literature}
 drugAndClinicalCandidates {count rows {id maxClinicalStage
 diseases {diseaseFromSource disease {id name}}
 clinicalReports {id url clinicalStage trialOverallStatus}
 drug {id name drugType maximumClinicalStage
 mechanismsOfAction {rows {actionType mechanismOfAction targets {id approvedSymbol}}}}
 }}
"""
ASSOCIATION_QUERY = """query Associations($id:String!, $page:Int!, $size:Int!) {
 meta {name dataVersion {year month iteration}}
 disease(efoId:$id) {id name description
 associatedTargets(enableIndirect:false,page:{index:$page,size:$size}) {
 count rows {score datasourceScores{id score} datatypeScores{id score}
 target {id approvedSymbol}}}}}
"""
TARGET_QUERY = "query Targets($ids:[String!]!) {meta {name dataVersion {year month iteration}} targets(ensemblIds:$ids) {" + TARGET_FIELDS + "}}"


def write_csv(path, fields, rows):
    if path.suffix == ".gz":
        handle = io.TextIOWrapper(gzip.GzipFile(filename=str(path), mode="wb", mtime=0), newline="")
    else:
        handle = path.open("w", newline="")
    with handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def request(query, variables):
    payload = json.dumps({"query": query, "variables": variables})
    response = subprocess.run(
        ["curl", "--fail", "--silent", "--show-error", "--retry", "2",
         "--max-time", "60", API, "-H", "Content-Type: application/json",
         "--data-binary", "@-"], input=payload, capture_output=True, text=True, check=True)
    result = json.loads(response.stdout)
    if result.get("errors"):
        raise ValueError(result["errors"])
    return result["data"]


def canonical(value):
    """GraphQL collection order is not semantic for these evidence fields."""
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in value.items()}
    if isinstance(value, list):
        return sorted((canonical(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True))
    return value


def merge_evidence(a, b):
    """Union returned evidence lists; scalar disagreements must not be hidden."""
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            raise ValueError("Inconsistent API evidence fields")
        return {k: merge_evidence(a[k], b[k]) for k in a}
    if isinstance(a, list) and isinstance(b, list):
        if all(isinstance(v, dict) and "id" in v for v in a + b):
            merged = {}
            for row in a + b:
                key = row["id"]
                merged[key] = merge_evidence(merged[key], row) if key in merged else row
            return canonical(list(merged.values()))
        return canonical(list({json.dumps(v, sort_keys=True): v for v in a + b}.values()))
    if a != b:
        raise ValueError(f"Conflicting API evidence values: {a!r} versus {b!r}")
    return a


def download(resume=False):
    raw = OUT / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        if resume and (raw / name).exists():
            continue
        subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error",
                        "--retry", "2", "--max-time", "120", url,
                        "--output", str(raw / name)], check=True)
    all_data, details, release = {}, {}, None

    def cached(query, variables):
        key = hashlib.sha256(json.dumps([query, variables], sort_keys=True).encode()).hexdigest()
        path = raw / f"request_{key}.json"
        if resume and path.exists():
            return json.loads(path.read_text())
        result = request(query, variables)
        path.write_text(json.dumps(result))
        return result

    for disease_id, name in DISEASES.items():
        unique, expected = {}, None
        for size in (3000, 2000, 1000, 500, 499, 333, 250, 100):
            index = 0
            while expected is None or index * size < expected:
                response = cached(ASSOCIATION_QUERY, {"id": disease_id, "page": index, "size": size})
                disease = response["disease"]
                if not disease or disease["name"] != name:
                    raise ValueError(f"Disease resolution changed: {disease_id}")
                if release is None:
                    release = response["meta"]
                if release != response["meta"]:
                    raise ValueError("API release changed during download")
                associations = disease["associatedTargets"]
                if expected is None:
                    expected = associations["count"]
                if expected != associations["count"]:
                    raise ValueError("API count changed during pagination")
                for row in associations["rows"]:
                    row = canonical(row)
                    key = row["target"]["id"]
                    unique[key] = merge_evidence(unique[key], row) if key in unique else row
                index += 1
                print(f"{name}: {len(unique)}/{expected} unique (page size {size})", flush=True)
            if len(unique) == expected:
                break
        if len(unique) != expected:
            raise ValueError(f"Incomplete unique targets: {len(unique)}/{expected}")
        all_data[disease_id] = {"name": name, "description": disease["description"],
            "count": expected, "meta": release, "rows": [unique[k] for k in sorted(unique)]}

    # Reuse complete target annotations from same-release pages retrieved earlier.
    for path in sorted(raw.glob("HP_0001395_page_*.json")) if resume else []:
        response = json.loads(path.read_text())
        if response["meta"] != release:
            continue
        for row in response["disease"]["associatedTargets"]["rows"]:
            t = canonical(row["target"])
            details[t["id"]] = merge_evidence(details[t["id"]], t) if t["id"] in details else t
    needed = sorted({r["target"]["id"] for d in all_data.values() for r in d["rows"]} - details.keys())
    for start in range(0, len(needed), 50):
        ids = needed[start:start + 50]
        response = cached(TARGET_QUERY, {"ids": ids})
        if response["meta"] != release or {t['id'] for t in response['targets']} != set(ids):
            raise ValueError("Incomplete targets or mixed release")
        for t in response["targets"]:
            details[t["id"]] = canonical(t)
        print(f"Additional target annotations: {min(start+50,len(needed))}/{len(needed)}", flush=True)
    for disease in all_data.values():
        for row in disease["rows"]:
            row["target"] = details[row["target"]["id"]]
    (raw / "opentargets_evidence.json").write_text(json.dumps(all_data))
    snapshots = []
    for name, url in {**SOURCES, "opentargets_evidence.json": API}.items():
        data = (raw / name).read_bytes()
        target = OUT / (name + ".gz")
        # Fixed gzip timestamp makes offline checks stable.
        target.write_bytes(gzip.compress(data, mtime=0))
        snapshots.append({"file": target.name, "source_url": url,
                          "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                          "uncompressed_sha256": hashlib.sha256(data).hexdigest()})
    (OUT / "manifest.json").write_text(json.dumps({
        "retrieved_at": datetime.now(ZoneInfo("America/New_York")).isoformat(),
        "diseases": DISEASES, "association_query": ASSOCIATION_QUERY, "target_query": TARGET_QUERY, "files": snapshots,
        "page_sizes": [3000, 2000, 1000, 500, 499, 333, 250, 100],
        "pagination": "Merge unique IDs across page sizes; require exact API total",

        "opentargets_releases": {k: v["meta"] for k, v in all_data.items()},
    }, indent=2) + "\n")


def text_snapshot(name):
    return gzip.open(OUT / (name + ".gz"), "rt")


def build():
    manifest = json.loads((OUT / "manifest.json").read_text())
    for entry in manifest["files"]:
        if hashlib.sha256((OUT / entry["file"]).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Snapshot checksum failed: {entry['file']}")
    with text_snapshot("hgnc_complete_set.txt") as handle:
        hgnc = {r["hgnc_id"]: r for r in csv.DictReader(handle, delimiter="\t")}
    groups = defaultdict(list)
    with text_snapshot("HOM_MouseHumanSequence.rpt") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            groups[row["DB Class Key"]].append(row)
    mappings = []
    for group, rows in groups.items():
        mice = [r for r in rows if r["NCBI Taxon ID"] == "10090"]
        humans = [r for r in rows if r["NCBI Taxon ID"] == "9606"]
        for mouse in mice:
            for human in humans:
                gene = hgnc.get(human["HGNC ID"], {})
                mappings.append({"homology_group": group, "mouse_symbol": mouse["Symbol"],
                    "mouse_mgi_id": mouse["Mouse MGI ID"], "human_hgnc_id": human["HGNC ID"],
                    "human_symbol": gene.get("symbol", human["Symbol"]),
                    "human_ensembl_id": gene.get("ensembl_gene_id", ""),
                    "group_mouse_genes": len(mice), "group_human_genes": len(humans)})
    write_csv(OUT / "mouse_human_homology.csv", list(mappings[0]), mappings)
    with text_snapshot("opentargets_evidence.json") as handle:
        evidence = json.load(handle)
    if len({json.dumps(d["meta"], sort_keys=True) for d in evidence.values()}) != 1:
        raise ValueError("Mixed Open Targets releases in evidence snapshot")
    associations, targets, orthologs = [], {}, {}
    for disease_id, disease in evidence.items():
        if disease["count"] != len(disease["rows"]):
            raise ValueError("Incomplete evidence snapshot")
        for row in disease["rows"]:
            t = row["target"]
            clinical = t["drugAndClinicalCandidates"]
            if clinical["count"] != len(clinical["rows"]):
                raise ValueError(f"Incomplete clinical candidate records for {t['id']}")
            if t["id"] not in targets:
                targets[t["id"]] = t
            elif targets[t["id"]] != t:
                targets[t["id"]] = merge_evidence(targets[t["id"]], t)
            associations.append({"disease_id": disease_id, "disease_name": disease["name"],
                "human_ensembl_id": t["id"], "human_symbol": t["approvedSymbol"],
                "association_score": row["score"],
                "datasource_scores": json.dumps(row["datasourceScores"], sort_keys=True),
                "datatype_scores": json.dumps(row["datatypeScores"], sort_keys=True),
                "indirect_associations": False})
            for h in t["homologues"]:
                if h["speciesId"] != "10090":
                    continue
                orthologs[(h["targetGeneId"], t["id"])] = {
                    "mouse_feature_id": h["targetGeneId"], "mouse_symbol": h["targetGeneSymbol"],
                    "human_ensembl_id": t["id"], "human_symbol": t["approvedSymbol"],
                    "homology_type": h["homologyType"], "high_confidence": h["isHighConfidence"]}
    write_csv(OUT / "disease_target_associations.csv", list(associations[0]), associations)
    write_csv(OUT / "target_mouse_orthologs.csv", list(next(iter(orthologs.values()))), orthologs.values())
    details = [{"human_ensembl_id": t["id"], "human_symbol": t["approvedSymbol"],
                "human_name": t["approvedName"], "tractability": json.dumps(t["tractability"]),
                "safety_liabilities": json.dumps(t["safetyLiabilities"]),
                "drug_and_clinical_candidates": json.dumps(t["drugAndClinicalCandidates"])}
               for t in targets.values()]
    write_csv(OUT / "target_annotations.csv.gz", list(details[0]), details)
    # Only the feature table is needed to report mapping coverage.
    with zipfile.ZipFile(ROOT / "data/source/24_m1.zip") as archive:
        members = [n for n in archive.namelist() if n.endswith("/raw_feature_bc_matrix/features.tsv.gz")
                   and not n.startswith("__MACOSX/")]
        if len(members) != 1:
            raise ValueError("Ambiguous source feature table")
        with io.TextIOWrapper(gzip.GzipFile(fileobj=archive.open(members[0]))) as handle:
            features = list(csv.reader(handle, delimiter="\t"))
    by_id, by_symbol = defaultdict(list), defaultdict(list)
    for row in orthologs.values():
        by_id[row["mouse_feature_id"]].append(row)
    for row in mappings:
        by_symbol[row["mouse_symbol"]].append(row)
    coverage = []
    symbol_counts = Counter(r[1] for r in features)
    for feature_id, symbol, _ in features:
        stable = by_id.get(feature_id.split(".")[0], [])
        fallback = by_symbol.get(symbol, [])
        ids = sorted({r["human_ensembl_id"] for r in stable or fallback if r["human_ensembl_id"]})
        method = "opentargets_stable_id" if stable else "mgi_exact_symbol_requires_review" if fallback else "unmapped"
        coverage.append({"mouse_feature_id": feature_id, "mouse_symbol": symbol,
            "duplicate_dataset_symbol": symbol_counts[symbol] > 1, "mapping_method": method,
            "human_ensembl_ids": "|".join(ids), "human_mapping_count": len(ids),
            "has_collected_disease_evidence": bool(set(ids) & targets.keys())})
    write_csv(OUT / "feature_mapping_coverage.csv", list(coverage[0]), coverage)
    summary = {"features": len(features), "homology_pairs": len(mappings),
        "mapping_methods": dict(Counter(r["mapping_method"] for r in coverage)),
        "features_with_human_ensembl_mapping": sum(bool(r["human_ensembl_ids"]) for r in coverage),
        "features_with_collected_disease_evidence": sum(r["has_collected_disease_evidence"] for r in coverage),
        "unique_annotated_human_targets": len(targets), "disease_associations": len(associations),
        "disease_counts": {k: v["count"] for k, v in evidence.items()}}
    (OUT / "coverage_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Reuse same-release cached downloads")
    args = parser.parse_args()
    if args.download:
        download(resume=args.resume)
    elif args.resume:
        parser.error("--resume requires --download")
    build()
