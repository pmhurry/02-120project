"""Package full-resolution maps for the three reviewed target profiles."""
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app_data import RANKING, MAPS, load_mouse, spot_rows
from sparse_loader import ARCHIVES

with (RANKING / 'complete_ranking.csv').open(newline='') as handle:
    targets = [row['feature_id'] for row in list(csv.DictReader(handle))[:3]]

MAPS.mkdir(parents=True, exist_ok=True)
hashes = {}
for sample in ARCHIVES:
    time, mouse_id = sample.split('_')
    mouse = f't_{time}h_{mouse_id}'
    data = load_mouse(mouse)
    for target in targets:
        rows = spot_rows(data, target)
        buffer = io.StringIO(newline='')
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        name = f'{mouse}_{target}.csv.gz'
        payload = gzip.compress(buffer.getvalue().encode(), mtime=0)
        (MAPS / name).write_bytes(payload)
        hashes[name] = hashlib.sha256(payload).hexdigest()
    del data

manifest = {
    'version': 'reviewed-target-maps-v1',
    'ranking_manifest_sha256': hashlib.sha256((RANKING / 'manifest.json').read_bytes()).hexdigest(),
    'files': hashes,
}
(MAPS / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
