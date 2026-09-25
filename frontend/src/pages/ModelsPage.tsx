import React, { useState, useEffect } from 'react';
import { fetchTools, type ToolDefinitionModel } from '../api/client';
import { useRouter } from '../context/RouterContext';
import { useAnalysis, type TaskMode } from '../context/AnalysisContext';
import { IconShield, IconInfo, IconExternalLink } from '../components/common/Icons';

interface ModelProfile {
  id: string;
  name: string;
  category: 'Deep Multimodal Neural Network' | 'Transformer Object Detector' | 'Siamese Feature Engine' | 'Deterministic Signal Engine';
  task: TaskMode;
  taskTitle: string;
  weightsRef: string;
  role: string;
  vramFootprint: string;
  typicalLatency: string;
  inputContract: string;
  outputContract: string;
  confidenceSemantics: string;
  parameters: Array<{ name: string; type: string; defaultVal: any; range: string; desc: string }>;
}

const MODEL_PROFILES: ModelProfile[] = [
  {
    id: 'model-vqa',
    name: 'AdaptLLM Remote Sensing Qwen2.5-VL-3B',
    category: 'Deep Multimodal Neural Network',
    task: 'VQA',
    taskTitle: 'Visual Question Answering',
    weightsRef: 'AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct',
    role: 'Domain-adapted visual reasoning over remote sensing overhead imagery',
    vramFootprint: '~6.9 GB peak VRAM (NVIDIA CUDA)',
    typicalLatency: '~50.9s pipeline execution',
    inputContract: 'Primary satellite image (RGB) + natural language query',
    outputContract: 'Contextual answer text + scene description + dynamic visual evidence items',
    confidenceSemantics: 'Evidence Strength Heuristic: 5-signal weighted sum (uncalibrated)',
    parameters: [
      { name: 'max_new_tokens', type: 'int', defaultVal: 100, range: '16 – 256', desc: 'Maximum autoregressive generated tokens' },
      { name: 'do_sample', type: 'bool', defaultVal: false, range: 'false (deterministic)', desc: 'Greedy decoding for verifiable outputs' },
      { name: 'min_pixels', type: 'int', defaultVal: 200704, range: '200,704 – 401,408', desc: 'Vision encoder resolution patch bounds' },
    ],
  },
  {
    id: 'model-grounding',
    name: 'Grounding DINO Tiny',
    category: 'Transformer Object Detector',
    task: 'GROUNDING',
    taskTitle: 'Visual Referring Expression Grounding',
    weightsRef: 'IDEA-Research/grounding-dino-tiny',
    role: 'Open-vocabulary zero-shot spatial bounding box localization',
    vramFootprint: '~1.3 GB VRAM',
    typicalLatency: '~7.9s pipeline execution',
    inputContract: 'Primary satellite image + target object referring expression',
    outputContract: 'Array of bounding boxes [y1, x1, y2, x2] + detector scores',
    confidenceSemantics: 'Detector score — uncalibrated cross-attention logit (NOT IoU or accuracy)',
    parameters: [
      { name: 'box_threshold', type: 'float', defaultVal: 0.35, range: '0.10 – 0.90', desc: 'Bounding box cross-attention score filter' },
      { name: 'text_threshold', type: 'float', defaultVal: 0.25, range: '0.10 – 0.90', desc: 'Text-to-feature token alignment cutoff' },
    ],
  },
  {
    id: 'model-change',
    name: 'Siamese ResNet-18 Feature Differencer',
    category: 'Siamese Feature Engine',
    task: 'CHANGE_DETECTION',
    taskTitle: 'Bi-Temporal Change Difference Detection',
    weightsRef: 'Siamese-ResNet18-FeatureDifferencer',
    role: 'Extracts deep convolutional embeddings to compute pixel-wise differential distance',
    vramFootprint: '~0.8 GB VRAM',
    typicalLatency: '~0.75s pipeline execution',
    inputContract: 'Co-registered Baseline T1 image + Post-Event T2 image',
    outputContract: 'Differential distance heatmap artifact + changed pixel count & ratio',
    confidenceSemantics: 'Change evidence confidence: area stability margin (1.0 - change_ratio)',
    parameters: [
      { name: 'threshold', type: 'float', defaultVal: 0.40, range: '0.10 – 0.90', desc: 'Feature distance decision threshold (τ)' },
    ],
  },
  {
    id: 'model-sar',
    name: 'Dual-Stream Multi-Sensor Feature Ingestion Engine',
    category: 'Deterministic Signal Engine',
    task: 'OPTICAL_SAR',
    taskTitle: 'Optical + SAR Radiometric Synergy',
    weightsRef: 'Dual-Stream Cross-Modal Engine (Deterministic Algorithm)',
    role: 'Correlates optical spectral reflectance with microwave SAR radar backscatter anomalies',
    vramFootprint: 'CPU / GPU Tensor Matrix (<0.2 GB)',
    typicalLatency: '~0.28s pipeline execution',
    inputContract: 'Primary optical image + Microwave SAR radar asset',
    outputContract: 'Pearson correlation (r) + radar-dominant anomalies + cross-modal composite',
    confidenceSemantics: 'Pipeline integrity status: valid matrix dimension & cross-modal correlation',
    parameters: [
      { name: 'high_scatter_threshold', type: 'float', defaultVal: 180.0, range: '100.0 – 250.0', desc: 'SAR high-intensity backscatter threshold' },
    ],
  },
];

export const ModelsPage: React.FC = () => {
  const { navigate } = useRouter();
  const { setTaskMode } = useAnalysis();
  const [toolsData, setToolsData] = useState<ToolDefinitionModel[] | null>(null);
  const [selectedModelId, setSelectedModelId] = useState<string>(MODEL_PROFILES[0].id);

  useEffect(() => {
    fetchTools()
      .then((data) => setToolsData(data))
      .catch((err) => console.warn('Could not fetch tools catalog from backend:', err));
  }, []);

  const handleLaunchModel = (task: TaskMode) => {
    setTaskMode(task);
    navigate('/analyze');
  };

  const activeModel = MODEL_PROFILES.find((m) => m.id === selectedModelId) || MODEL_PROFILES[0];

  return (
    <div className="models-page-container">
      {/* Header */}
      <div className="models-header">
        <div>
          <h2 className="page-title">Model &amp; Engine Registry</h2>
          <p className="page-subtitle">
            Inspection catalog of domain-adapted neural weights and deterministic signal processing engines deployed in the SatQuery AI runtime.
          </p>
        </div>

        <div className="models-stats-pill">
          <span>{toolsData ? `${toolsData.length} Registered Tools` : '4 Registered Engines'}</span>
          <span className="pill-sep">•</span>
          <span>CUDA 13.0 Enabled</span>
        </div>
      </div>

      {/* Engineering Distinction Alert */}
      <div className="model-distinction-banner">
        <IconInfo size={16} className="text-secondary flex-shrink-0" />
        <div className="distinction-text">
          <strong className="text-primary">Engineering Distinction:</strong> SatQuery AI strictly segregates deep neural weights (Qwen2.5-VL-3B, Grounding DINO) from deterministic signal processing engines (Siamese Differencer, Dual-Stream Optical-SAR). All models operate behind an allowlisted parameter firewall to ensure reproducible, secure execution.
        </div>
      </div>

      {/* Main Content Layout: Registry Table + Inspector Drawer */}
      <div className="models-registry-layout">
        {/* Table Section */}
        <div className="registry-table-card">
          <div className="registry-card-header">
            <span className="registry-header-title">ACTIVE REGISTERED ENGINES ({MODEL_PROFILES.length})</span>
            <span className="registry-header-sub">SELECT ROW TO INSPECT SCHEMA &amp; CONTRACTS</span>
          </div>

          <div className="table-wrapper">
            <table className="geospatial-table">
              <thead>
                <tr>
                  <th>STATUS</th>
                  <th>IDENTIFIER / MODEL NAME</th>
                  <th>TASK MODE</th>
                  <th>TYPE</th>
                  <th>PEAK VRAM</th>
                  <th>TYPICAL LATENCY</th>
                  <th style={{ textAlign: 'right' }}>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {MODEL_PROFILES.map((model) => {
                  const isSelected = model.id === activeModel.id;
                  return (
                    <tr
                      key={model.id}
                      className={`registry-row ${isSelected ? 'row-selected' : ''}`}
                      onClick={() => setSelectedModelId(model.id)}
                    >
                      <td>
                        <span className="status-indicator">
                          <span className="status-dot status-dot-active" />
                          <span className="font-mono text-xs text-primary">ONLINE</span>
                        </span>
                      </td>
                      <td>
                        <div className="font-semibold text-primary">{model.name}</div>
                        <div className="font-mono text-xs text-muted truncate max-w-xs">{model.weightsRef}</div>
                      </td>
                      <td>
                        <span className="geo-badge">{model.task}</span>
                      </td>
                      <td className="text-secondary text-xs">{model.category}</td>
                      <td className="font-mono text-xs text-secondary">{model.vramFootprint}</td>
                      <td className="font-mono text-xs text-primary">{model.typicalLatency}</td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          type="button"
                          className="action-btn-sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleLaunchModel(model.task);
                          }}
                          title={`Test ${model.task} in Workspace`}
                        >
                          Launch ↗
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Model Detail Panel */}
        <div className="model-inspector-panel">
          <div className="inspector-panel-header">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="geo-badge">{activeModel.task}</span>
                <span className="text-xs text-muted font-mono">{activeModel.id.toUpperCase()}</span>
              </div>
              <h3 className="inspector-model-title">{activeModel.name}</h3>
              <div className="font-mono text-xs text-secondary">{activeModel.weightsRef}</div>
            </div>

            <button
              type="button"
              className="action-btn-primary"
              onClick={() => handleLaunchModel(activeModel.task)}
            >
              <span>Test in Workspace</span>
              <IconExternalLink size={13} />
            </button>
          </div>

          <p className="inspector-model-role">{activeModel.role}</p>

          {/* Specifications Grid */}
          <div className="inspector-specs-grid">
            <div className="spec-item">
              <span className="spec-k">CATEGORY</span>
              <span className="spec-v text-primary">{activeModel.category}</span>
            </div>
            <div className="spec-item">
              <span className="spec-k">VRAM FOOTPRINT</span>
              <span className="spec-v font-mono">{activeModel.vramFootprint}</span>
            </div>
            <div className="spec-item">
              <span className="spec-k">INPUT CONTRACT</span>
              <span className="spec-v font-mono text-xs">{activeModel.inputContract}</span>
            </div>
            <div className="spec-item">
              <span className="spec-k">OUTPUT CONTRACT</span>
              <span className="spec-v font-mono text-xs">{activeModel.outputContract}</span>
            </div>
          </div>

          {/* Confidence Semantics Note */}
          <div className="inspector-confidence-block">
            <span className="spec-k">CONFIDENCE / CERTAINTY SEMANTICS</span>
            <div className="inspector-confidence-text">
              <span className="font-mono text-xs text-primary">{activeModel.confidenceSemantics}</span>
            </div>
          </div>

          {/* Allowlisted Parameter Schema */}
          <div className="inspector-params-block">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <IconShield size={14} className="text-accent" />
                <span className="spec-k text-primary">ALLOWLISTED PARAMETER FIREWALL</span>
              </div>
              <span className="text-xs text-muted font-mono">{activeModel.parameters.length} PARAMETERS BOUND</span>
            </div>

            <div className="table-wrapper">
              <table className="geospatial-table params-table">
                <thead>
                  <tr>
                    <th>PARAMETER</th>
                    <th>TYPE</th>
                    <th>DEFAULT</th>
                    <th>VALID RANGE</th>
                    <th>PURPOSE / VALIDATION</th>
                  </tr>
                </thead>
                <tbody>
                  {activeModel.parameters.map((p) => (
                    <tr key={p.name}>
                      <td className="font-mono text-accent text-xs font-semibold">{p.name}</td>
                      <td><span className="geo-badge">{p.type}</span></td>
                      <td className="font-mono text-xs">{String(p.defaultVal)}</td>
                      <td className="font-mono text-xs text-secondary">{p.range}</td>
                      <td className="text-xs text-secondary">{p.desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
