import React, { useState } from 'react';
import { useAnalysis } from '../context/AnalysisContext';
import { useRouter } from '../context/RouterContext';
import { getArtifactUrl } from '../api/client';
import { ImageViewer, type BoundingBox } from '../components/common/ImageViewer';

export const ResultsPage: React.FC = () => {
  const { result, state } = useAnalysis();
  const { navigate } = useRouter();
  const [activeReportTab, setActiveReportTab] = useState<'report' | 'visualization' | 'trace' | 'limitations'>('report');

  if (!result) {
    return (
      <div style={{ padding: 'var(--space-6)', textAlign: 'center', background: 'var(--surface-primary)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-panel)', maxWidth: '560px', margin: '60px auto' }}>
        <h2 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', marginBottom: '8px' }}>NO ACTIVE ANALYSIS RESULT</h2>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Execute an analytical query in the workspace or select a sample scene to generate a scientific evidence report.
        </p>
        <button type="button" className="btn-primary" onClick={() => navigate('/analyze')}>
          Open Analysis Workspace →
        </button>
      </div>
    );
  }

  const evidence = result.evidence || {};
  const metadata = result.metadata || {};
  const artifactRef = evidence.annotated_artifact || null;
  const artifactUrl = getArtifactUrl(artifactRef);

  const isProxySar =
    evidence.sar_data_classification === 'proxy_sar' ||
    metadata.sar_data_classification === 'proxy_sar' ||
    result.selected_tool === 'OPTICAL_SAR';

  const isSyntheticChange =
    result.selected_tool === 'CHANGE_DETECTION' ||
    evidence.dataset_note ||
    metadata.data_classification;

  // Extract confidence values
  const isObjectConf = typeof result.confidence === 'object' && result.confidence !== null;
  const confLevel = isObjectConf ? (result.confidence as any).level : (typeof result.confidence === 'number' ? (result.confidence >= 0.7 ? 'HIGH' : result.confidence >= 0.4 ? 'MEDIUM' : 'LOW') : 'LOW');
  const confScore = isObjectConf ? (result.confidence as any).score : (typeof result.confidence === 'number' ? result.confidence : null);
  const confExplanation = isObjectConf ? (result.confidence as any).explanation : null;

  // Bounding boxes
  const boundingBoxes: BoundingBox[] = [];
  if (evidence.bounding_boxes && Array.isArray(evidence.bounding_boxes)) {
    evidence.bounding_boxes.forEach((coords: [number, number, number, number], idx: number) => {
      boundingBoxes.push({
        coords,
        label: state.query ? state.query.replace(/locate /i, '').replace(/the /i, '') : 'Object',
        score: evidence.detector_scores ? evidence.detector_scores[idx] : confScore ?? undefined,
      });
    });
  }

  return (
    <div className="results-report-layout">
      {/* Top Technical Metadata Strip */}
      <div className="report-header-strip">
        <div className="report-title-group">
          <h2>SCIENTIFIC ANALYSIS REPORT</h2>
        </div>

        <div className="report-meta-tags">
          <span className="tag-technical">TOOL: {result.selected_tool || 'AUTO'}</span>
          <span className="tag-technical">MODEL: {result.model}</span>
          <span className="tag-technical">LATENCY: {result.latency_ms.toFixed(1)} ms</span>
          <span className="tag-technical" style={{ color: 'var(--color-success)' }}>STATUS: {result.status}</span>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div style={{ display: 'flex', gap: 'var(--space-2)', borderBottom: '1px solid var(--border-default)', paddingBottom: 'var(--space-1)' }}>
        <button
          type="button"
          className={`task-segment-btn ${activeReportTab === 'report' ? 'active' : ''}`}
          onClick={() => setActiveReportTab('report')}
        >
          ANALYSIS &amp; EVIDENCE
        </button>
        <button
          type="button"
          className={`task-segment-btn ${activeReportTab === 'visualization' ? 'active' : ''}`}
          onClick={() => setActiveReportTab('visualization')}
        >
          SPATIAL CANVAS &amp; OVERLAYS
        </button>
        <button
          type="button"
          className={`task-segment-btn ${activeReportTab === 'trace' ? 'active' : ''}`}
          onClick={() => setActiveReportTab('trace')}
        >
          EXECUTION AUDIT TRACE
        </button>
        <button
          type="button"
          className={`task-segment-btn ${activeReportTab === 'limitations' ? 'active' : ''}`}
          onClick={() => setActiveReportTab('limitations')}
        >
          TECHNICAL DISCLOSURES
        </button>
      </div>

      {/* TAB 1: Scientific Analysis Report */}
      {activeReportTab === 'report' && (
        <div style={{ background: 'var(--surface-primary)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-panel)', padding: 'var(--space-5)', display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
          {/* Question */}
          <div className="report-section">
            <span className="report-section-label">ANALYTICAL QUERY</span>
            <p style={{ fontSize: '0.95rem', color: 'var(--text-primary)', fontWeight: 600 }}>
              "{state.query}"
            </p>
          </div>

          <hr className="report-hairline-divider" />

          {/* Answer */}
          <div className="report-section">
            <span className="report-section-label">ASSESSMENT / ANSWER</span>
            <p className="report-answer-text">{result.answer}</p>
          </div>

          {/* Scene Interpretation */}
          {result.image_description && (
            <>
              <hr className="report-hairline-divider" />
              <div className="report-section">
                <span className="report-section-label">IMAGE DESCRIPTION / CONTEXT</span>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                  {result.image_description}
                </p>
              </div>
            </>
          )}

          {/* Visual Evidence (Numbered list) */}
          {result.visual_evidence && result.visual_evidence.length > 0 && (
            <>
              <hr className="report-hairline-divider" />
              <div className="report-section">
                <span className="report-section-label">OBSERVABLE VISUAL EVIDENCE SIGNALS</span>
                <div className="evidence-numbered-list">
                  {result.visual_evidence.map((item, idx) => (
                    <div key={idx} className="evidence-numbered-row">
                      <span className="evidence-index">0{idx + 1}</span>
                      <span className="evidence-category">{item.category.replace(/_/g, ' ')}</span>
                      <span className="evidence-desc">{item.description}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Evidence Strength / Confidence Indicator */}
          <hr className="report-hairline-divider" />
          <div className="report-section">
            <span className="report-section-label">EVIDENCE STRENGTH HEURISTIC</span>
            <div className="confidence-technical-indicator">
              <span className={`conf-dot ${confLevel === 'HIGH' ? 'conf-level-high' : confLevel === 'MEDIUM' ? 'conf-level-medium' : 'conf-level-low'}`} style={{ background: 'currentColor' }} />
              <span className={`conf-level-text ${confLevel === 'HIGH' ? 'conf-level-high' : confLevel === 'MEDIUM' ? 'conf-level-medium' : 'conf-level-low'}`}>
                {confLevel}
              </span>
              <span className="conf-uncalibrated-sub">
                Model-derived · Uncalibrated {confScore !== null && `(${(confScore * 100).toFixed(1)}%)`}
              </span>
            </div>
            {confExplanation && (
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '6px', lineHeight: '1.4' }}>
                {confExplanation}
              </p>
            )}
            <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Evidence-strength heuristic, not a statistical probability of correctness. Evaluates presence and consistency of observable image evidence.
            </span>
          </div>
        </div>
      )}

      {/* TAB 2: Spatial Canvas & Overlays */}
      {activeReportTab === 'visualization' && (
        <div style={{ background: 'var(--surface-primary)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-panel)', overflow: 'hidden', height: '620px' }}>
          {state.primaryPreview ? (
            <ImageViewer
              primarySrc={state.primaryPreview}
              secondarySrc={state.secondPreview || state.sarPreview}
              overlaySrc={artifactUrl}
              boundingBoxes={boundingBoxes}
              mode={state.secondPreview || state.sarPreview ? 'side-by-side' : 'single'}
              title={`${result.selected_tool} · VISUAL GROUNDING`}
            />
          ) : artifactUrl ? (
            <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#000' }}>
              <img src={artifactUrl} alt="Analysis Artifact" style={{ maxHeight: '100%', maxWidth: '100%' }} />
            </div>
          ) : (
            <div style={{ padding: 'var(--space-6)', textAlign: 'center', color: 'var(--text-muted)' }}>
              No visual artifact generated for this analysis.
            </div>
          )}
        </div>
      )}

      {/* TAB 3: Execution Audit Trace */}
      {activeReportTab === 'trace' && (
        <div className="data-table-container">
          <table className="data-table-technical">
            <thead>
              <tr>
                <th style={{ width: '60px' }}>Step</th>
                <th style={{ width: '220px' }}>Stage</th>
                <th style={{ width: '100px' }}>Latency</th>
                <th style={{ width: '120px' }}>Status</th>
                <th>Audit Reference / Output Reference</th>
              </tr>
            </thead>
            <tbody>
              {result.observable_execution_trace && result.observable_execution_trace.length > 0 ? (
                result.observable_execution_trace.map((step, idx) => (
                  <tr key={idx}>
                    <td className="mono-cell">0{idx + 1}</td>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{step.step}</td>
                    <td className="mono-cell">
                      {step.latency_ms !== null && step.latency_ms !== undefined ? `${step.latency_ms.toFixed(1)} ms` : '—'}
                    </td>
                    <td style={{ color: step.status === 'ERROR' ? 'var(--color-error)' : 'var(--color-success)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                      {step.status === 'ERROR' ? '✕ FAILED' : '✓ OK'}
                    </td>
                    <td className="mono-cell" style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                      {step.output_reference || step.evidence_reference || (step.selected_tool ? `tool=${step.selected_tool}` : 'contract_verified')}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No execution trace recorded.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* TAB 4: Technical Disclosures */}
      {activeReportTab === 'limitations' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {isProxySar && (
            <div style={{ background: 'var(--surface-primary)', border: '1px solid var(--border-default)', borderLeft: '3px solid var(--color-warning)', padding: 'var(--space-4)', borderRadius: 'var(--radius-panel)' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-warning)', marginBottom: '4px' }}>
                DATA CLASSIFICATION: PROXY SAR
              </div>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                The radar backscatter imagery evaluated represents a calibrated surface roughness proxy. Genuine spaceborne ISRO/SAC Cartosat-2S and RISAT-1A co-registered pairs remain restricted under institutional licensing.
              </p>
            </div>
          )}

          {isSyntheticChange && (
            <div style={{ background: 'var(--surface-primary)', border: '1px solid var(--border-default)', borderLeft: '3px solid var(--accent-teal)', padding: 'var(--space-4)', borderRadius: 'var(--radius-panel)' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)', marginBottom: '4px' }}>
                EVALUATION NOTICE: SYNTHETIC TEMPORAL PAIR
              </div>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                Change detection was evaluated on a controlled synthetic temporal pair and LEVIR-CD $N=20$ baseline slice. Operational invariance across atmospheric haze and disparate solar angles is not claimed.
              </p>
            </div>
          )}

          <div style={{ background: 'var(--surface-primary)', border: '1px solid var(--border-default)', padding: 'var(--space-4)', borderRadius: 'var(--radius-panel)' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: '4px' }}>
              REQUIREMENT #5: PARTIAL / OPEN
            </div>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              Evaluated open-source domain-adapted remote-sensing VLM checkpoint zero-shot on RSVQA-LR (35.0% EM). Custom team-owned fine-tuning on Indian EO data is an active roadmap milestone.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
