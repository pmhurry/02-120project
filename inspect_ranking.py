"""Build offline ranking exports from checked spatial and external evidence snapshots."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
from gather_target_data import DISEASES, write_csv
from target_ranking import mapping_gate, spatial_component, tractability, priority, assign_ranks, WEIGHTS

ROOT = Path(__file__).resolve().parent
csv.field_size_limit(10000000)


def read(path):
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as f:
        return list(csv.DictReader(f))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(disease='HP_0001395', output=None):
    ext, spatial = ROOT / 'data/external', ROOT / 'results/spatial'
    out = Path(output) if output else ROOT / 'results/ranking' / disease
    out.mkdir(parents=True, exist_ok=True)
    inputs = [spatial / 'per_mouse.csv.gz', spatial / 'manifest.json',
              ext / 'target_mouse_orthologs.csv', ext / 'feature_mapping_coverage.csv',
              ext / 'disease_target_associations.csv', ext / 'target_annotations.csv.gz',
              ext / 'target_tissue_summary.csv', ext / 'manifest.json', ext / 'tissue_manifest.json',
              ROOT / 'target_ranking.py', ROOT / 'inspect_ranking.py', ROOT / 'ENGINE_DESIGN.md']
    manifest = json.loads((spatial / 'manifest.json').read_text())
    for name, expected in manifest['output_sha256'].items():
        if sha(spatial / name) != expected:
            raise ValueError(f'Spatial checksum failed: {name}')
    # Derived external tables are rebuilt only after their raw snapshots pass checks.
    from gather_target_data import build as rebuild_targets
    from gather_tissue_data import build as rebuild_tissues
    rebuild_targets()
    rebuild_tissues()
    by_feature, orthologs, reverse = defaultdict(list), defaultdict(list), defaultdict(set)
    for r in read(spatial / 'per_mouse.csv.gz'):
        by_feature[r['feature_id']].append(r)
    for r in read(ext / 'target_mouse_orthologs.csv'):
        orthologs[r['mouse_feature_id']].append(r)
        reverse[r['human_ensembl_id']].add(r['mouse_feature_id'])
    coverage = {r['mouse_feature_id']: r for r in read(ext / 'feature_mapping_coverage.csv')}
    targets = {r['human_ensembl_id']: r for r in read(ext / 'target_annotations.csv.gz')}
    tissues = {r['human_ensembl_id']: r for r in read(ext / 'target_tissue_summary.csv')}
    associations = {r['human_ensembl_id']: r for r in read(ext / 'disease_target_associations.csv') if r['disease_id'] == disease}
    rows, profiles = [], []
    for fid, mice in sorted(by_feature.items()):
        human, reasons = mapping_gate(orthologs[fid.split('.')[0]], reverse)
        s48, s72 = spatial_component(mice, 48), spatial_component(mice, 72)
        s = (s48 + s72) / 2 if s48 is not None and s72 is not None else None
        enriched = any(v is not None and v > 0 for v in (s48, s72))
        target, assoc = targets.get(human), associations.get(human)
        t = tractability(json.loads(target['tractability'])) if target else None
        d = float(assoc['association_score']) if assoc else None
        exclusions = list(reasons)
        if not enriched:
            exclusions.append('not_reproducibly_positive')
        for label, value in [('spatial', s), ('tractability', t), ('selected_disease', d)]:
            if value is None:
                exclusions.append('missing_' + label)
        row = dict(feature_id=fid, symbol=mice[0]['symbol'], human_ensembl_id=human,
                   human_symbol=target['human_symbol'] if target else '',
                   mapping_method=coverage[fid]['mapping_method'],
                   provisional_human_ids=coverage[fid]['human_ensembl_ids'], mapping_reasons='|'.join(reasons),
                   annotation_linked_marker=mice[0]['annotation_linked_marker'],
                   S_48=s48, S_72=s72, S=s, T=t, D=d, disease_id=disease,
                   disease_name=DISEASES[disease], reproducibly_positive=enriched,
                   exclusion_reasons='|'.join(exclusions),
                   priority=priority(s, t, d) if not exclusions else None)
        row['priority_spatial_heavy'] = priority(s, t, d, (.80, .15, .05)) if not exclusions else None
        row['priority_equal_components'] = priority(s, t, d, (1/3, 1/3, 1/3)) if not exclusions else None
        for time, component in [(48, s48), (72, s72)]:
            row[f'priority_{time}h'] = (priority(component, t, d)
                if not reasons and component is not None and component > 0 else None)
        rows.append(row)
        liabilities = json.loads(target['safety_liabilities']) if target else None
        profiles.append(dict(feature_id=fid, human_ensembl_id=human,
            mapping_accepted=not reasons, mouse_evidence=mice,
            disease_evidence=assoc, tractability=json.loads(target['tractability']) if target else None,
            liability_status=('data unavailable' if liabilities is None else
                              'reported liabilities present' if liabilities else 'none reported in collected sources'),
            reported_liabilities=liabilities,
            drug_and_clinical_candidates=json.loads(target['drug_and_clinical_candidates']) if target else None,
            tissue_summary=tissues.get(human),
            full_tissue_profile_sources=['data/external/hpa_rna_tissue_consensus.tsv.zip', 'data/external/hpa_normal_ihc_data.tsv.zip'],
            source_links=([f'https://platform.opentargets.org/target/{human}',
                           f'https://www.proteinatlas.org/{human}'] if human else [])))
    assign_ranks(rows, 'S', 'spatial_rank')
    assign_ranks(rows, 'priority', 'priority_rank')
    for variant in ['spatial_heavy', 'equal_components', '48h', '72h']:
        assign_ranks(rows, 'priority_' + variant, 'rank_' + variant)
    write_csv(out / 'components.csv', list(rows[0]), rows)
    for name, rank in [('spatial_screen.csv', 'spatial_rank'), ('complete_ranking.csv', 'priority_rank')]:
        selected = sorted((r for r in rows if r[rank] is not None), key=lambda r: r[rank])
        write_csv(out / name, list(rows[0]), selected)
    with gzip.GzipFile(filename=str(out / 'evidence_profiles.jsonl.gz'), mode='wb', mtime=0) as f:
        for profile in profiles:
            f.write((json.dumps(profile, sort_keys=True) + '\n').encode())
    spatial_top = {r['feature_id'] for r in rows if r['spatial_rank'] and r['spatial_rank'] <= 10}
    complete_top = {r['feature_id'] for r in rows if r['priority_rank'] and r['priority_rank'] <= 10}
    summary = dict(features=len(rows), mapped_gate_pass=sum(not r['mapping_reasons'] for r in rows),
        reproducibly_positive=sum(r['reproducibly_positive'] for r in rows),
        spatial_ranked=sum(r['spatial_rank'] is not None for r in rows),
        complete_ranked=sum(r['priority_rank'] is not None for r in rows),
        exclusion_counts=dict(Counter(reason for r in rows for reason in r['exclusion_reasons'].split('|') if reason)),
        top10_overlap=len(spatial_top & complete_top))
    config = dict(version='ranking-v1', disease_id=disease, disease_name=DISEASES[disease],
        weights=dict(zip(('S', 'T', 'D'), WEIGHTS)), tie_break='stable feature ID ascending',
        missing='empty CSV cells; no weight renormalization', safety='context only; no score',
        source_versions={name: json.loads((ext / name).read_text()) for name in ['manifest.json', 'tissue_manifest.json']},
        input_sha256={str(p.relative_to(ROOT)): sha(p) for p in inputs}, coverage=summary,
        output_sha256={p.name: sha(p) for p in sorted(out.iterdir()) if p.name != 'manifest.json'})
    (out / 'manifest.json').write_text(json.dumps(config, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disease', choices=DISEASES, default='HP_0001395')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    build(args.disease, args.output)
