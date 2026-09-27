import type { AnalysisApiResponse } from '../api/client';

// JSON preserves all evidence and execution fields; Markdown is readable offline.
export function downloadReport(result: AnalysisApiResponse, query: string, format: 'json' | 'md') {
  const savedAt = new Date().toISOString();
  const report = { exported_at: savedAt, query, ...result };
  const content = format === 'json' ? JSON.stringify(report, null, 2) : [
    '# SatQuery AI analysis report', '', `Exported: ${savedAt}`, '',
    '## Question', '', query, '', '## Answer', '', result.answer, '',
    `Status: ${result.status}`, `Model: ${result.model}`, '',
    '## Evidence, confidence, parameters and execution record', '',
    '```json', JSON.stringify(report, null, 2), '```', '',
    'Model outputs may be incorrect. Unavailable confidence is not a measured probability.',
  ].join('\n');
  const url = URL.createObjectURL(new Blob([content], { type: format === 'json' ? 'application/json' : 'text/markdown;charset=utf-8' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `satquery-report-${savedAt.replace(/[:.]/g, '-')}.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
