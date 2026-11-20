"""Vercel ASGI entry point and stateless media downloads for Streamlit."""
from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import streamlit as st

from app_data import ROOT, annotation_rows, load_mouse, read_packaged_map, read_profile, spot_rows, verify_exports
from app_tables import filter_components, load_components, load_tissue_review_data

os.environ['SPATIAL_HTTP_EXPORTS'] = '1'
streamlit_app = st.App(Path(__file__).with_name('app.py'))
app = FastAPI(lifespan=streamlit_app.lifespan(), docs_url=None, redoc_url=None,
              openapi_url=None)

FeatureID = Annotated[str, Query(pattern=r'^[A-Za-z0-9_.-]{1,96}$')]
MouseID = Annotated[str, Query(pattern=r'^t_(24|48|72)h_m[1-5]$')]


def attachment(filename):
    return {'Content-Disposition': f'attachment; filename="{filename}"'}


@lru_cache(maxsize=1)
def ranking_inputs():
    manifest = verify_exports()
    tissue = load_tissue_review_data(manifest['input_sha256']['data/external/target_tissue_summary.csv'])
    return load_components(), tissue


def csv_chunks(table):
    yield table.head(0).to_csv(index=False)
    for start in range(0, len(table), 1000):
        yield table.iloc[start:start + 1000].to_csv(index=False, header=False)


@app.get('/exports/ranking')
def ranking(view: Literal['priority_rank', 'spatial_rank', 'feature_id'] = 'priority_rank',
            minimum: Annotated[float, Query(ge=0, le=1)] = 0, liver: bool = False,
            search: Annotated[str, Query(max_length=500)] = ''):
    frame, tissue = ranking_inputs()
    table, _, _ = filter_components(frame, tissue, view, minimum, liver, search)
    return StreamingResponse(csv_chunks(table), media_type='text/csv',
                             headers=attachment('target_evidence.csv'))


@app.get('/exports/compounds')
def compounds():
    return FileResponse(ROOT / 'results/compound_activity/reviewed_compounds.csv',
                        media_type='text/csv', filename='reviewed_compounds.csv')


@app.get('/exports/profile')
def profile(feature_id: FeatureID):
    try:
        data = read_profile(feature_id)
    except ValueError as error:
        raise HTTPException(404, 'Feature profile unavailable') from error
    return Response(json.dumps(data, indent=2), media_type='application/json',
                    headers=attachment(f'{feature_id}_evidence.json'))


@app.get('/exports/map')
def map_csv(mouse: MouseID, feature_id: FeatureID, expression: bool = False):
    if expression:
        payload = read_packaged_map(mouse, feature_id)
        if payload is None:
            try:
                rows = spot_rows(load_mouse(mouse), feature_id)
            except (FileNotFoundError, KeyError, ValueError) as error:
                raise HTTPException(404, 'Expression map unavailable') from error
            payload = pd.DataFrame(rows).to_csv(index=False)
    else:
        rows = annotation_rows(mouse)
        if not rows:
            raise HTTPException(404, 'Mouse annotations unavailable')
        payload = pd.DataFrame(rows).to_csv(index=False)
    return Response(payload, media_type='text/csv',
                    headers=attachment(f'{mouse}_{feature_id}_spots.csv'))


@app.get('/api/preview/ranking')
def preview_ranking(
    view: Literal['priority_rank', 'spatial_rank', 'feature_id'] = 'priority_rank',
    minimum: Annotated[float, Query(ge=0, le=1)] = 0,
    liver: bool = False,
    search: Annotated[str, Query(max_length=500)] = '',
    offset: Annotated[int, Query(ge=0)] = 0,
):
    frame, tissue = ranking_inputs()
    table, excluded_tractability, excluded_tissue = filter_components(
        frame, tissue, view, minimum, liver, search)
    columns = ['feature_id', 'symbol', 'human_symbol', 'human_ensembl_id', 'S', 'T', 'D',
               'priority', 'priority_rank', 'spatial_rank', 'exclusion_reasons',
               'mapping_method', 'annotation_linked_marker']
    rows = table.iloc[offset:offset + 25][columns]
    return {
        'rows': json.loads(rows.to_json(orient='records', double_precision=15)),
        'total': len(table),
        'excluded_tractability': excluded_tractability,
        'excluded_tissue': excluded_tissue,
    }


preview = ROOT / 'frontend_dist'
if preview.is_dir():
    @app.get('/preview')
    def preview_page():
        return FileResponse(preview / 'index.html')

    app.mount('/preview', StaticFiles(directory=preview, html=True))

app.mount('/', streamlit_app)
