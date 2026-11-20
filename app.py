"""Read-only interface for the checked target-ranking exports."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/02-120-matplotlib')
from base64 import b64encode
import json
from html import escape
from io import BytesIO
from urllib.parse import urlencode

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from app_data import ROOT, annotation_rows, load_mouse, read_packaged_map, read_profile, spot_rows, verify_exports
from app_tables import VIEWS, filter_components, load_components, load_tissue_review_data

st.set_page_config(page_title='Spatial target evidence', layout='wide')


components = st.cache_data(load_components)
tissue_review_data = st.cache_data(load_tissue_review_data)
HTTP_EXPORTS = os.environ.get('SPATIAL_HTTP_EXPORTS') == '1'


def download(label, filename, content_type, data, route, **query):
    if HTTP_EXPORTS:
        url = f'/exports/{route}'
        if query:
            url = f'{url}?{urlencode(query)}'
        st.html(f'<a href="{escape(url)}" download="{escape(filename)}">{escape(label)}</a>')
    else:
        st.download_button(label, data(), filename, content_type)


@st.cache_data
def reviewed_compounds():
    return pd.read_csv(ROOT / 'results/compound_activity/reviewed_compounds.csv',
                       keep_default_na=False)


profile_for = st.cache_data(max_entries=16)(read_profile)
packaged_map = st.cache_data(max_entries=18)(read_packaged_map)
mouse_data = st.cache_resource(max_entries=2)(load_mouse)
checked_manifest = st.cache_data(verify_exports)


def main():
    st.title('Spatial target evidence')
    st.write('Explore ranked human-target hypotheses from mouse acute liver injury.')
    st.warning('Hypotheses for follow-up. Expression does not establish causality, treatment direction, efficacy, or safety.')
    try:
        frame = components()
        manifest = checked_manifest()
        tissue = tissue_review_data(manifest['input_sha256']['data/external/target_tissue_summary.csv'])
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
    view = st.radio('Evidence view', list(VIEWS), horizontal=True)
    search = st.text_input('Find mouse/human symbol or stable ID', max_chars=500, help='Case-insensitive literal lookup; switch to all features to find excluded targets.')
    with st.expander('Optional review filters'):
        minimum = st.select_slider('Minimum small-molecule tractability score',
                                   [0.0, 0.3, 0.6, 0.8, 1.0], value=0.0)
        require_liver = st.checkbox('Require a measured normal-human liver RNA value')
        table, tractability_excluded, tissue_excluded = filter_components(
            frame, tissue, VIEWS[view], minimum, require_liver, search)
        st.caption(f'{tractability_excluded:,} excluded by the tractability filter.')
        st.caption(f'{tissue_excluded:,} additionally excluded by the liver RNA coverage filter.')
        st.caption('Filters apply in order before search. Clear both controls to restore the full view.')
    columns = ['priority_rank', 'spatial_rank', 'symbol', 'feature_id', 'human_symbol', 'S', 'T', 'D', 'priority', 'reproducibly_positive', 'exclusion_reasons']
    st.caption(f'{len(table):,} matching features. Blank numeric cells mean unavailable, not zero. Ranks remain those of the full saved export. Weights and source versions appear above.')
    st.dataframe(table[columns].head(250), hide_index=True)
    download('Download matching evidence table (CSV)', 'target_evidence.csv', 'text/csv',
             lambda: table.to_csv(index=False), 'ranking',
             view=VIEWS[view], minimum=minimum, liver=require_liver, search=search)
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
    st.caption('24 h: necrotic-region context only.' if time == 24 else '48/72 h: collagen-linked annotated region; the smaller contrast of the two mice determines the contribution at this time.')
    st.dataframe(selected[['mouse', 'annotation_context', 'difference', 'annotated_mean', 'other_mean', 'annotated_detection', 'other_detection', 'annotated_n', 'other_n', 'status']], hide_index=True)
    st.caption('n columns are retained spot counts, not biological replicates. Each row represents one mouse. Difference = annotated mean − other mean.')
    mouse = st.selectbox('Mouse', selected.mouse.tolist())
    mode = st.radio('Map layer', ['Annotations', 'Selected target expression'], horizontal=True)
    saved = None
    if mode == 'Selected target expression':
        try:
            saved = packaged_map(mouse, feature_id)
            if saved is not None:
                points = pd.read_csv(BytesIO(saved))
            else:
                try:
                    with st.spinner('Loading this mouse’s full sparse archive…'):
                        points = pd.DataFrame(spot_rows(mouse_data(mouse), feature_id))
                except FileNotFoundError:
                    mode = 'Annotations'
                    st.info('Expression maps are packaged for CD74, LGALS3, and CTSS. Other targets require the local source archive. Showing annotations.')
        except (OSError, ValueError) as error:
            st.error(f'Expression map unavailable: {error}. See DATA_PROVENANCE.md.')
            mode = 'Annotations'
            st.info('Showing annotations while expression is unavailable.')
    if mode == 'Annotations':
        points = pd.DataFrame(annotation_rows(mouse))
    fig, ax = plt.subplots(figsize=(8, 6))
    if mode == 'Annotations':
        for flag, color, label in [(False, '#b9c5ce', 'Other'), (True, '#d77731', 'Annotated')]:
            group = points[points.annotated == flag]
            ax.scatter(group.x, group.y, s=7, color=color, label=label)
        ax.legend()
    else:
        valid = points.expression.notna()
        maximum = points.loc[valid, 'expression'].max() if valid.any() else 0
        upper = maximum if maximum > 0 else 1
        scatter = ax.scatter(points.loc[valid, 'x'], points.loc[valid, 'y'],
                             c=points.loc[valid, 'expression'], s=7, cmap='viridis',
                             vmin=0, vmax=upper)
        fig.colorbar(scatter, ax=ax, label='ln(1 + 10,000 × count / all-feature library)')
        missing = points[~valid]
        if len(missing):
            ax.scatter(missing.x, missing.y, color='gray', marker='x', label='Missing (zero library)')
            ax.legend()
        st.caption(f'{valid.sum():,} measured spots; {(~valid).sum():,} missing. Measured zeros use the zero color. The color scale runs from 0 to {upper:.3g} for this mouse and target.')
    ax.set_aspect('equal', adjustable='box')
    ax.invert_yaxis()
    ax.set(xlabel='Visium x', ylabel='Visium y', title=f'{mouse} · {mode}')
    if HTTP_EXPORTS:
        image = BytesIO()
        fig.savefig(image, format='png', dpi=150, bbox_inches='tight')
        st.image('data:image/png;base64,' + b64encode(image.getvalue()).decode('ascii'),
                 width='stretch')
    else:
        st.pyplot(fig)
    plt.close(fig)
    expression_mode = mode == 'Selected target expression'
    download('Download displayed map data (full barcodes)', f'{mouse}_{feature_id}_spots.csv',
             'text/csv', lambda: saved if expression_mode and saved is not None else points.to_csv(index=False),
             'map', mouse=mouse, feature_id=feature_id, expression=expression_mode)

    st.subheader('Human tissue and reported liabilities')
    st.write('Liability evidence:', profile['liability_status'])
    st.caption('“None reported in collected sources” and missing records do not establish safety. Normal-human tissue expression is context, not a toxicity prediction.')
    st.caption('RNA is reported in normalized transcripts per million (nTPM). Protein is summarized from immunohistochemistry with HPA reliability categories.')
    st.json(profile['tissue_summary'] or {'status': 'unavailable'})
    with st.expander('Reported liability records and references'):
        st.json(profile['reported_liabilities'])
    with st.expander('Known drug mechanisms, indications, and clinical records'):
        st.caption('Target-level tractability does not mean a drug is approved for liver injury or that inhibition helps recovery. Empty rows mean no records in this snapshot.')
        candidates = profile['drug_and_clinical_candidates']['rows']
        if not candidates:
            st.write('No drug records in this snapshot.')
        for candidate in candidates:
            drug = candidate['drug']
            st.markdown(f"**{drug['name']}** · {drug['id']}")
            st.write('Overall clinical stage in snapshot', drug['maximumClinicalStage'])
            st.json({'mechanisms': drug['mechanismsOfAction']['rows'],
                     'listed_indications': candidate['diseases'],
                     'individual_clinical_records': candidate['clinicalReports']})
    st.subheader('Reviewed compound and intervention evidence')
    try:
        compounds = reviewed_compounds()
    except (OSError, ValueError) as error:
        st.error(f'Compound evidence unavailable: {error}')
    else:
        selected_compounds = compounds[compounds.target == row.human_symbol]
        if selected_compounds.empty:
            st.info('No curated compound evidence for this target. Intervention direction is unknown.')
        for entry in selected_compounds.to_dict('records'):
            st.markdown(f"**{entry['compound']}** · {entry['compound_id']}")
            st.caption(f"Evidence review {entry['review_version']} · {entry['snapshot_source']}")
            st.write('Target direction for acute APAP follow-up', entry['target_direction'])
            st.write(entry['target_experiment'])
            st.write(entry['counter_evidence'])
            st.write('Compound action', entry['compound_action'])
            st.write('Published assay or study', entry['activity_type'])
            if entry['activity_value'] != '':
                st.write('Measured value', f"{entry['activity_value']} {entry['activity_unit']}")
            for field in ('liver_evidence', 'selectivity', 'liabilities', 'decision'):
                st.write(entry[field])
            for i, link in enumerate((entry['target_sources'] + ' | ' + entry['compound_sources']).split(' | '), 1):
                st.link_button(f"{entry['compound']} study {i}", link)
        download('Download reviewed compound evidence (CSV)', 'reviewed_compounds.csv',
                 'text/csv', (ROOT / 'results/compound_activity/reviewed_compounds.csv').read_bytes,
                 'compounds')
    with st.expander('Disease evidence and tractability records'):
        st.json({'disease': profile['disease_evidence'], 'tractability': profile['tractability']})
    for i, link in enumerate(profile['source_links'], 1):
        st.link_button(f'Target source {i}', link)
    download('Download complete selected evidence profile (JSON)', f'{feature_id}_evidence.json',
             'application/json', lambda: json.dumps(profile, indent=2),
             'profile', feature_id=feature_id)


if __name__ == '__main__':
    main()
