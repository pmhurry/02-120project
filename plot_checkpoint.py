"""Create dependency-free SVG figures and per-mouse summaries for checkpoint 1."""
import argparse
import csv
import html
import math
from pathlib import Path
from statistics import mean

from data_loader import load_dataset
from scoring import score_dataset

ROOT = Path(__file__).resolve().parent


def write_svg(path, width, height, elements):
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>'
        '<style>text{font-family:Arial,sans-serif;fill:#222;font-size:14px}</style>'
        + ''.join(elements) + '</svg>\n', encoding='utf-8')


def text(x, y, label, size=14):
    return f'<text x="{x}" y="{y}" style="font-size:{size}px">{html.escape(str(label))}</text>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mouse', help='Mouse ID; default is the first mouse alphabetically')
    parser.add_argument('--gene', default='Col1a1', help='Unique gene symbol (default: Col1a1)')
    parser.add_argument('--output', type=Path, default=ROOT / 'results')
    args = parser.parse_args()
    data = load_dataset(ROOT / 'spatial_matrix.csv', ROOT / 'Visium_Meta_data.txt')
    # Reuse the checked normalization with one marker; its centered score is not plotted.
    result = score_dataset(data, (args.gene,))
    values = result.normalized_markers[args.gene]
    measured = {s.barcode: values[i] for i, s in enumerate(data.spots)}
    mice = sorted({s.mouse for s in data.metadata.values()})
    mouse = args.mouse or mice[0]
    if mouse not in mice:
        parser.error(f'Unknown mouse {mouse!r}; choose from {mice}')
    args.output.mkdir(parents=True, exist_ok=True)
    spots = [s for s in data.metadata.values() if s.mouse == mouse]
    xmin, xmax = min(s.x for s in spots), max(s.x for s in spots)
    ymin, ymax = min(s.y for s in spots), max(s.y for s in spots)
    scale = min(470 / max(xmax-xmin, 1), 470 / max(ymax-ymin, 1))
    vmax = max(v for v in values if math.isfinite(v))
    elements = [text(25, 30, f'{mouse} | {spots[0].time_hours} h | {args.gene}', 20),
                text(25, 55, 'Subset expression; positions are full-resolution image pixels (y increases downward).'),
                text(25, 88, 'Annotations: blue = fibrogenic; light gray = other'),
                text(605, 88, 'Expression: gray = unmeasured / unscorable')]
    for panel in (0, 1):
        for spot in spots:
            x = 30 + panel*580 + (spot.x-xmin)*scale
            y = 110 + (spot.y-ymin)*scale
            value = measured.get(spot.barcode, math.nan)
            if panel == 0:
                color = '#2166ac' if spot.fibrogenic else '#dddddd'
            elif not math.isfinite(value):
                color = '#dddddd'
            else:
                fraction = value/vmax if vmax else 0
                color = f'rgb({round(255-190*fraction)},{round(247-165*fraction)},{round(188-148*fraction)})'
            label = f'{spot.barcode}; fibrogenic={spot.fibrogenic}; '
            label += f'normalized={value:.5f}' if math.isfinite(value) else 'expression missing'
            elements.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.5" fill="{color}"><title>{html.escape(label)}</title></circle>')
    elements.extend([text(25, 615, f'{len(spots)} metadata spots; {sum(s.barcode in measured for s in spots)} measured spots.'),
                     text(605, 615, f'Color range: 0 (pale yellow) to {vmax:.3f} (brown), shared across six mice.'),
                     text(25, 642, 'Normalized expression = ln(1 + count / total spot counts × 10,000). Zero expression is pale yellow.')])
    write_svg(args.output / 'spatial.svg', 1190, 665, elements)

    rows = []
    for sample in sorted(mice, key=lambda m: (next(s.time_hours for s in data.metadata.values() if s.mouse == m), m)):
        for group in (False, True):
            metadata = [s for s in data.metadata.values() if s.mouse == sample and s.fibrogenic == group]
            group_values = [measured[s.barcode] for s in metadata if s.barcode in measured and math.isfinite(measured[s.barcode])]
            rows.append(dict(mouse=sample, time_hours=next(s.time_hours for s in data.metadata.values() if s.mouse == sample),
                             fibrogenic=int(group), metadata_spots=len(metadata),
                             measured_spots=sum(s.barcode in measured for s in metadata),
                             scorable_spots=len(group_values),
                             mean_log1p_cp10k=mean(group_values) if group_values else ''))
    with (args.output / 'group_summary.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    top = max((r['mean_log1p_cp10k'] for r in rows if r['mean_log1p_cp10k'] != ''), default=1) or 1
    elements = [text(25, 30, f'{args.gene}: mean normalized expression within each mouse and annotation', 20),
                text(25, 57, 'Six mice total; two per time point. Each row is one mouse/group; spots are not independent mice.'),
                text(25, 83, 'Bars show mean ln(1 + counts per 10,000); labels show scorable / measured / metadata spots.')]
    for i, row in enumerate(rows):
        y = 120+i*38
        label = f"{row['time_hours']} h | {row['mouse']} | {'fibrogenic' if row['fibrogenic'] else 'other'}"
        elements.append(text(25, y+15, label))
        value = row['mean_log1p_cp10k']
        if value != '':
            width = value/top*350
            color = '#2166ac' if row['fibrogenic'] else '#888888'
            elements.append(f'<rect x="410" y="{y}" width="{width:.2f}" height="20" fill="{color}"/>')
            suffix = f'{value:.3f}'
        else:
            suffix = 'missing'
        elements.append(text(785, y+15, f"{suffix}; n={row['scorable_spots']} / {row['measured_spots']} / {row['metadata_spots']}"))
    elements.append(text(25, 610, 'Descriptive subset comparison; no significance test. Collagen-derived labels are not independent validation.'))
    write_svg(args.output / 'group_comparison.svg', 1190, 640, elements)
    print(f'Wrote figures and group_summary.csv to {args.output}')
    for row in rows:
        print(row)


if __name__ == '__main__':
    main()
