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

  const filtered = history.filter((item) => {
    const matchesSearch =
      searchTerm.trim() === '' ||
      item.query.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.task.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.model.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesTask =
      filterTask === 'ALL' || item.task.toUpperCase() === filterTask.toUpperCase();

    return matchesSearch && matchesTask;
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
      <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center', background: 'var(--surface-primary)', border: '1px solid var(--border-default)', padding: 'var(--space-2) var(--space-3)', borderRadius: 'var(--radius-control)' }}>
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
      </div>

      {/* Tabular Audit Table */}
      <div className="data-table-container">
        <table className="data-table-technical">
          <thead>
            <tr>
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
                <td colSpan={6} style={{ textAlign: 'center', padding: 'var(--space-6)', color: 'var(--text-muted)' }}>
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
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
                      {item.task}
                    </td>
                    <td style={{ color: 'var(--text-primary)' }}>
                      "{item.query}"
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
