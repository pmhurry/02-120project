import {useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import Papa from 'papaparse';
import Predictions from './Predictions.jsx';
import ProjectGuide from './ProjectGuide.jsx';
import './style.css';

const query = (values) => new URLSearchParams(values).toString();
const timePoints = [24, 48, 72];
const number = (value, digits = 2) =>
  value === '' || value == null ? '—' : Number(value).toLocaleString('en-US', {maximumFractionDigits: digits});
const mouseName = (mouse) => mouse?.split('_').at(-1).toUpperCase();
const viewLabels = {
  priority_rank: 'Complete-evidence ranking',
  spatial_rank: 'Spatial-only screen',
  feature_id: 'All features / mapping audit',
};

async function get(url, signal, csv) {
  const response = await fetch(url, {signal});
  if (!response.ok) throw new Error(response.status === 404 ? 'Evidence is unavailable for this selection.' : 'Could not load the saved evidence.');
  if (!csv) return response.json();
  const parsed = Papa.parse(await response.text(), {header: true, skipEmptyLines: true});
  if (parsed.errors.length) throw new Error('Could not read the evidence table.');
  return parsed.data;
}

function useEvidence(url, csv = false) {
  const [state, setState] = useState({});
  useEffect(() => {
    if (!url) return;
    const controller = new AbortController();
    get(url, controller.signal, csv)
      .then(data => setState({url, data}))
      .catch(error => {
        if (!controller.signal.aborted) setState({url, error: error.message});
      });
    return () => controller.abort();
  }, [url, csv]);
  return state.url === url ? state : {};
}

function SpatialPlot({rows, expression, loading, error, mouse}) {
  const canvas = useRef(null);
  const measured = expression ? rows.filter(row => row.expression !== '' && Number.isFinite(Number(row.expression))) : [];
  const maximum = measured.reduce((max, row) => Math.max(max, Number(row.expression)), 0);

  useEffect(() => {
    if (!canvas.current || !rows.length) return;
    const context = canvas.current.getContext('2d');
    context.clearRect(0, 0, 720, 400);
    const x = rows.map(row => Number(row.x));
    const y = rows.map(row => Number(row.y));
    const minX = Math.min(...x), maxX = Math.max(...x);
    const minY = Math.min(...y), maxY = Math.max(...y);
    const scale = Math.min(660 / (maxX - minX || 1), 348 / (maxY - minY || 1));
    const left = (720 - (maxX - minX) * scale) / 2;
    const top = (400 - (maxY - minY) * scale) / 2;
    rows.forEach((row, index) => {
      const fraction = Math.max(0, Math.min(1, Number(row.expression) / (maximum || 1)));
      if (!expression) context.fillStyle = row.annotated === 'True' ? '#ed804b' : '#b4bed5';
      else if (row.expression === '') context.fillStyle = '#9297a6';
      else {
        const [low, high] = fraction < .5 ? [[219, 225, 248], [120, 110, 220]] : [[120, 110, 220], [52, 26, 126]];
        const offset = fraction < .5 ? 2 * fraction : 2 * fraction - 1;
        context.fillStyle = `rgb(${low.map((channel, i) => Math.round(channel + (high[i] - channel) * offset)).join(',')})`;
      }
      context.beginPath();
      context.arc(left + (x[index] - minX) * scale, top + (y[index] - minY) * scale, 2.45, 0, 2 * Math.PI);
      context.fill();
    });
  }, [rows, expression, maximum]);

  return <>
    <div className="plot">
      {rows.length > 0
        ? <canvas ref={canvas} width="720" height="400" role="img" aria-label={`${expression ? 'Gene expression' : 'Region annotations'} for ${mouseName(mouse)}, ${rows.length} spots`} />
        : <p className="status" role="status">{error || (loading ? 'Loading spatial spots…' : 'Select a mouse to see its map.')}</p>}
    </div>
    {rows.length > 0 && <div className="legend">
      {expression
        ? <><span>Normalized expression</span><span>0</span><span className="gradient"/><span>{number(maximum)}</span><span>{rows.length - measured.length} missing</span></>
        : <><span><i className="dot annotated"/> Annotated region</span><span><i className="dot other"/> Other region</span><span className="spot-total">{number(rows.length, 0)} spots</span></>}
    </div>}
  </>;
}

function Score({row}) {
  return <section className="card score-card">
    <h2>Score breakdown</h2>
    <div className="score-grid">
      {[['Spatial contrast', row.S, '60%'], ['Tractability', row.T, '25%'], ['Disease association', row.D, '15%']].map(([label, value, weight]) =>
        <div className="metric" key={label}>
          <span>{label}</span><strong>{number(value, 3)}</strong>
          <div className="track" aria-hidden="true"><i style={{width: `${Math.max(0, Math.min(1, value ?? 0)) * 100}%`}}/></div>
          <small>{weight} of priority score</small>
        </div>)}
    </div>
    <p className="muted">Priority combines 48 h and 72 h mouse contrasts with small-molecule tractability and hepatic fibrosis association. A missing component prevents a complete rank.</p>
    {row.exclusion_reasons && <p className="notice">Ranking exclusion · {row.exclusion_reasons}</p>}
    {row.annotation_linked_marker === 'True' && <p className="notice">This collagen-linked marker helped define the annotated region. Its enrichment does not independently validate that region.</p>}
  </section>;
}

function Evidence({entries, error}) {
  return <section className="card evidence-card">
    <div className="card-title"><h2>Compound evidence</h2><a href="/exports/compounds">Download CSV</a></div>
    {error && <p className="notice" role="status">{error}</p>}
    {!error && (entries?.length ? entries.map(entry => <article key={entry.compound_id}>
      <div className="card-title"><h3>{entry.compound}</h3><span className="soft-label">{entry.modality}</span></div>
      <p className="muted">{entry.compound_id} · {entry.snapshot_source}</p>
      <dl className="details">
        <dt>Target direction</dt><dd>{entry.target_direction}</dd>
        <dt>Compound action</dt><dd>{entry.compound_action}</dd>
        <dt>Published experiment</dt><dd>{entry.activity_type}{entry.activity_value && ` · ${entry.activity_value} ${entry.activity_unit}`}</dd>
        <dt>Supporting findings</dt><dd>{entry.target_experiment}</dd>
        <dt>Counter-evidence</dt><dd>{entry.counter_evidence}</dd>
        <dt>Liver evidence</dt><dd>{entry.liver_evidence}</dd>
        <dt>Selectivity</dt><dd>{entry.selectivity}</dd>
        <dt>Reported liabilities</dt><dd>{entry.liabilities}</dd>
        <dt>Follow-up decision</dt><dd>{entry.decision}</dd>
      </dl>
      <div className="source-links">
        {[...new Set(`${entry.target_sources} | ${entry.compound_sources}`.split(' | '))].filter(Boolean).map((url, index) =>
          <a key={url} href={url} target="_blank" rel="noreferrer">Study {index + 1}</a>)}
      </div>
    </article>) : <p className="muted">{entries ? 'Intervention direction is unknown in the reviewed evidence.' : 'Loading compound evidence…'}</p>)}
  </section>;
}

function Tissue({profile}) {
  const tissue = profile.tissue_summary;
  return <section className="card evidence-card">
    <h2>Normal-human tissue and liabilities</h2>
    {tissue ? <dl className="details">
      <dt>Liver RNA</dt><dd>{number(tissue.liver_ntpm, 1)} nTPM</dd>
      <dt>Highest non-liver RNA</dt><dd>{number(tissue.max_non_liver_ntpm, 1)} nTPM · {tissue.max_non_liver_tissues || 'Tissue unavailable'}</dd>
      <dt>Protein coverage</dt><dd>{tissue.protein_coverage || 'Unavailable'}{tissue.protein_rows_measured && ` · ${tissue.protein_rows_measured} measured records`}</dd>
      <dt>Protein reliability counts</dt><dd>{tissue.protein_reliability_counts || 'Unavailable'}</dd>
      <dt>Reported liabilities</dt><dd>{profile.liability_status}</dd>
    </dl> : <p className="muted">Normal-human tissue measurements are unavailable for this target.</p>}
    <p className="muted">RNA is measured in normalized transcripts per million. Tissue expression and absent liability reports do not establish safety.</p>
    {profile.reported_liabilities?.length > 0 && <details><summary>Reported liability records</summary><pre>{JSON.stringify(profile.reported_liabilities, null, 2)}</pre></details>}
    <div className="source-links">{profile.source_links.map(url => <a key={url} href={url} target="_blank" rel="noreferrer">{new URL(url).hostname}</a>)}</div>
  </section>;
}

function Profile({row}) {
  const [tab, setTab] = useState('Spatial');
  const [time, setTime] = useState(48);
  const [mouseChoice, setMouse] = useState(null);
  const [layer, setLayer] = useState('annotation');
  const profileUrl = '/exports/profile?' + query({feature_id: row.feature_id});
  const {data: profile, error: profileError} = useEvidence(profileUrl);
  const pairs = profile?.mouse_evidence.filter(item => Number(item.time_hours) === time) ?? [];
  const mouse = pairs.some(item => item.mouse === mouseChoice) ? mouseChoice : pairs[0]?.mouse;
  const expression = layer === 'expression';
  const mapArgs = {feature_id: row.feature_id, mouse, expression};
  const mapUrl = mouse ? '/exports/map?' + query(mapArgs) : null;
  const {data: spots, error: mapError} = useEvidence(tab === 'Spatial' ? mapUrl : null, true);
  const {data: compounds, error: compoundError} = useEvidence(tab === 'Compounds' ? '/exports/compounds' : null, true);

  return <section className="profile" aria-label="Selected target">
    <div className="profile-heading">
      <div><span className="eyebrow">Target profile</span><h1>{row.symbol}</h1>
        <p>{row.human_symbol ? `Human ortholog · ${row.human_symbol}` : 'Human mapping unavailable'} <span>· {row.feature_id}</span></p>
      </div>
      <div className="priority"><span>Priority score</span><strong>{number(row.priority)}</strong><small>{row.priority_rank ? `Rank #${row.priority_rank}` : 'Unranked'}</small></div>
    </div>
    {profileError && <p className="notice" role="status">{profileError}</p>}
    <div className="tabs" aria-label="Evidence sections">
      {['Spatial', 'Compounds', 'Tissue & liabilities'].map(name =>
        <button key={name} aria-pressed={tab === name} onClick={() => setTab(name)}>{name}</button>)}
      <a className="profile-export" href={profileUrl}>Profile JSON</a>
    </div>
    {tab === 'Spatial' && <>
      <section className="card map-card">
        <div className="card-title"><div><h2>Spatial evidence</h2><p className="muted">Acetaminophen-induced liver injury · mouse Visium</p></div>
          {mapUrl && spots && <a href={mapUrl}>Download spots</a>}
        </div>
        <div className="map-controls">
          <div className="segmented" aria-label="Time since injury">{timePoints.map(value =>
            <button key={value} aria-pressed={time === value} onClick={() => setTime(value)}>{value} h</button>)}</div>
          <label className="mouse-select">Mouse <select value={mouse ?? ''} onChange={event => setMouse(event.target.value)} disabled={!pairs.length}>
            {!pairs.length && <option value="">—</option>}
            {pairs.map(item => <option key={item.mouse} value={item.mouse}>{mouseName(item.mouse)}</option>)}</select></label>
          <div className="segmented layers" aria-label="Map layer">
            <button aria-pressed={!expression} onClick={() => setLayer('annotation')}>Annotations</button>
            <button aria-pressed={expression} onClick={() => setLayer('expression')}>Expression</button>
          </div>
        </div>
        <SpatialPlot rows={spots ?? []} expression={expression} mouse={mouse} loading={!profileError && !mapError} error={mapError && expression ? 'Hosted expression maps cover Cd74, Lgals3, and Ctss. Switch to Annotations to view all targets.' : mapError} />
        <p className="map-note">{time === 24 ? '24 h shows necrotic-region context. The priority score uses 48 h and 72 h.' : '48 h and 72 h compare collagen-linked annotations with the other region.'} {expression && 'Expression uses log-normalized full-library counts and a map-specific color scale.'}</p>
      </section>
      <Score row={row}/>
      {pairs.length > 0 && <section className="card">
        <h2>Mouse-level contrasts</h2>
        <div className="table-wrap"><table>
          <thead><tr><th>Mouse</th><th>Annotated mean</th><th>Other mean</th><th>Difference</th><th>Spots</th></tr></thead>
          <tbody>{pairs.map(item => <tr key={item.mouse}>
            <td>{mouseName(item.mouse)}</td><td>{number(item.annotated_mean, 3)}</td><td>{number(item.other_mean, 3)}</td>
            <td>{number(item.difference, 3)}</td><td>{number(Number(item.annotated_n) + Number(item.other_n), 0)}</td>
          </tr>)}</tbody>
        </table></div>
        <p className="muted">Each row is an independent mouse. Spots contribute to the within-mouse contrast.</p>
      </section>}
    </>}
    {tab === 'Compounds' && <Evidence entries={compounds?.filter(entry => entry.target === row.human_symbol)} error={compoundError}/>}
    {tab === 'Tissue & liabilities' && (profile ? <Tissue profile={profile}/> : <p role="status">{profileError || 'Loading tissue evidence…'}</p>)}
  </section>;
}

function Explorer() {
  const [view, setView] = useState('priority_rank');
  const [search, setSearch] = useState('');
  const [min, setMin] = useState('0');
  const [liver, setLiver] = useState(false);
  const [offset, setOffset] = useState(0);
  const [selected, setSelected] = useState(null);
  const params = query({view, search, minimum: min, liver});
  const {data, error} = useEvidence(`/api/preview/ranking?${params}&offset=${offset}`);
  const row = data?.rows.find(item => item.feature_id === selected) ?? data?.rows[0];
  const change = (setter, value) => {setter(value); setOffset(0);};
  const rankLabel = view === 'spatial_rank' ? 'Spatial rank' : 'Rank';
  return <>
    <main className="workspace">
      <aside className="card explorer">
        <div className="explorer-heading"><h2>Target explorer</h2><a href={`/exports/ranking?${params}`}>CSV</a></div>
        <label className="control">Find a target<input type="search" placeholder="Gene symbol or stable ID" value={search} maxLength={500} onChange={event => change(setSearch, event.target.value)}/></label>
        <label className="control">Evidence view<select value={view} onChange={event => change(setView, event.target.value)}>
          {Object.entries(viewLabels).map(([value, label]) => <option value={value} key={value}>{label}</option>)}
        </select></label>
        <details className="filters"><summary>Review filters</summary>
          <label className="control">Minimum tractability<select value={min} onChange={event => change(setMin, event.target.value)}>
            {['0', '.3', '.6', '.8', '1'].map(value => <option value={value} key={value}>{Number(value).toFixed(1)}</option>)}
          </select></label>
          <label className="check"><input type="checkbox" checked={liver} onChange={event => change(setLiver, event.target.checked)}/> Require measured liver RNA</label>
          {data && <p className="muted">{number(data.excluded_tractability, 0)} excluded by tractability · {number(data.excluded_tissue, 0)} by tissue coverage</p>}
        </details>
        <p className="results-count" role="status">{error || (data ? `${number(data.total, 0)} matching features` : 'Loading targets…')}</p>
        {data?.rows.length > 0 && <>
          <div className="rank-grid rank-head"><span>{rankLabel}</span><span>Target</span><span>Priority</span></div>
          <div className="rank-list">
            {data.rows.map(item => <button className="rank-grid rank-row" key={item.feature_id} aria-pressed={item.feature_id === row.feature_id} onClick={() => setSelected(item.feature_id)}>
              <span className="rank-index">{number(view === 'spatial_rank' ? item.spatial_rank : item.priority_rank, 0)}</span>
              <span><strong>{item.symbol}</strong><small>{item.human_symbol || item.feature_id}</small></span>
              <span className="rank-value">{number(item.priority)}</span>
            </button>)}
          </div>
          <div className="pagination"><button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 25))}>Previous</button>
            <span>{offset + 1}–{offset + data.rows.length}</span>
            <button disabled={offset + data.rows.length >= data.total} onClick={() => setOffset(offset + 25)}>Next</button></div>
        </>}
      </aside>
      {row ? <Profile key={row.feature_id} row={row}/>
        : <section className="card empty" role="status">{error || (data ? 'No targets match these filters.' : 'Preparing the target explorer…')}</section>}
    </main>
    <footer>Exploratory target hypotheses · 2 mice per time point · No uninjured controls</footer>
  </>;
}

function PredictionView() {
  const {data, error} = useEvidence('/assets/heldout_evaluation.json');
  return <Predictions report={data} error={error}/>;
}

function App() {
  const view = new URLSearchParams(window.location.search).get('view');
  const showGuide = view === 'guide';
  const showPredictions = view === 'predictions';
  return <>
    <header className="topbar">
      <a className="brand" href="/"><span className="mark" aria-hidden="true">✳</span><span>Spatial Target Evidence</span></a>
      <nav className="top-links" aria-label="Main navigation">
        <a href="/" aria-current={!showGuide && !showPredictions ? 'page' : undefined}>Explorer</a>
        <a href="/?view=guide" aria-current={showGuide ? 'page' : undefined}>Project guide</a>
        <a href="/?view=predictions" aria-current={showPredictions ? 'page' : undefined}>Predictions</a>
      </nav>
    </header>
    {showGuide ? <ProjectGuide/> : showPredictions ? <PredictionView/> : <Explorer/>}
  </>;
}

createRoot(document.getElementById('root')).render(<App/>);
