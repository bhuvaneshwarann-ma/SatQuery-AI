import React from 'react';
import { IconInfo, IconShield, IconTerminal } from '../components/common/Icons';

export const EvaluationPage: React.FC = () => {
  return (
    <div className="evaluation-page-container">
      {/* Header */}
      <div className="evaluation-header">
        <div>
          <h2 className="page-title">Evaluation &amp; Performance Benchmarks</h2>
          <p className="page-subtitle">
            Empirical baseline metrics evaluated on standardized remote sensing benchmarks and local RTX 5050 hardware telemetry.
          </p>
        </div>

        <div className="eval-status-badge">
          <span className="badge-tag">SUITE STATUS:</span>
          <span className="badge-val">BASELINE EVALUATION (N=20)</span>
        </div>
      </div>

      {/* Mandatory Benchmark Disclosure Banner */}
      <div className="eval-disclosure-banner">
        <IconInfo size={16} className="text-secondary flex-shrink-0" />
        <div className="banner-text">
          <strong className="text-primary">Scientific Rigor &amp; Reproducibility Guarantee:</strong> The benchmarks presented below reflect an <em>N=20</em> baseline slice designed for verifiable test reproducibility on workstation hardware. SatQuery AI does not claim state-of-the-art (SOTA) operational accuracy or unvalidated production readiness. All metrics represent empirical measurements of zero-shot domain-adapted weights against public ground truth.
        </div>
      </div>

      {/* Benchmark Tables / Cards */}
      <div className="benchmarks-tables-grid">
        {/* RSVQA-LR Section */}
        <div className="bench-section-panel">
          <div className="bench-panel-header">
            <div>
              <span className="geo-badge mb-1">VLM REASONING BENCHMARK</span>
              <h3 className="bench-title">RSVQA-LR Remote Sensing Benchmark</h3>
              <p className="text-xs text-secondary mt-1">
                Low-Resolution Remote Sensing VQA (Sentinel-2 overhead scenes) targeting object presence, land use categorization, and numeric count queries.
              </p>
            </div>
            <div className="bench-sample-size-tag">
              <span>N = 20 BASELINE</span>
            </div>
          </div>

          <div className="table-wrapper mt-3">
            <table className="geospatial-table">
              <thead>
                <tr>
                  <th>METRIC</th>
                  <th>SCORE</th>
                  <th>EVALUATION BASELINE</th>
                  <th>PRECISION / TARGET</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="font-semibold text-primary">Exact Match (EM)</td>
                  <td className="font-mono text-accent font-bold text-sm">35.0%</td>
                  <td className="text-xs text-secondary">Strict string equality vs RSVQA ground truth</td>
                  <td className="font-mono text-xs">RSVQA-LR Test Split</td>
                </tr>
                <tr>
                  <td className="font-semibold text-primary">Token F1 Score</td>
                  <td className="font-mono text-accent font-bold text-sm">0.2525</td>
                  <td className="text-xs text-secondary">Token overlap harmonic mean</td>
                  <td className="font-mono text-xs">RSVQA-LR Test Split</td>
                </tr>
                <tr>
                  <td className="font-semibold text-primary">Mean Pipeline Latency</td>
                  <td className="font-mono text-primary text-xs">50.11 s</td>
                  <td className="text-xs text-secondary">End-to-end vision encoder + autoregressive decoding</td>
                  <td className="font-mono text-xs">CUDA FP16, RTX 5050</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="bench-panel-footer">
            <span className="text-xs text-muted">CHECKPOINT:</span>
            <code className="font-mono text-xs text-secondary">AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct</code>
            <span className="text-muted">•</span>
            <span className="text-xs text-muted">WEIGHTS: FP16</span>
          </div>
        </div>

        {/* LEVIR-CD Section */}
        <div className="bench-section-panel">
          <div className="bench-panel-header">
            <div>
              <span className="geo-badge mb-1">CHANGE DETECTION BENCHMARK</span>
              <h3 className="bench-title">LEVIR-CD Bi-Temporal Building Change Benchmark</h3>
              <p className="text-xs text-secondary mt-1">
                Evaluated on LEVIR-CD bi-temporal building change dataset assessing pixel-level precision, recall, and differential intersection-over-union.
              </p>
            </div>
            <div className="bench-sample-size-tag">
              <span>N = 20 BASELINE</span>
            </div>
          </div>

          <div className="table-wrapper mt-3">
            <table className="geospatial-table">
              <thead>
                <tr>
                  <th>METRIC</th>
                  <th>SCORE</th>
                  <th>EVALUATION BASELINE</th>
                  <th>PRECISION / TARGET</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="font-semibold text-primary">Macro IoU</td>
                  <td className="font-mono text-accent font-bold text-sm">0.0878</td>
                  <td className="text-xs text-secondary">Intersection over Union on change masks</td>
                  <td className="font-mono text-xs">LEVIR-CD Test Split</td>
                </tr>
                <tr>
                  <td className="font-semibold text-primary">Macro F1 Score</td>
                  <td className="font-mono text-accent font-bold text-sm">0.1535</td>
                  <td className="text-xs text-secondary">Harmonic mean of pixel precision and recall</td>
                  <td className="font-mono text-xs">LEVIR-CD Test Split</td>
                </tr>
                <tr>
                  <td className="font-semibold text-primary">Macro Precision</td>
                  <td className="font-mono text-secondary text-xs">0.1237</td>
                  <td className="text-xs text-secondary">True positive pixel ratio</td>
                  <td className="font-mono text-xs">LEVIR-CD Test Split</td>
                </tr>
                <tr>
                  <td className="font-semibold text-primary">Macro Recall</td>
                  <td className="font-mono text-accent font-bold text-sm">0.6755</td>
                  <td className="text-xs text-secondary">Identified change pixel coverage</td>
                  <td className="font-mono text-xs">LEVIR-CD Test Split</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="bench-panel-footer">
            <span className="text-xs text-muted">MODEL:</span>
            <code className="font-mono text-xs text-secondary">Siamese-ResNet18-FeatureDifferencer</code>
            <span className="text-muted">•</span>
            <span className="text-xs text-muted">LATENCY: 27.4 ms (Inference)</span>
          </div>
        </div>
      </div>

      {/* System Hardware & Latency Telemetry */}
      <div className="eval-section-block">
        <div className="flex items-center gap-2 mb-2">
          <IconTerminal size={15} className="text-accent" />
          <h3 className="eval-block-title">Hardware Profile &amp; End-to-End Latency Telemetry</h3>
        </div>
        <p className="text-xs text-secondary mb-3">
          Measured on local host hardware (NVIDIA GeForce RTX 5050 Laptop GPU, CUDA 13.0, PyTorch 2.14.0+cu130).
        </p>

        <div className="table-wrapper">
          <table className="geospatial-table">
            <thead>
              <tr>
                <th>ANALYTICAL TOOL</th>
                <th>UNDERLYING ENGINE / MODEL</th>
                <th>OBSERVED LATENCY</th>
                <th>PEAK VRAM</th>
                <th>EXECUTION MODE</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong className="text-primary">VQA</strong></td>
                <td className="font-mono text-xs text-secondary">AdaptLLM Qwen2.5-VL-3B-Instruct</td>
                <td><span className="font-mono text-xs text-accent">~50.98 s</span></td>
                <td className="font-mono text-xs text-secondary">~6.9 GB</td>
                <td className="text-xs text-secondary">CUDA FP16 Autoregressive</td>
              </tr>
              <tr>
                <td><strong className="text-primary">Visual Grounding</strong></td>
                <td className="font-mono text-xs text-secondary">IDEA Grounding DINO Tiny</td>
                <td><span className="font-mono text-xs text-accent">~7.98 s</span></td>
                <td className="font-mono text-xs text-secondary">~1.3 GB</td>
                <td className="text-xs text-secondary">PyTorch Tensor Cross-Attention</td>
              </tr>
              <tr>
                <td><strong className="text-primary">Change Detection</strong></td>
                <td className="font-mono text-xs text-secondary">Siamese ResNet-18 Differencer</td>
                <td><span className="font-mono text-xs text-accent">0.75 s</span></td>
                <td className="font-mono text-xs text-secondary">~0.8 GB</td>
                <td className="text-xs text-secondary">PyTorch Feature Extraction</td>
              </tr>
              <tr>
                <td><strong className="text-primary">Optical-SAR</strong></td>
                <td className="font-mono text-xs text-secondary">Dual-Stream Multi-Sensor Engine</td>
                <td><span className="font-mono text-xs text-accent">0.28 s</span></td>
                <td className="font-mono text-xs text-secondary">&lt;0.2 GB</td>
                <td className="text-xs text-secondary">NumPy / SciPy Correlation Matrix</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Honest Scientific Disclosures & Roadmap */}
      <div className="eval-section-block">
        <div className="flex items-center gap-2 mb-2">
          <IconShield size={15} className="text-accent" />
          <h3 className="eval-block-title">Operational Disclosures &amp; Architectural Boundaries</h3>
        </div>

        <div className="limitations-grid">
          <div className="limitation-item-card">
            <div className="limitation-header">
              <span className="badge-roadmap">REQUIREMENT #5: PARTIAL / OPEN</span>
              <h4 className="limitation-title">Domain-Adapted VLM Checkpoint Status</h4>
            </div>
            <p className="limitation-desc">
              The system currently integrates the public open-source AdaptLLM remote sensing checkpoint. Fine-tuning a fully proprietary checkpoint exclusively on Indian Earth Observation imagery (Cartosat, Resourcesat) remains an active roadmap milestone.
            </p>
          </div>

          <div className="limitation-item-card">
            <div className="limitation-header">
              <span className="badge-sar">DATA CLASSIFICATION: PROXY SAR</span>
              <h4 className="limitation-title">Simulated Microwave Radar Channel</h4>
            </div>
            <p className="limitation-desc">
              Due to institutional data licensing constraints on genuine spaceborne ISRO RISAT-1A complex SLC datasets, a calibrated radiometric roughness proxy is deployed in the live demo assets.
            </p>
          </div>

          <div className="limitation-item-card">
            <div className="limitation-header">
              <span className="badge-synthetic">TEMPORAL BENCHMARK</span>
              <h4 className="limitation-title">Small Subset &amp; Synthetic Pair Verification</h4>
            </div>
            <p className="limitation-desc">
              Change detection verification relies on an <em>N=20</em> baseline slice and controlled synthetic temporal pairs. Operational invariance across atmospheric haze and disparate viewing angles is not claimed.
            </p>
          </div>

          <div className="limitation-item-card">
            <div className="limitation-header">
              <span className="badge-conf">CONFIDENCE SEMANTICS</span>
              <h4 className="limitation-title">Uncalibrated Evidence-Strength Heuristic</h4>
            </div>
            <p className="limitation-desc">
              Confidence scores are derived from a 5-signal visual consistency heuristic. They communicate the presence and stability of observable evidence, strictly avoiding claims of statistical correctness probabilities.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
