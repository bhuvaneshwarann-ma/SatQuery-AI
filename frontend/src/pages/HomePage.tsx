import React from 'react';
import { useRouter } from '../context/RouterContext';
import { useAnalysis, type TaskMode } from '../context/AnalysisContext';

export const HomePage: React.FC = () => {
  const { navigate } = useRouter();
  const { setTaskMode } = useAnalysis();

  const handleLaunchTask = (mode: TaskMode) => {
    setTaskMode(mode);
    navigate('/analyze');
  };

  return (
    <div className="home-page-container">
      {/* Workstation Briefing Panel */}
      <section className="hero-briefing-panel">
        <div className="briefing-left">
          <span className="briefing-tagline">EARTH OBSERVATION INTELLIGENCE</span>
          <h1 className="briefing-headline">Ask. Locate. Compare. Analyze.</h1>
          <p className="briefing-summary">
            A controlled visual intelligence workspace for satellite imagery. SatQuery AI pairs domain-adapted vision-language models, zero-shot spatial grounding, bi-temporal differential change detection, and cross-modal optical-SAR correlation in an audited agentic pipeline.
          </p>

          <div className="briefing-actions">
            <button
              type="button"
              className="btn-primary"
              onClick={() => navigate('/analyze')}
            >
              Open Analysis Workspace →
            </button>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => navigate('/scenes')}
            >
              Browse Scene Catalog
            </button>
          </div>

          <div style={{ marginTop: 'var(--space-2)', fontSize: '0.74rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
            <span style={{ color: 'var(--color-warning)', fontWeight: 600 }}>Scientific Notice:</span> Provides model-derived, uncalibrated evidence-strength heuristics and deterministic radar correlation. Does not claim calibrated statistical accuracy or automated disaster alerting.
          </div>
        </div>

        {/* Remote Sensing Imagery Preview Window */}
        <div className="briefing-imagery-window">
          <div className="window-header">
            <span>SATELLITE RASTER SOURCE · PORT OF SANTOS</span>
            <span>512 × 512 GSD</span>
          </div>
          <div className="window-canvas">
            <img src="/samples/sample_satellite_port.jpg" alt="Port of Santos Satellite Imagery" />
            <div className="window-reticle-overlay">
              <span className="reticle-label">OPTICAL RGB · 0.5M GSD</span>
              <span className="reticle-label">23.96° S, 46.33° W</span>
            </div>
          </div>
        </div>
      </section>

      {/* Capability Matrix Section */}
      <section className="capability-matrix-section">
        <span className="section-title-technical">ANALYTICAL CAPABILITIES &amp; ENGINES</span>

        <table className="capability-matrix-table">
          <thead>
            <tr>
              <th style={{ width: '18%' }}>Capability</th>
              <th style={{ width: '30%' }}>Analytical Objective</th>
              <th style={{ width: '28%' }}>Underlying Engine</th>
              <th style={{ width: '14%' }}>Latency Profile</th>
              <th style={{ width: '10%' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>VQA Reasoning</td>
              <td>Natural language question answering over remote sensing scenes</td>
              <td><code>AdaptLLM/Qwen2.5-VL-3B-Instruct</code></td>
              <td><span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>~50s</span></td>
              <td>
                <span className="matrix-action-link" onClick={() => handleLaunchTask('VQA')}>
                  Launch →
                </span>
              </td>
            </tr>
            <tr>
              <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Visual Grounding</td>
              <td>Zero-shot spatial bounding box localization of target objects</td>
              <td><code>IDEA/Grounding-DINO-Tiny</code></td>
              <td><span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>~8s</span></td>
              <td>
                <span className="matrix-action-link" onClick={() => handleLaunchTask('GROUNDING')}>
                  Launch →
                </span>
              </td>
            </tr>
            <tr>
              <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Change Detection</td>
              <td>Bi-temporal differential distance heatmap across temporal pairs</td>
              <td><code>Siamese-ResNet18-Differencer</code></td>
              <td><span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>&lt;1s</span></td>
              <td>
                <span className="matrix-action-link" onClick={() => handleLaunchTask('CHANGE_DETECTION')}>
                  Launch →
                </span>
              </td>
            </tr>
            <tr>
              <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Optical + SAR Fusion</td>
              <td>Cross-modal optical reflectance and radar backscatter correlation</td>
              <td><code>Dual-Stream Multi-Sensor Engine</code></td>
              <td><span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>&lt;0.5s</span></td>
              <td>
                <span className="matrix-action-link" onClick={() => handleLaunchTask('OPTICAL_SAR')}>
                  Launch →
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      {/* System Integrity & Pipeline Summary */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
        <div style={{ background: 'var(--surface-primary)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-panel)', padding: 'var(--space-4)' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)', marginBottom: '4px' }}>
            01 · AGENT ROUTER &amp; FIREWALL
          </div>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
            User requests pass through deterministic contract validation and parameter firewalls. Unknown tools and unauthorized injection parameters are intercepted in &lt;20ms before any GPU execution.
          </p>
        </div>

        <div style={{ background: 'var(--surface-primary)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-panel)', padding: 'var(--space-4)' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)', marginBottom: '4px' }}>
            02 · EVIDENCE-BASED HEURISTICS
          </div>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
            Confidence levels (LOW / MEDIUM / HIGH) represent uncalibrated evidence strength heuristics calculated across five visual signals. Hard uncertainty ceilings prevent overconfidence on ambiguous imagery.
          </p>
        </div>

        <div style={{ background: 'var(--surface-primary)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-panel)', padding: 'var(--space-4)' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)', marginBottom: '4px' }}>
            03 · OBSERVABLE AUDIT TRACE
          </div>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
            SatQuery AI logs strictly observable operational events: input validation, router decisions, authorized tool arguments, and tensor latencies. Zero stochastic chain-of-thought tokens are exposed.
          </p>
        </div>
      </section>
    </div>
  );
};
