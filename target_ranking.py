"""Fixed, descriptive target rubric. No fitted weights or inferred safety scores."""
from collections import defaultdict
import math

TIERS = {'Approved Drug': 1., 'Advanced Clinical': .8, 'Phase 1 Clinical': .7,
         'High-Quality Ligand': .6, 'Structure with Ligand': .4,
         'High-Quality Pocket': .3, 'Med-Quality Pocket': .3, 'Druggable Family': .2}
WEIGHTS = (.60, .25, .15)


def mapping_gate(rows, reverse):
    reasons = []
    ids = sorted({r['human_ensembl_id'] for r in rows})
    if not rows:
        return '', ['no_stable_id_mapping']
    if len(ids) != 1:
        reasons.append('multiple_human_targets')
    if any(r['homology_type'] != 'ortholog_one2one' for r in rows):
        reasons.append('not_one_to_one')
    if any(str(r['high_confidence']).lower() not in ('1', 'true') for r in rows):
        reasons.append('low_or_missing_confidence')
    if any(len(reverse[i]) != 1 for i in ids):
        reasons.append('multiple_mouse_ids')
    return (ids[0] if len(ids) == 1 else ''), reasons


def spatial_component(rows, time):
    selected = [r for r in rows if int(r['time_hours']) == time]
    if len(selected) != 2 or len({r['mouse'] for r in selected}) != 2:
        return None
    if any(r['difference'] in ('', None) for r in selected):
        return None
    differences = [float(r['difference']) for r in selected]
    if not all(math.isfinite(d) for d in differences):
        raise ValueError('Non-finite spatial difference')
    d = max(0., min(differences))
    return d / (1 + d)


def tractability(records):
    sm = [r for r in records if r['modality'] == 'SM']
    if not sm:
        return None
    # Partial or unrecognized records cannot establish an explicit all-false tier set.
    if {r['label'] for r in sm} != set(TIERS) or any(type(r['value']) is not bool for r in sm):
        raise ValueError('Unexpected small-molecule tractability schema')
    return max((TIERS[r['label']] for r in sm if r['value']), default=0.)


def priority(s, t, d, weights=WEIGHTS):
    if any(v is None for v in (s, t, d)):
        return None
    if any(not math.isfinite(v) or not 0 <= v <= 1 for v in (s, t, d)):
        raise ValueError('Components must be finite and bounded')
    return 100 * math.fsum(w * v for w, v in zip(weights, (s, t, d)))


def assign_ranks(rows, value, rank, eligible=lambda r: True):
    for r in rows:
        r[rank] = None
    selected = [r for r in rows if eligible(r) and r[value] is not None]
    for i, r in enumerate(sorted(selected, key=lambda r: (-r[value], r['feature_id'])), 1):
        r[rank] = i
