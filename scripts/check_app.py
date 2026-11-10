"""Integration checks against actual exports; run with .venv/bin/python."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest
from app_data import RANKING, read_components

app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=120).run()
assert not app.exception, [e.message for e in app.exception]
with (RANKING / 'complete_ranking.csv').open() as handle:
    expected = list(csv.DictReader(handle))
shown = app.dataframe[0].value
for i in range(5):
    assert shown.iloc[i].feature_id == expected[i]['feature_id']
    assert shown.iloc[i].priority_rank == int(expected[i]['priority_rank'])
    assert abs(shown.iloc[i].priority - float(expected[i]['priority'])) < 1e-10

for symbol in ['Cd74', 'Lgals3', 'Ctss', 'Col3a1']:
    app.text_input[0].set_value(symbol).run()
    assert not app.exception
    exact = next(r for r in read_components() if r['symbol'] == symbol)
    app.selectbox[0].set_value(exact['feature_id']).run()
    shown = app.dataframe[1].value.iloc[0]
    assert abs(shown.priority - float(exact['priority'])) < 1e-10
    assert shown.priority_rank == int(exact['priority_rank'])

app.radio[0].set_value('All features / mapping audit').run()
app.text_input[0].set_value('Lyz2').run()
assert not app.exception
assert app.dataframe[0].value.iloc[0].exclusion_reasons
assert app.dataframe[0].value.priority_rank.isna().all()
for time in [24, 72, 48]:
    app.selectbox[1].set_value(time).run()
    assert not app.exception
    assert all(f't_{time}h_' in x for x in app.selectbox[2].options)
    app.selectbox[2].set_value(app.selectbox[2].options[1]).run()
    assert not app.exception
app.text_input[0].set_value('no_matching_target_1234').run()
assert not app.exception
assert app.dataframe[0].value.empty
print('App checks passed: top-five CLI ranks, four target scores, excluded Lyz2, all time/mouse selectors, empty search.')

if '--expression' in sys.argv:
    app.text_input[0].set_value('Cd74').run()
    app.selectbox[2].set_value('t_48h_m4').run()
    app.radio[1].set_value('Selected target expression').run(timeout=120)
    assert not app.exception, [e.message for e in app.exception]
    assert any('2,965 measured spots; 0 missing' in x.value for x in app.caption)
    assert app.get('download_button')
    print('Actual full-data expression layer rendered successfully for t_48h_m4 / Cd74.')
