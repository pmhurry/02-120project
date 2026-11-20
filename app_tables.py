"""Shared ranking and tissue table operations for the app and HTTP exports."""
import hashlib

import pandas as pd

from app_data import ROOT, read_components

VIEWS = {'Complete-evidence ranking': 'priority_rank',
         'Spatial-only screen': 'spatial_rank',
         'All features / mapping audit': 'feature_id'}


def load_components():
    frame = pd.DataFrame(read_components()).replace('', None)
    numeric = ['S', 'S_48', 'S_72', 'T', 'D', 'priority', 'priority_rank', 'spatial_rank',
               'rank_spatial_heavy', 'rank_equal_components', 'rank_48h', 'rank_72h']
    for column in numeric:
        frame[column] = pd.to_numeric(frame[column], errors='coerce')
    return frame


def load_tissue_review_data(expected_hash):
    source = ROOT / 'data/external/target_tissue_summary.csv'
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected_hash:
        raise ValueError('Tissue summary checksum mismatch')
    tissue = pd.read_csv(source).set_index('human_ensembl_id')
    if not tissue.index.is_unique:
        raise ValueError('Tissue summary contains duplicate human gene IDs')
    return tissue


def filter_components(frame, tissue, sort_column, minimum, require_liver, search):
    table = frame[frame[sort_column].notna()].sort_values(sort_column)
    before = len(table)
    if minimum > 0:
        table = table[table['T'].ge(minimum)]
    tractability_excluded = before - len(table)
    before = len(table)
    if require_liver:
        table = table[table.human_ensembl_id.map(tissue.liver_ntpm).notna()]
    tissue_excluded = before - len(table)
    if search:
        columns = ['symbol', 'human_symbol', 'feature_id', 'human_ensembl_id']
        mask = table[columns].fillna('').apply(
            lambda col: col.str.contains(search, case=False, regex=False)).any(axis=1)
        table = table[mask]
    return table, tractability_excluded, tissue_excluded
