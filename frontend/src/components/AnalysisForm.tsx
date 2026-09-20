import React, { useState, useRef, useEffect } from 'react';
import type { AnalyzePayload } from '../api/client';

export type TaskMode = 'AUTO' | 'VQA' | 'GROUNDING' | 'CHANGE_DETECTION' | 'OPTICAL_SAR';

interface AnalysisFormProps {
  onAnalyze: (payload: AnalyzePayload, previews: { primary: string | null; second: string | null; sar: string | null }) => void;
  loading: boolean;
}

interface DemoPreset {
  id: string;
  badge: string;
  title: string;
  description: string;
  mode: TaskMode;
  query: string;
  primaryAsset: string;
  secondAsset?: string;
  sarAsset?: string;
}

const DEMO_PRESETS: DemoPreset[] = [
  {
    id: 'demo-a',
    badge: 'Demo A: VQA',
    title: 'Port Facility Question Answering',
    description: 'Natural language dialogue via AdaptLLM Qwen2.5-VL-3B (~50s)',
    mode: 'VQA',
    query: 'What type of maritime port or facility is shown in this satellite image?',
    primaryAsset: 'sample_satellite_port.jpg',
  },
  {
    id: 'demo-b',
    badge: 'Demo B: Grounding',
    title: 'Maritime Vessel Localization',
    description: 'Zero-shot referring expression grounding via Grounding DINO (~8s)',
    mode: 'GROUNDING',
    query: 'Locate the ships in this satellite image.',
    primaryAsset: 'sample_satellite_port.jpg',
  },
  {
    id: 'demo-c',
    badge: 'Demo C: Change',
    title: 'Bi-Temporal Difference Detection',
    description: 'Differential feature distance heatmap via Siamese ResNet-18 (<1s)',
    mode: 'CHANGE_DETECTION',
    query: 'Identify differences and what changed between these two images',
    primaryAsset: 'sample_satellite_port.jpg',
    secondAsset: 'sample_satellite_port_t2_synthetic.jpg',
  },
  {
    id: 'demo-d',
    badge: 'Demo D: Optical+SAR',
    title: 'Cross-Modal Radiometric Fusion',
    description: 'Dual-stream optical and radar backscatter analysis (<0.5s)',
    mode: 'OPTICAL_SAR',
    query: 'Analyze optical and SAR radar cross-modal backscatter imagery',
    primaryAsset: 'sample_satellite_port.jpg',
    sarAsset: 'sample_sentinel1_sar_mauritius.jpg',
  },
  {
    id: 'demo-e',
    badge: 'Safety & Firewall',
    title: 'Ambiguous Query Interception',
    description: 'Rejects invalid intent in <20ms before model execution',
    mode: 'AUTO',
    query: 'calculate orbital trajectory',
    primaryAsset: 'sample_satellite_port.jpg',
  },
];

export const AnalysisForm: React.FC<AnalysisFormProps> = ({ onAnalyze, loading }) => {
  const [taskMode, setTaskMode] = useState<TaskMode>('AUTO');
  const [query, setQuery] = useState('');
  
  const [primaryImage, setPrimaryImage] = useState<File | null>(null);
  const [primaryPreview, setPrimaryPreview] = useState<string | null>(null);

  const [secondImage, setSecondImage] = useState<File | null>(null);
  const [secondPreview, setSecondPreview] = useState<string | null>(null);

  const [sarImage, setSarImage] = useState<File | null>(null);
  const [sarPreview, setSarPreview] = useState<string | null>(null);

  const [loadingPresetId, setLoadingPresetId] = useState<string | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const primaryInputRef = useRef<HTMLInputElement>(null);
  const secondInputRef = useRef<HTMLInputElement>(null);
  const sarInputRef = useRef<HTMLInputElement>(null);

  // Live stopwatch when loading
  useEffect(() => {
    let timer: any;
    if (loading) {
      setElapsedSeconds(0);
      const start = performance.now();
      timer = setInterval(() => {
        setElapsedSeconds(Math.round((performance.now() - start) / 100) / 10);
      }, 100);
    } else {
      setElapsedSeconds(0);
    }
    return () => clearInterval(timer);
  }, [loading]);

  // Generate image previews
  useEffect(() => {
    if (!primaryImage) {
      setPrimaryPreview(null);
      return;
    }
    const url = URL.createObjectURL(primaryImage);
    setPrimaryPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [primaryImage]);

  useEffect(() => {
    if (!secondImage) {
      setSecondPreview(null);
      return;
    }
    const url = URL.createObjectURL(secondImage);
    setSecondPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [secondImage]);

  useEffect(() => {
    if (!sarImage) {
      setSarPreview(null);
      return;
    }
    const url = URL.createObjectURL(sarImage);
    setSarPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [sarImage]);

  // Helper to load sample files from public /samples/
  const loadPreset = async (preset: DemoPreset) => {
    if (loading) return;
    setLoadingPresetId(preset.id);

    try {
      setTaskMode(preset.mode);
      setQuery(preset.query);

      // Load primary asset
      const primRes = await fetch(`/samples/${preset.primaryAsset}`);
      const primBlob = await primRes.blob();
      const primFile = new File([primBlob], preset.primaryAsset, { type: primBlob.type || 'image/jpeg' });
      setPrimaryImage(primFile);

      // Load second asset if present
      if (preset.secondAsset) {
        const secRes = await fetch(`/samples/${preset.secondAsset}`);
        const secBlob = await secRes.blob();
        const secFile = new File([secBlob], preset.secondAsset, { type: secBlob.type || 'image/jpeg' });
        setSecondImage(secFile);
      } else {
        setSecondImage(null);
      }

      // Load SAR asset if present
      if (preset.sarAsset) {
        const sarRes = await fetch(`/samples/${preset.sarAsset}`);
        const sarBlob = await sarRes.blob();
        const sarFile = new File([sarBlob], preset.sarAsset, { type: sarBlob.type || 'image/jpeg' });
        setSarImage(sarFile);
      } else {
        setSarImage(null);
      }
    } catch (err) {
      console.error('Failed to load sample demo preset asset:', err);
    } finally {
      setLoadingPresetId(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    onAnalyze(
      {
        query: query.trim(),
        image: primaryImage,
        second_image: secondImage,
        sar_image: sarImage,
        task: taskMode === 'AUTO' ? null : taskMode,
      },
      {
        primary: primaryPreview,
        second: secondPreview,
        sar: sarPreview,
      }
    );
  };

  const showSecondImageSlot = taskMode === 'AUTO' || taskMode === 'CHANGE_DETECTION';
  const showSarImageSlot = taskMode === 'AUTO' || taskMode === 'OPTICAL_SAR';

  return (
    <form className="analysis-form-card" onSubmit={handleSubmit}>
      {/* Quick Demo Workflow Presets */}
      <div className="form-section demo-presets-section">
        <div className="section-label-row">
          <label className="section-label">
            <span>⚡ Evaluator Quick Presets</span>
            <span className="section-hint">One-click loading of verified sample assets and analytical queries</span>
          </label>
        </div>
        <div className="demo-presets-grid">
          {DEMO_PRESETS.map((preset) => (
            <button
              type="button"
              key={preset.id}
              className={`preset-card ${loadingPresetId === preset.id ? 'preset-card-loading' : ''}`}
              onClick={() => loadPreset(preset)}
              disabled={loading}
            >
              <div className="preset-card-top">
                <span className="preset-badge">{preset.badge}</span>
                {loadingPresetId === preset.id && <span className="preset-spinner" />}
              </div>
              <strong className="preset-title">{preset.title}</strong>
              <span className="preset-desc">{preset.description}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Task Mode Selector Tabs */}
      <div className="form-section">
        <label className="section-label">
          <span>1. Operational Intent / Tool Mode</span>
          <span className="section-hint">Deterministic router assigns intent and enforces parameter firewall</span>
        </label>
        <div className="task-mode-tabs" role="tablist">
          {(['AUTO', 'VQA', 'GROUNDING', 'CHANGE_DETECTION', 'OPTICAL_SAR'] as TaskMode[]).map((mode) => (
            <button
              type="button"
              key={mode}
              className={`mode-tab ${taskMode === mode ? 'mode-tab-active' : ''}`}
              onClick={() => setTaskMode(mode)}
              disabled={loading}
            >
              {mode === 'AUTO' ? '⚡ Autonomous Router' : mode.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Upload Dropzones */}
      <div className="form-section">
        <label className="section-label">
          <span>2. Satellite Imagery Assets</span>
          <span className="section-hint">Supported: .jpg, .jpeg, .png, .tif (Max 100MB)</span>
        </label>

        <div className="upload-slots-grid">
          {/* Slot 1: Primary / Optical Asset */}
          <div className="upload-slot">
            <div className="slot-header">
              <span className="slot-title">
                {taskMode === 'CHANGE_DETECTION' ? 'Baseline Image (T1)' : taskMode === 'OPTICAL_SAR' ? 'Optical Sensor Imagery' : 'Primary Satellite Image'}
              </span>
              <span className="slot-badge required-badge">Required</span>
            </div>

            <input
              type="file"
              ref={primaryInputRef}
              accept=".jpg,.jpeg,.png,.tif,.tiff,image/*"
              style={{ display: 'none' }}
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setPrimaryImage(e.target.files[0]);
                }
              }}
              disabled={loading}
            />

            {primaryPreview ? (
              <div className="preview-container">
                <img src={primaryPreview} alt="Primary satellite target" className="asset-thumbnail" />
                <div className="asset-meta-overlay">
                  <span className="asset-filename" title={primaryImage?.name}>{primaryImage?.name}</span>
                  <button
                    type="button"
                    className="asset-remove-btn"
                    onClick={() => setPrimaryImage(null)}
                    disabled={loading}
                    title="Remove asset"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ) : (
              <div
                className="dropzone-area"
                onClick={() => primaryInputRef.current?.click()}
              >
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="upload-icon">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <span className="dropzone-label">Click to select primary image</span>
                <span className="dropzone-sub">Optical RGB / Multispectral</span>
              </div>
            )}
          </div>

          {/* Slot 2: Second Image (Change Detection T2) */}
          {showSecondImageSlot && (
            <div className="upload-slot">
              <div className="slot-header">
                <span className="slot-title">Post-Event Image (T2)</span>
                <span className={`slot-badge ${taskMode === 'CHANGE_DETECTION' ? 'required-badge' : 'optional-badge'}`}>
                  {taskMode === 'CHANGE_DETECTION' ? 'Required' : 'Optional'}
                </span>
              </div>

              <input
                type="file"
                ref={secondInputRef}
                accept=".jpg,.jpeg,.png,.tif,.tiff,image/*"
                style={{ display: 'none' }}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setSecondImage(e.target.files[0]);
                  }
                }}
                disabled={loading}
              />

              {secondPreview ? (
                <div className="preview-container">
                  <img src={secondPreview} alt="Second temporal pass" className="asset-thumbnail" />
                  <div className="asset-meta-overlay">
                    <span className="asset-filename" title={secondImage?.name}>{secondImage?.name}</span>
                    <button
                      type="button"
                      className="asset-remove-btn"
                      onClick={() => setSecondImage(null)}
                      disabled={loading}
                      title="Remove asset"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ) : (
                <div
                  className="dropzone-area"
                  onClick={() => secondInputRef.current?.click()}
                >
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="upload-icon">
                    <circle cx="12" cy="12" r="10" />
                    <polyline points="12 6 12 12 16 14" />
                  </svg>
                  <span className="dropzone-label">Select T2 temporal pass</span>
                  <span className="dropzone-sub">For Bi-Temporal Change Detection</span>
                </div>
              )}
            </div>
          )}

          {/* Slot 3: SAR Image (Radar Backscatter) */}
          {showSarImageSlot && (
            <div className="upload-slot">
              <div className="slot-header">
                <span className="slot-title">SAR Radar Asset</span>
                <span className={`slot-badge ${taskMode === 'OPTICAL_SAR' ? 'required-badge' : 'optional-badge'}`}>
                  {taskMode === 'OPTICAL_SAR' ? 'Required' : 'Optional'}
                </span>
              </div>

              <input
                type="file"
                ref={sarInputRef}
                accept=".jpg,.jpeg,.png,.tif,.tiff,image/*"
                style={{ display: 'none' }}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setSarImage(e.target.files[0]);
                  }
                }}
                disabled={loading}
              />

              {sarPreview ? (
                <div className="preview-container">
                  <img src={sarPreview} alt="SAR microwave radar" className="asset-thumbnail" />
                  <div className="asset-meta-overlay">
                    <span className="asset-filename" title={sarImage?.name}>{sarImage?.name}</span>
                    <button
                      type="button"
                      className="asset-remove-btn"
                      onClick={() => setSarImage(null)}
                      disabled={loading}
                      title="Remove asset"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ) : (
                <div
                  className="dropzone-area"
                  onClick={() => sarInputRef.current?.click()}
                >
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="upload-icon">
                    <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z" />
                    <path d="M12 6a6 6 0 1 0 6 6 6 6 0 0 0-6-6z" />
                  </svg>
                  <span className="dropzone-label">Select SAR radar image</span>
                  <span className="dropzone-sub">Sentinel-1 / Proxy SAR</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Query Input Section */}
      <div className="form-section">
        <label className="section-label" htmlFor="analytical-query-input">
          <span>3. Analytical Question or Objective</span>
          <span className="section-hint">Ask in plain English or select a quick preset above</span>
        </label>

        <textarea
          id="analytical-query-input"
          className="query-textarea"
          rows={3}
          placeholder="Enter natural-language query (e.g. 'What objects are visible?', 'Locate all cargo ships', or 'What changed between these images?')..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
        />
      </div>

      {/* Form Submission Actions */}
      <div className="form-actions-row">
        <div className="inputs-summary">
          {primaryImage && <span className="summary-chip">✓ Primary: {primaryImage.name}</span>}
          {secondImage && <span className="summary-chip">✓ T2: {secondImage.name}</span>}
          {sarImage && <span className="summary-chip">✓ SAR: {sarImage.name}</span>}
        </div>

        <button
          type="submit"
          className={`analyze-submit-btn ${loading ? 'btn-loading' : ''}`}
          disabled={loading || !query.trim()}
        >
          {loading ? (
            <div className="btn-loading-content">
              <span className="spinner-dot" />
              <span>Analyzing... ({elapsedSeconds.toFixed(1)}s)</span>
            </div>
          ) : (
            <div className="btn-normal-content">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <span>Run Satellite Analysis</span>
            </div>
          )}
        </button>
      </div>

      {/* Elapsed Time & Execution Lock State */}
      {loading && (
        <div className="analysis-progress-notice">
          <div className="progress-notice-header">
            <span className="notice-icon">⏱</span>
            <strong>Elapsed Time: {elapsedSeconds.toFixed(1)}s — Execution Lock Active</strong>
          </div>
          <p className="progress-notice-desc">
            {taskMode === 'VQA'
              ? 'Autoregressive 3B VLM reasoning via AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct (~50s typical). Concurrent executions are blocked to guarantee stability.'
              : taskMode === 'GROUNDING'
              ? 'Executing Grounding DINO Swin-Transformer cross-attention forward pass (~8–10s typical)...'
              : taskMode === 'CHANGE_DETECTION'
              ? 'Executing Siamese-ResNet18 bi-temporal differential distance calculation (<1s typical)...'
              : taskMode === 'OPTICAL_SAR'
              ? 'Executing Dual-Stream radiometric matrix ingestion & Pearson cross-correlation (<0.5s typical)...'
              : 'Agent Router intent classification and parameter firewall verification in progress (<20ms)...'}
          </p>
        </div>
      )}
    </form>
  );
};
