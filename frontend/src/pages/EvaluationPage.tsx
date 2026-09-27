import React, { useEffect, useState } from 'react';
interface Metrics { sample_count: number; exact_match_pct: number; macro_token_f1: number; mean_latency_ms: number; failed_samples: number }
interface Report { status: string; timestamp?: string; benchmark?: string; device?: string; dtype?: string; baseline?: Metrics; adapted?: Metrics; limitations?: string[]; latency_scope?: string; settings?: Record<string, unknown> }
export const EvaluationPage: React.FC = () => {
  const [report, setReport] = useState<Report | null>(null);
  const [readiness, setReadiness] = useState<Record<string, { status: string; sample_count?: number | null }>>({});
  const [error, setError] = useState('');
  const downloadSummary = () => {
    const payload = JSON.stringify({ generated_at: new Date().toISOString(), readiness, report }, null, 2);
    const url = URL.createObjectURL(new Blob([payload], { type: 'application/json' }));
    const link = document.createElement('a'); link.href = url; link.download = 'satquery-evaluation-summary.json'; link.click(); URL.revokeObjectURL(url);
  };
  useEffect(() => {
    const controller = new AbortController();
    fetch('/api/evaluation', { signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error('Evaluation report could not be loaded.');
      setReport(await response.json());
    }).catch(e => { if (e.name !== 'AbortError') setError(e.message); });
    fetch('/api/benchmarks/readiness', { signal: controller.signal }).then(async response => {
      if (response.ok) setReadiness(await response.json());
    }).catch(() => undefined);
    return () => controller.abort();
  }, []);
  return <div className="evaluation-page-container">
    <div className="evaluation-header"><div><h2 className="page-title">Measured evaluation results</h2><p>Benchmark measurements and dataset readiness for the judging workflow.</p></div><button type="button" className="btn-secondary" onClick={downloadSummary}>Download evaluation summary</button></div>
    <p>Controlled baseline and adapter comparison from the completed backend report.</p>
    {error && <p role="alert">{error}</p>}
    <section className="benchmark-readiness-strip" aria-label="Benchmark readiness">
      {['CDVQA', 'SEN1-2', 'ISRO/SAC'].map(name => {
        const item = readiness[name];
        const status = item?.status || 'CHECKING';
        return <div className="benchmark-readiness-card" key={name}><div><strong>{name}</strong><span>{item?.sample_count != null ? `${item.sample_count} samples` : 'Prescribed input'}</span></div><b className={`readiness-${status.toLowerCase()}`}>{status.replace('_', ' ')}</b></div>;
      })}
    </section>
    {!report && !error && <p>Loading report...</p>}
    {report && report.status !== 'COMPLETED' && <p>No completed controlled evaluation is available yet.</p>}
    {report?.status === 'COMPLETED' && <>
      <p>{report.benchmark} | {report.timestamp} | {report.device} / {report.dtype}</p>
      <table className="geospatial-table"><thead><tr><th>Variant</th><th>Samples</th><th>Exact match</th><th>Token F1</th><th>Failures</th><th>Mean generation time</th></tr></thead>
      <tbody>{(['baseline', 'adapted'] as const).map(name => {
        const m = report[name];
        return m ? <tr key={name}><td>{name}</td><td>{m.sample_count}</td><td>{m.exact_match_pct}%</td><td>{m.macro_token_f1}</td><td>{m.failed_samples}</td><td>{(m.mean_latency_ms / 1000).toFixed(2)}s</td></tr> : null;
      })}</tbody></table>
      <p>{report.latency_scope}</p>
      <p>Settings: {JSON.stringify(report.settings)}</p>
      <ul>{report.limitations?.map(item => <li key={item}>{item}</li>)}</ul>
    </>}
  </div>;
};
