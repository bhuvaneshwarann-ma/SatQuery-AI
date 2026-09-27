import React, { useState } from 'react';
import { useHistory, type HistoryEntry } from '../context/HistoryContext';
import { useAnalysis } from '../context/AnalysisContext';
import { useRouter } from '../context/RouterContext';

export const HistoryPage: React.FC = () => {
  const { history, deleteHistoryEntry, clearHistory } = useHistory();
  const { setResultDirectly, setTaskMode, setQuery } = useAnalysis();
  const { navigate } = useRouter();

  const [searchTerm, setSearchTerm] = useState('');
  const [filterTask, setFilterTask] = useState<string>('ALL');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [filterSensor, setFilterSensor] = useState<string>('ALL');
  const [filterDate, setFilterDate] = useState<string>('ALL');

  const sensorFor = (item: HistoryEntry) => {
    const kind = item.result?.metadata?.pair_kind;
    if (kind === 'optical_sar' || item.sarPreview) return 'OPTICAL + SAR';
    if (kind === 'temporal' || item.secondPreview) return 'BI-TEMPORAL';
    return 'SINGLE IMAGE';
  };

  const filtered = history.filter((item) => {
    const matchesSearch =
      searchTerm.trim() === '' ||
      item.query.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.task.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.model.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesTask =
      filterTask === 'ALL' || item.task.toUpperCase() === filterTask.toUpperCase();
    const matchesStatus = filterStatus === 'ALL' || item.status.toUpperCase() === filterStatus;
    const matchesSensor = filterSensor === 'ALL' || sensorFor(item) === filterSensor;
    const ageDays = (Date.now() - new Date(item.timestamp).getTime()) / 86400000;
    const matchesDate = filterDate === 'ALL' || (filterDate === 'TODAY' ? ageDays < 1 : filterDate === '7D' ? ageDays < 7 : ageDays < 30);

    return matchesSearch && matchesTask && matchesStatus && matchesSensor && matchesDate;
  });

  const handleReopen = (item: HistoryEntry) => {
    setResultDirectly(
      item.result,
      {
        primary: item.primaryPreview,
        second: item.secondPreview,
        sar: item.sarPreview,
      },
      item.query
    );
    navigate('/results');
  };

  const handleReanalyze = (item: HistoryEntry, e: React.MouseEvent) => {
    e.stopPropagation();
    setTaskMode(item.task as any);
    setQuery(item.query);
    navigate('/analyze');
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    deleteHistoryEntry(id);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', maxWidth: '1280px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>AUDIT HISTORY</h2>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Locally stored audit records of previous remote sensing queries and uncalibrated assessments.
          </span>
        </div>

        {history.length > 0 && (
          <button
            type="button"
            className="btn-secondary"
            style={{ fontSize: '0.75rem', padding: '4px 10px' }}
            onClick={() => {
              if (window.confirm('Clear all local analysis history?')) clearHistory();
            }}
          >
            Clear Records ({history.length})
          </button>
        )}
      </div>

      {/* Toolbar */}
      <div className="history-toolbar">
        <input
          type="text"
          placeholder="Filter queries, models, or tasks..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ flex: 1, background: 'transparent', border: 'none', color: 'var(--text-primary)', fontSize: '0.84rem', outline: 'none' }}
        />

        <select
          value={filterTask}
          onChange={(e) => setFilterTask(e.target.value)}
          style={{ background: 'var(--surface-secondary)', border: '1px solid var(--border-default)', color: 'var(--text-secondary)', padding: '4px 8px', borderRadius: 'var(--radius-tag)', fontSize: '0.78rem', outline: 'none' }}
        >
          <option value="ALL">All Tasks</option>
          <option value="VQA">VQA</option>
          <option value="GROUNDING">Grounding</option>
          <option value="CHANGE_DETECTION">Change Detection</option>
          <option value="OPTICAL_SAR">Optical-SAR</option>
        </select>
        <select value={filterSensor} onChange={(e) => setFilterSensor(e.target.value)} aria-label="Filter by sensor">
          <option value="ALL">All Sensors</option><option value="SINGLE IMAGE">Single image</option><option value="BI-TEMPORAL">Bi-temporal</option><option value="OPTICAL + SAR">Optical + SAR</option>
        </select>
        <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} aria-label="Filter by status">
          <option value="ALL">All Status</option><option value="SUCCESS">Success</option><option value="ERROR">Error</option>
        </select>
        <select value={filterDate} onChange={(e) => setFilterDate(e.target.value)} aria-label="Filter by date">
          <option value="ALL">Any time</option><option value="TODAY">Today</option><option value="7D">Last 7 days</option><option value="30D">Last 30 days</option>
        </select>
      </div>

      {/* Tabular Audit Table */}
      <div className="data-table-container">
        <table className="data-table-technical">
          <thead>
            <tr>
              <th style={{ width: '58px' }}>Scene</th>
              <th style={{ width: '120px' }}>Task</th>
              <th>Analytical Query</th>
              <th style={{ width: '160px' }}>Confidence</th>
              <th style={{ width: '100px' }}>Status</th>
              <th style={{ width: '140px' }}>Date</th>
              <th style={{ width: '130px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: 'var(--space-6)', color: 'var(--text-muted)' }}>
                  {history.length === 0 ? 'No completed analyses in local storage.' : 'No analyses match active filter.'}
                </td>
              </tr>
            ) : (
              filtered.map((item) => {
                const dateStr = new Date(item.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
                const level = item.confidenceLevel || 'LOW';

                return (
                  <tr
                    key={item.id}
                    onClick={() => handleReopen(item)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td><div className="history-thumb">{item.primaryPreview ? <img src={item.primaryPreview} alt="" /> : <span>EO</span>}</div></td>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
                      {item.task}
                    </td>
                    <td style={{ color: 'var(--text-primary)' }}>
                      <strong className="history-query-preview">{item.query}</strong><span className="history-sensor-label">{sensorFor(item)}</span>
                    </td>
                    <td>
                      <span style={{
                        fontSize: '0.72rem',
                        fontFamily: 'var(--font-mono)',
                        fontWeight: 600,
                        color: level === 'HIGH' ? 'var(--color-success)' : level === 'MEDIUM' ? 'var(--color-warning)' : 'var(--color-error)'
                      }}>
                        ● {level} {item.confidenceScore !== null && `(${(item.confidenceScore * 100).toFixed(0)}%)`}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--color-success)' }}>
                      {item.status}
                    </td>
                    <td className="mono-cell" style={{ fontSize: '0.75rem' }}>
                      {dateStr}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        type="button"
                        style={{ background: 'transparent', border: '1px solid var(--border-default)', color: 'var(--text-secondary)', padding: '2px 6px', borderRadius: '3px', fontSize: '0.7rem', marginRight: '4px', cursor: 'pointer' }}
                        onClick={(e) => handleReanalyze(item, e)}
                        title="Re-run in workspace"
                      >
                        Re-run
                      </button>
                      <button type="button" className="history-open-btn" onClick={(e) => { e.stopPropagation(); handleReopen(item); }}>Open</button>
                      <button
                        type="button"
                        style={{ background: 'transparent', border: 'none', color: 'var(--color-error)', fontSize: '0.75rem', cursor: 'pointer' }}
                        onClick={(e) => handleDelete(item.id, e)}
                        title="Delete entry"
                      >
                        ✕
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
