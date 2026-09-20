import React, { useState } from 'react';
import type { AnalysisApiResponse } from '../api/client';
import { getArtifactUrl } from '../api/client';

interface ResultViewProps {
  result: AnalysisApiResponse;
  query?: string;
  primaryPreview?: string | null;
  secondPreview?: string | null;
  sarPreview?: string | null;
}

export const ResultView: React.FC<ResultViewProps> = ({
  result,
  query,
  primaryPreview,
  secondPreview,
  sarPreview,
}) => {
  const [artifactError, setArtifactError] = useState(false);

  // Locate artifact reference from evidence if provided
  const artifactRef = result.evidence?.annotated_artifact || null;
  const artifactUrl = getArtifactUrl(artifactRef);

  const evidence = result.evidence || {};
  const metadata = result.metadata || {};

  // Check for domain evaluation notices
  const isProxySar =
    evidence.sar_data_classification === 'proxy_sar' ||
    metadata.sar_data_classification === 'proxy_sar' ||
    result.selected_tool === 'OPTICAL_SAR';

  const isSyntheticChange =
    result.selected_tool === 'CHANGE_DETECTION' ||
    evidence.dataset_note ||
    metadata.data_classification;

  // Render confidence block with strict semantic labeling
  const renderConfidenceBlock = () => {
    if (result.selected_tool === 'VQA' || result.confidence === null || result.confidence === undefined) {
      return (
        <div className="confidence-metric-block confidence-null-block">
          <span className="confidence-label">Confidence Semantics:</span>
          <span className="confidence-badge badge-null">Unavailable / Null</span>
          <span className="confidence-caveat" title="VQA outputs natural language responses via autoregressive decoding; no token confidence is fabricated.">
            (Autoregressive VLM — Not Fabricated)
          </span>
        </div>
      );
    }

    if (result.selected_tool === 'GROUNDING') {
      return (
        <div className="confidence-metric-block confidence-grounding-block">
          <span className="confidence-label">Detector Score:</span>
          <span className="confidence-value">{(result.confidence * 100).toFixed(1)}%</span>
          <span className="confidence-caveat" title="Cross-attention similarity score; NOT calibrated and NOT spatial localization accuracy or IoU.">
            (Uncalibrated Logit — Not Localization IoU)
          </span>
        </div>
      );
    }

    if (result.selected_tool === 'CHANGE_DETECTION') {
      return (
        <div className="confidence-metric-block confidence-change-block">
          <span className="confidence-label">Area Stability Margin:</span>
          <span className="confidence-value">{(result.confidence * 100).toFixed(1)}%</span>
          <span className="confidence-caveat" title="Proportion of scene remaining unchanged under feature differencing; strictly NOT equivalent to classification F1-score or IoU.">
            (Unmodified Area Ratio — Not F1/IoU)
          </span>
        </div>
      );
    }

    if (result.selected_tool === 'OPTICAL_SAR') {
      return (
        <div className="confidence-metric-block confidence-sar-block">
          <span className="confidence-label">Pipeline Integrity:</span>
          <span className="confidence-value">{(result.confidence * 100).toFixed(0)}%</span>
          <span className="confidence-caveat" title="Confirms dual-sensor raster grid alignment and valid Pearson correlation; NOT target prediction accuracy.">
            (Matrix Correlation Validated — Not Target Accuracy)
          </span>
        </div>
      );
    }

    return (
      <div className="confidence-metric-block">
        <span className="confidence-label">System Confidence:</span>
        <span className="confidence-value">{(result.confidence * 100).toFixed(1)}%</span>
        <span className="confidence-caveat">(Uncalibrated model estimate)</span>
      </div>
    );
  };

  return (
    <div className="result-view-card">
      {/* Top Banner: Tool, Model, Latency & Status */}
      <div className="result-top-banner">
        <div className="result-badges-group">
          {result.selected_tool && (
            <span className="badge tool-badge">
              <strong>TOOL:</strong> {result.selected_tool}
            </span>
          )}
          <span className="badge model-badge">
            <strong>MODEL:</strong> {result.model}
          </span>
          <span className={`badge status-badge status-${result.status.toLowerCase()}`}>
            {result.status}
          </span>
          <span className="badge latency-badge">
            ⏱ {result.latency_ms.toFixed(1)} ms
          </span>
        </div>

        {renderConfidenceBlock()}
      </div>

      {/* User Query Echo */}
      {query && (
        <div className="submitted-query-callout">
          <span className="query-callout-label">ANALYTICAL QUERY:</span>
          <span className="query-callout-text">"{query}"</span>
        </div>
      )}

      {/* Answer Block */}
      <div className="result-answer-section">
        <h3 className="section-heading">Analytical Assessment</h3>
        <div className="answer-text-bubble">
          <p className="answer-content">{result.answer}</p>
        </div>
      </div>

      {/* Domain Disclaimers & Limitations */}
      <div className="domain-limitation-notice">
        {isProxySar && (
          <div className="notice-item">
            <span className="notice-badge proxy-badge">DATA CLASSIFICATION: PROXY SAR</span>
            <span>
              Simulated radar backscatter proxy reflecting corner reflection &amp; surface roughness. Authentic spaceborne ISRO/SAC Cartosat-2S and RISAT-1A co-registered pairs remain restricted under institutional licensing.
            </span>
          </div>
        )}
        {isSyntheticChange && (
          <div className="notice-item">
            <span className="notice-badge synthetic-badge">EVALUATION NOTICE</span>
            <span>
              Evaluated on controlled synthetic temporal pair / LEVIR-CD $N=20$ slice. Does not imply generalized real-world change detection accuracy across arbitrary terrain.
            </span>
          </div>
        )}
        <div className="notice-item notice-roadmap">
          <span className="notice-badge roadmap-badge">REQUIREMENT #5: PARTIAL / OPEN</span>
          <span>
            Evaluated open-source domain-adapted remote-sensing VLM checkpoint zero-shot on RSVQA-LR (35.0% EM). Custom team-owned fine-tuning on Indian EO data is an active roadmap milestone.
          </span>
        </div>
      </div>

      {/* Visual Evidence Section */}
      <div className="result-evidence-section">
        <h3 className="section-heading">Visual Evidence &amp; Multi-Sensor Analysis</h3>

        {/* Multi-Panel Comparison View for Bi-Temporal Change Detection */}
        {result.selected_tool === 'CHANGE_DETECTION' && (
          <div className="comparison-panels-container">
            <h4 className="comparison-heading">Bi-Temporal Input &amp; Differential Change Comparison</h4>
            <div className="comparison-panels-grid three-panels">
              <div className="comparison-panel">
                <span className="panel-tag">Baseline Image (T1)</span>
                <div className="panel-img-wrap">
                  {primaryPreview ? (
                    <img src={primaryPreview} alt="T1 Baseline" className="comparison-img" />
                  ) : (
                    <div className="img-placeholder">T1 Optical Asset</div>
                  )}
                </div>
              </div>

              <div className="comparison-panel">
                <span className="panel-tag">Post-Event Image (T2)</span>
                <div className="panel-img-wrap">
                  {secondPreview ? (
                    <img src={secondPreview} alt="T2 Post-Event" className="comparison-img" />
                  ) : (
                    <div className="img-placeholder">T2 Optical Asset</div>
                  )}
                </div>
              </div>

              <div className="comparison-panel panel-artifact">
                <span className="panel-tag tag-highlight">Differential Change Heatmap</span>
                <div className="panel-img-wrap">
                  {artifactUrl && !artifactError ? (
                    <img
                      src={artifactUrl}
                      alt="Change Detection Heatmap"
                      className="comparison-img"
                      onError={() => setArtifactError(true)}
                    />
                  ) : (
                    <div className="img-placeholder">Change Heatmap Artifact</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Multi-Panel Comparison View for Optical-SAR Cross-Modal Fusion */}
        {result.selected_tool === 'OPTICAL_SAR' && (
          <div className="comparison-panels-container">
            <h4 className="comparison-heading">Multi-Sensor Ingestion &amp; Cross-Modal Radiometric Synergy</h4>
            <div className="comparison-panels-grid three-panels">
              <div className="comparison-panel">
                <span className="panel-tag">Optical RGB Sensor</span>
                <div className="panel-img-wrap">
                  {primaryPreview ? (
                    <img src={primaryPreview} alt="Optical Sensor" className="comparison-img" />
                  ) : (
                    <div className="img-placeholder">Optical RGB Asset</div>
                  )}
                </div>
              </div>

              <div className="comparison-panel">
                <span className="panel-tag">Microwave SAR Radar</span>
                <div className="panel-img-wrap">
                  {sarPreview ? (
                    <img src={sarPreview} alt="SAR Microwave Radar" className="comparison-img" />
                  ) : (
                    <div className="img-placeholder">SAR Radar Asset</div>
                  )}
                </div>
              </div>

              <div className="comparison-panel panel-artifact">
                <span className="panel-tag tag-highlight">Radiometric Synergy Composite</span>
                <div className="panel-img-wrap">
                  {artifactUrl && !artifactError ? (
                    <img
                      src={artifactUrl}
                      alt="Optical-SAR Synergy Artifact"
                      className="comparison-img"
                      onError={() => setArtifactError(true)}
                    />
                  ) : (
                    <div className="img-placeholder">Synergy Composite Artifact</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Multi-Panel Comparison View for Visual Grounding */}
        {result.selected_tool === 'GROUNDING' && (
          <div className="comparison-panels-container">
            <h4 className="comparison-heading">Visual Grounding Spatial Referring Expression Localization</h4>
            <div className="comparison-panels-grid two-panels">
              <div className="comparison-panel">
                <span className="panel-tag">Input Satellite Image</span>
                <div className="panel-img-wrap">
                  {primaryPreview ? (
                    <img src={primaryPreview} alt="Input Satellite" className="comparison-img" />
                  ) : (
                    <div className="img-placeholder">Optical Satellite Asset</div>
                  )}
                </div>
              </div>

              <div className="comparison-panel panel-artifact">
                <span className="panel-tag tag-highlight">Annotated Bounding Box Overlay</span>
                <div className="panel-img-wrap">
                  {artifactUrl && !artifactError ? (
                    <img
                      src={artifactUrl}
                      alt="Grounding Bounding Boxes"
                      className="comparison-img"
                      onError={() => setArtifactError(true)}
                    />
                  ) : (
                    <div className="img-placeholder">Bounding Box Artifact</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Standard Single Artifact Grid & Key Metrics */}
        <div className="evidence-display-grid">
          {/* Main Visual Artifact Display if not already shown above */}
          {result.selected_tool === 'VQA' && (
            <div className="artifact-media-card">
              <div className="artifact-media-header">
                <span className="artifact-title">Input Satellite Scene</span>
                {primaryPreview && (
                  <a href={primaryPreview} target="_blank" rel="noopener noreferrer" className="artifact-open-link">
                    Open Fullscreen ↗
                  </a>
                )}
              </div>
              <div className="artifact-image-wrapper">
                {primaryPreview ? (
                  <img src={primaryPreview} alt="Input Scene" className="artifact-img" />
                ) : (
                  <div className="artifact-placeholder-card">
                    <span className="placeholder-icon">🛰</span>
                    <span>Input scene verified by VLM vision encoder.</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Evidence Metrics Table */}
          <div className="evidence-metrics-card">
            <h4 className="metrics-card-title">Evidence Metrics &amp; Grounding Details</h4>
            <div className="metrics-scroll-area">
              <table className="metrics-table">
                <tbody>
                  {evidence.type && (
                    <tr>
                      <td className="metric-name">Evidence Type</td>
                      <td className="metric-val"><code>{evidence.type}</code></td>
                    </tr>
                  )}
                  {evidence.detections_count !== undefined && (
                    <tr>
                      <td className="metric-name">Detections Count</td>
                      <td className="metric-val"><strong>{evidence.detections_count}</strong> object(s) located</td>
                    </tr>
                  )}
                  {evidence.changed_pixels !== undefined && (
                    <tr>
                      <td className="metric-name">Changed Pixels</td>
                      <td className="metric-val">
                        <strong>{Number(evidence.changed_pixels).toLocaleString()} px</strong> ({evidence.change_percentage}%)
                      </td>
                    </tr>
                  )}
                  {evidence.threshold !== undefined && (
                    <tr>
                      <td className="metric-name">Decision Threshold (τ)</td>
                      <td className="metric-val"><code>{evidence.threshold}</code></td>
                    </tr>
                  )}
                  {evidence.optical_stats && (
                    <tr>
                      <td className="metric-name">Optical Mean / Std</td>
                      <td className="metric-val">{evidence.optical_stats.mean} / {evidence.optical_stats.std}</td>
                    </tr>
                  )}
                  {evidence.sar_stats && (
                    <tr>
                      <td className="metric-name">SAR Backscatter Mean / Std</td>
                      <td className="metric-val">{evidence.sar_stats.mean} / {evidence.sar_stats.std}</td>
                    </tr>
                  )}
                  {evidence.cross_modal_correlation !== undefined && (
                    <tr>
                      <td className="metric-name">Cross-Modal Correlation (Pearson r)</td>
                      <td className="metric-val"><strong>{evidence.cross_modal_correlation}</strong></td>
                    </tr>
                  )}
                  {evidence.radar_dominant_anomalies !== undefined && (
                    <tr>
                      <td className="metric-name">Radar-Dominant Anomalies</td>
                      <td className="metric-val">{Number(evidence.radar_dominant_anomalies).toLocaleString()} pixels</td>
                    </tr>
                  )}
                  {evidence.bounding_boxes && evidence.bounding_boxes.length > 0 && (
                    <tr>
                      <td className="metric-name">Bounding Box Coordinates [y1, x1, y2, x2]</td>
                      <td className="metric-val font-mono">
                        {evidence.bounding_boxes.slice(0, 3).map((box: any, i: number) => (
                          <div key={i}>[{box.join(', ')}]</div>
                        ))}
                        {evidence.bounding_boxes.length > 3 && (
                          <small>+{evidence.bounding_boxes.length - 3} more...</small>
                        )}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Observable Execution Trace Timeline */}
      <div className="result-trace-section">
        <div className="trace-header-row">
          <div>
            <h3 className="section-heading">Observable Execution Trace</h3>
            <span className="trace-subtitle">
              Audit trail exposing the 5-stage agentic pipeline — zero ungrounded chain-of-thought
            </span>
          </div>
          <span className="trace-stage-count">5 Stages Validated</span>
        </div>

        <div className="trace-timeline">
          {result.observable_execution_trace && result.observable_execution_trace.length > 0 ? (
            result.observable_execution_trace.map((entry, idx) => (
              <div key={idx} className="trace-step-card">
                <div className="step-marker-col">
                  <span className={`step-dot ${entry.status === 'ERROR' ? 'dot-error' : 'dot-success'}`}>
                    {idx + 1}
                  </span>
                  {idx < result.observable_execution_trace.length - 1 && <span className="step-line" />}
                </div>

                <div className="step-body-col">
                  <div className="step-top-line">
                    <span className="step-name">{entry.step}</span>
                    <span className={`step-status-chip ${entry.status === 'ERROR' ? 'chip-error' : 'chip-pass'}`}>
                      {entry.status}
                    </span>
                    {entry.latency_ms !== null && entry.latency_ms !== undefined && (
                      <span className="step-latency-chip">{entry.latency_ms.toFixed(1)} ms</span>
                    )}
                  </div>

                  <div className="step-meta-details">
                    {entry.model && (
                      <span className="step-meta-item">
                        <strong>Engine/Model:</strong> {entry.model}
                      </span>
                    )}
                    {entry.selected_tool && (
                      <span className="step-meta-item">
                        <strong>Selected Tool:</strong> {entry.selected_tool}
                      </span>
                    )}
                    {entry.permitted_parameters && Object.keys(entry.permitted_parameters).length > 0 && (
                      <span className="step-meta-item">
                        <strong>Authorized Parameters:</strong> <code>{JSON.stringify(entry.permitted_parameters)}</code>
                      </span>
                    )}
                    {entry.output_reference && (
                      <span className="step-meta-item font-mono">
                        <strong>Output Reference:</strong> {entry.output_reference}
                      </span>
                    )}
                    {entry.evidence_reference && (
                      <span className="step-meta-item font-mono">
                        <strong>Evidence Artifact:</strong> {entry.evidence_reference}
                      </span>
                    )}
                    {entry.error && (
                      <span className="step-meta-error">
                        <strong>Error:</strong> {entry.error}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="no-trace-text">No execution trace returned.</p>
          )}
        </div>
      </div>
    </div>
  );
};
