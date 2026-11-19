"""Integration checks against actual exports; run with .venv/bin/python."""
import csv
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest
import streamlit as st
from app_data import RANKING, read_components, read_profile, spot_rows, load_mouse

app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=120).run()
assert not app.exception, [e.message for e in app.exception]
with (RANKING / 'complete_ranking.csv').open() as handle:
    expected = list(csv.DictReader(handle))
shown = app.dataframe[0].value
for i in range(5):
    assert shown.iloc[i].feature_id == expected[i]['feature_id']
    assert shown.iloc[i].priority_rank == int(expected[i]['priority_rank'])
    assert abs(shown.iloc[i].priority - float(expected[i]['priority'])) < 1e-10

app.select_slider[0].set_value(1.0).run()
assert app.dataframe[0].value['T'].eq(1).all()
assert len(app.dataframe[0].value) < min(len(expected), 250)
app.select_slider[0].set_value(0.0).run()
assert list(app.dataframe[0].value.feature_id.head(5)) == [r['feature_id'] for r in expected[:5]]
app.checkbox[0].check().run()
assert not app.exception
assert any('additionally excluded by the liver RNA coverage filter' in c.value for c in app.caption)
app.checkbox[0].uncheck().run()

for symbol in ['Cd74', 'Lgals3', 'Ctss', 'Col3a1']:
    app.text_input[0].set_value(symbol).run()
    assert not app.exception
    exact = next(r for r in read_components() if r['symbol'] == symbol)
    app.selectbox[0].set_value(exact['feature_id']).run()
    shown = app.dataframe[1].value.iloc[0]
    assert abs(shown.priority - float(exact['priority'])) < 1e-10
    assert shown.priority_rank == int(exact['priority_rank'])

assert any('No curated compound evidence' in item.value for item in app.info)
reviewed = ROOT / 'results/compound_activity/reviewed_compounds.csv'
with reviewed.open(newline='') as handle:
    compounds = list(csv.DictReader(handle))
for target in ('Cd74', 'Lgals3', 'Ctss'):
    with patch.object(st, 'download_button', wraps=st.download_button) as downloads, \
         patch.object(st, 'link_button', wraps=st.link_button) as links:
        app.text_input[0].set_value(target).run()
    assert not app.exception
    displayed = '\n'.join(item.value for item in app.markdown)
    for entry in (entry for entry in compounds if entry['target'] == target.upper()):
        for field in ('compound', 'compound_id', 'target_direction', 'compound_action',
                      'target_experiment', 'counter_evidence'):
            assert entry[field] in displayed
        if entry['activity_value']:
            assert f"{entry['activity_value']} {entry['activity_unit']}" in displayed
        source_urls = (entry['target_sources'] + ' | ' + entry['compound_sources']).split(' | ')
        assert set(source_urls) <= {call.args[1] for call in links.call_args_list}
    download_data = {call.args[0]: call.args[1] for call in downloads.call_args_list}
    assert download_data['Download reviewed compound evidence (CSV)'] == reviewed.read_bytes()
    profile = read_profile(app.selectbox[0].value)
    assert json.loads(download_data['Download complete selected evidence profile (JSON)']) == profile
    rendered_json = [json.loads(item.value) for item in app.json]
    assert profile['tissue_summary'] in rendered_json
    assert profile['reported_liabilities'] in rendered_json

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
    with patch.object(st, 'download_button', wraps=st.download_button) as downloads:
        app.radio[1].set_value('Selected target expression').run(timeout=120)
    calls = [call.args for call in downloads.call_args_list]
    map_csv = next(args[1] for args in calls if args[0].startswith('Download displayed map data'))
    if isinstance(map_csv, bytes):
        map_csv = map_csv.decode()
    actual = list(csv.DictReader(map_csv.splitlines()))
    expected_rows = spot_rows(load_mouse('t_48h_m4'), 'ENSMUSG00000024610')
    assert len(actual) == len(expected_rows)
    for row, expected_row in zip(actual, expected_rows):
        assert row['barcode'] == expected_row['barcode']
        assert row['annotated'] == str(expected_row['annotated'])
        assert float(row['expression']) == expected_row['expression']
    reviewed_csv = next(args[1] for args in calls if args[0].startswith('Download reviewed compound'))
    assert reviewed_csv == (ROOT / 'results/compound_activity/reviewed_compounds.csv').read_bytes()
    assert not app.exception, [e.message for e in app.exception]
    assert any('2,965 measured spots; 0 missing' in x.value for x in app.caption)
    assert app.get('download_button')
    print('Actual full-data expression layer rendered successfully for t_48h_m4 / Cd74.')
