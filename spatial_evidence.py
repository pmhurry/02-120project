"""All-feature sparse spatial summaries; zero-library spots are excluded explicitly."""
from array import array
from collections import defaultdict
import math
import statistics

ANNOTATION_MARKERS = {"Col1a1", "Col1a2", "Col3a1"}


def normalized_count(count, library):
    return math.log1p(10000 * count / library) if library else None


def summarize(data):
    """Keep stable feature IDs and mouse-specific groups; implicit sparse zeros count."""
    n = len(data.features)
    if len(data.spots) != len(data.indices) or len(data.spots) != len(data.values):
        raise ValueError("Sparse columns do not align with spots")
    if len({s.barcode for s in data.spots}) != len(data.spots):
        raise ValueError("Duplicate spot barcode")
    groups = {}
    libraries = []
    mouse_spots = defaultdict(list)
    mouse_times = {}
    for j, spot in enumerate(data.spots):
        if spot.mouse in mouse_times and mouse_times[spot.mouse] != spot.time_hours:
            raise ValueError("Mouse has inconsistent time points")
        mouse_times[spot.mouse] = spot.time_hours
        mouse_spots[spot.mouse].append(j)
        rows, counts = data.indices[j], data.values[j]
        if len(rows) != len(counts) or any(a >= b for a, b in zip(rows, rows[1:])):
            raise ValueError("Sparse indices must be aligned, unique, sorted")
        if any(i < 0 or i >= n for i in rows) or any(c <= 0 or not math.isfinite(c) or int(c) != c for c in counts):
            raise ValueError("Invalid sparse index/count")
        library = sum(counts)
        libraries.append(library)
        key = (spot.mouse, spot.fibrogenic)
        if key not in groups:
            groups[key] = [0, array('d', [0]) * n, array('I', [0]) * n]
        group = groups[key]
        if not library:
            continue
        group[0] += 1
        for i, count in zip(rows, counts):
            group[1][i] += normalized_count(count, library)
            group[2][i] += 1
    qc = []
    for mouse, indices in sorted(mouse_spots.items()):
        sizes = sorted(libraries[j] for j in indices)
        qc.append(dict(mouse=mouse, time_hours=mouse_times[mouse], total_spots=len(sizes),
                       retained_spots=sum(v > 0 for v in sizes), excluded_zero_library=sum(v == 0 for v in sizes),
                       library_min=min(sizes), library_median=statistics.median(sizes),
                       library_max=max(sizes), library_total=sum(sizes)))
    records = []
    for i, feature in enumerate(data.features):
        for mouse in sorted(mouse_spots):
            row = dict(feature_id=feature.feature_id, symbol=feature.symbol, mouse=mouse,
                       time_hours=mouse_times[mouse], annotation_context=("necrotic_region" if mouse_times[mouse] == 24 else "collagen_linked_region"),
                       annotation_linked_marker=feature.symbol in ANNOTATION_MARKERS)
            for label, flag in (("annotated", True), ("other", False)):
                group = groups.get((mouse, flag))
                count = group[0] if group else 0
                row[label + '_n'] = count
                row[label + '_mean'] = group[1][i] / count if count else None
                row[label + '_detection'] = group[2][i] / count if count else None
            row['difference'] = (row['annotated_mean'] - row['other_mean']
                                 if row['annotated_n'] and row['other_n'] else None)
            row['status'] = 'available' if row['difference'] is not None else 'missing_group'
            records.append(row)
    return libraries, qc, records


def equal_mouse_summaries(records):
    """Average mouse means/differences, never pool spots; require both mice per time."""
    features = defaultdict(list)
    for row in records:
        features[row['feature_id']].append(row)
    output = []
    for feature_id, rows in features.items():
        for context, times, expected in [('24h_context', (24,), 2), ('48h', (48,), 2),
                                         ('72h', (72,), 2), ('48h_72h', (48, 72), 4)]:
            selected = [r for r in rows if r['time_hours'] in times]
            valid = [r for r in selected if r['difference'] is not None]
            complete = (len(selected) == expected and len(valid) == expected
                        and all(sum(r['time_hours'] == t for r in selected) == 2 for t in times))
            row = dict(feature_id=feature_id, symbol=rows[0]['symbol'], context=context,
                       expected_mice=expected, available_mice=len(valid),
                       status='available' if complete else 'missing_mouse_or_group')
            for metric in ('annotated_mean', 'other_mean', 'difference', 'annotated_detection', 'other_detection'):
                row[metric] = math.fsum(r[metric] for r in valid) / expected if complete else None
            output.append(row)
    return output
