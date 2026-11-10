"""Local, read-only interface for the checked target-ranking exports."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/02-120-matplotlib')
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from app_data import ROOT, RANKING, load_mouse, read_components, read_profile, spot_rows, verify_exports
from data_loader import load_metadata

st.set_page_config(page_title='Spatial target evidence', layout='wide')


@st.cache_data
def components():
    frame = pd.DataFrame(read_components()).replace('', None)
    numeric = ['S', 'S_48', 'S_72', 'T', 'D', 'priority', 'priority_rank', 'spatial_rank',
               'rank_spatial_heavy', 'rank_equal_components', 'rank_48h', 'rank_72h']
    for column in numeric:
        frame[column] = pd.to_numeric(frame[column], errors='coerce')
    return frame


profile_for = st.cache_data(max_entries=16)(read_profile)
mouse_data = st.cache_resource(max_entries=2)(load_mouse)
checked_manifest = st.cache_data(verify_exports)


def main():
    st.title('Spatial target evidence')
    st.write('Explore ranked human-target hypotheses from mouse acute liver injury.')
    st.warning('Hypotheses for follow-up. Expression does not establish causality, treatment direction, efficacy, or safety.')
    try:
        frame = components()
        manifest = checked_manifest()
    except (OSError, ValueError) as error:
        st.error(f'Cannot read saved ranking: {error}. Run python3 inspect_ranking.py first.')
        st.stop()
    st.caption(f"Disease evidence: {manifest['disease_name']} ({manifest['disease_id']}); chronic-fibrosis context for an acute-injury experiment.")
    st.caption('Ranks combine 48 and 72 h. 24 h is separate necrotic-region context. Two independent mice per time; no uninjured controls.')
    a, b, c = st.columns(3)
    a.metric('Features screened', f'{len(frame):,}')
    b.metric('Complete-evidence targets', f'{frame.priority_rank.notna().sum():,}')
    c.metric('Spatial component available', f'{frame.S.notna().sum():,}')
    with st.expander('How the score works · weights and source versions'):
        st.write('S: at each later time, use the smaller mouse difference, truncate below zero, transform x/(1+x), then average 48 and 72 h equally. T: fixed small-molecule tractability tier. D: selected-disease association score.')
        st.code('Priority = 100 × (0.60 × S + 0.25 × T + 0.15 × D)')
        st.write('No weight renormalization. Missing components prevent complete ranking. Mapping requires a high-confidence one-to-one stable-ID match; reproducible enrichment requires both mice positive at one later time. Ties use stable feature ID. Tissue expression and liabilities never enter the score.')
        st.json({'version': manifest['version'], 'weights': manifest['weights'], 'sources': manifest['source_versions']})

    st.subheader('Target ranking and lookup')
    view = st.radio('Evidence view', ['Complete-evidence ranking', 'Spatial-only screen', 'All features / mapping audit'], horizontal=True)
    search = st.text_input('Find mouse/human symbol or stable ID', help='Case-insensitive literal lookup; switch to all features to find excluded targets.')
    if view == 'Complete-evidence ranking':
        table = frame[frame.priority_rank.notna()].sort_values('priority_rank')
    elif view == 'Spatial-only screen':
        table = frame[frame.spatial_rank.notna()].sort_values('spatial_rank')
    else:
        table = frame.sort_values('feature_id')
    if search:
        mask = table[['symbol', 'human_symbol', 'feature_id', 'human_ensembl_id']].fillna('').apply(
            lambda col: col.str.contains(search, case=False, regex=False)).any(axis=1)
        table = table[mask]
    columns = ['priority_rank', 'spatial_rank', 'symbol', 'feature_id', 'human_symbol', 'S', 'T', 'D', 'priority', 'exclusion_reasons']
    st.caption(f'{len(table):,} matching features. Blank numeric cells mean unavailable, not zero. Ranks remain those of the full saved export.')
    st.dataframe(table[columns].head(250), hide_index=True)
    st.download_button('Download matching evidence table (CSV)', table.to_csv(index=False), 'target_evidence.csv', 'text/csv')
    if table.empty:
        st.info('No matches in this view. Try all features or another symbol/ID.')
        return
    labels = {r.feature_id: f'{r.symbol} · {r.feature_id} · {r.human_symbol or "human mapping unavailable"}' for r in table.itertuples()}
    feature_id = st.selectbox('Target evidence profile', list(labels), format_func=labels.get)
    row = frame.set_index('feature_id').loc[feature_id]
    profile = profile_for(feature_id)
    st.subheader(f'{row.symbol} · target evidence')
    st.dataframe(pd.DataFrame([row[['S', 'S_48', 'S_72', 'T', 'D', 'priority', 'priority_rank', 'spatial_rank', 'rank_spatial_heavy', 'rank_equal_components', 'rank_48h', 'rank_72h']]]), hide_index=True)
    st.write('Mapping:', row.human_ensembl_id or 'unavailable', '·', row.mapping_method or 'unavailable')
    st.write('Exclusion reasons:', row.exclusion_reasons or 'none')
    if row.annotation_linked_marker == 'True':
        st.info('Annotation-linked collagen marker: enrichment is not independent validation of the region annotation.')

    st.subheader('Mouse and spatial evidence')
    time = st.selectbox('Spatial time (hours)', [48, 72, 24])
    evidence = pd.DataFrame(profile['mouse_evidence'])
    selected = evidence[evidence.time_hours.astype(int) == time]
    st.caption('24 h: necrotic-region context only.' if time == 24 else '48/72 h: collagen-linked annotated region; both mice contribute equally to S.')
    st.dataframe(selected[['mouse', 'annotation_context', 'difference', 'annotated_mean', 'other_mean', 'annotated_detection', 'other_detection', 'annotated_n', 'other_n', 'status']], hide_index=True)
    st.caption('n columns are retained spot counts, not biological replicates. Each row represents one mouse. Difference = annotated mean − other mean.')
    mouse = st.selectbox('Mouse', selected.mouse.tolist())
    mode = st.radio('Map layer', ['Annotations', 'Selected target expression'], horizontal=True)
    if mode == 'Annotations':
        spots = [s for s in load_metadata(ROOT / 'Visium_Meta_data.txt').values() if s.mouse == mouse]
        points = pd.DataFrame([dict(barcode=s.barcode, x=s.x, y=s.y, annotated=s.fibrogenic) for s in spots])
    else:
        try:
            with st.spinner('Loading and checksum-checking this mouse’s full sparse archive…'):
                points = pd.DataFrame(spot_rows(mouse_data(mouse), feature_id))
        except (OSError, ValueError) as error:
            st.error(f'Expression map unavailable: {error}. Restore the matching archive in data/source; see DATA_PROVENANCE.md.')
            mode = 'Annotations'
            spots = [s for s in load_metadata(ROOT / 'Visium_Meta_data.txt').values() if s.mouse == mouse]
            points = pd.DataFrame([dict(barcode=s.barcode, x=s.x, y=s.y, annotated=s.fibrogenic) for s in spots])
            st.info('Showing annotations while expression is unavailable.')
    fig, ax = plt.subplots(figsize=(8, 6))
    if mode == 'Annotations':
        for flag, color, label in [(False, '#b9c5ce', 'Other'), (True, '#d77731', 'Annotated')]:
            group = points[points.annotated == flag]
            ax.scatter(group.x, group.y, s=7, color=color, label=label)
        ax.legend()
    else:
        valid = points.expression.notna()
        scatter = ax.scatter(points.loc[valid, 'x'], points.loc[valid, 'y'], c=points.loc[valid, 'expression'], s=7, cmap='viridis', vmin=0)
        fig.colorbar(scatter, ax=ax, label='ln(1 + 10,000 × count / all-feature library)')
        missing = points[~valid]
        if len(missing):
            ax.scatter(missing.x, missing.y, color='gray', marker='x', label='Missing (zero library)')
            ax.legend()
        st.caption(f'{valid.sum():,} measured spots; {(~valid).sum():,} missing. Measured zeros use the zero color. Color scale is specific to this mouse/target.')
    ax.set_aspect('equal', adjustable='box')
    ax.invert_yaxis()
    ax.set(xlabel='Visium x', ylabel='Visium y', title=f'{mouse} · {mode}')
    st.pyplot(fig)
    plt.close(fig)
    st.download_button('Download displayed map data (full barcodes)', points.to_csv(index=False), f'{mouse}_{feature_id}_spots.csv', 'text/csv')

    st.subheader('Human tissue and reported liabilities')
    st.write('Liability evidence:', profile['liability_status'])
    st.caption('“None reported in collected sources” and missing records do not establish safety. Normal-human tissue expression is context, not a toxicity prediction.')
    st.json(profile['tissue_summary'] or {'status': 'unavailable'})
    with st.expander('Reported liability records and references'):
        st.json(profile['reported_liabilities'])
    with st.expander('Known drug mechanisms, indications, and clinical records'):
        st.caption('Target-level tractability does not mean a drug is approved for liver injury or that inhibition helps recovery. Empty rows mean no records in this snapshot.')
        st.json(profile['drug_and_clinical_candidates'])
    with st.expander('Disease evidence and tractability records'):
        st.json({'disease': profile['disease_evidence'], 'tractability': profile['tractability']})
    for i, link in enumerate(profile['source_links'], 1):
        st.link_button(f'Target source {i}', link)
    st.download_button('Download complete selected evidence profile (JSON)', json.dumps(profile, indent=2), f'{feature_id}_evidence.json', 'application/json')


if __name__ == '__main__':
    main()
