import React, { useEffect } from 'react';
import { useAnalysis, type TaskMode } from '../context/AnalysisContext';
import { useRouter } from '../context/RouterContext';
import { DropZone } from '../components/common/DropZone';
import { ImageViewer } from '../components/common/ImageViewer';
import { QueryChips } from '../components/common/QueryChips';
import { LiveAnalysisStages } from '../components/common/LiveAnalysisStages';
import { ErrorBanner } from '../components/ErrorBanner';

interface DemoPreset {
  id: string;
  title: string;
  mode: TaskMode;
  query: string;
  meta: string;
  primaryAsset: string;
  secondAsset?: string;
  sarAsset?: string;
}

const DEMO_PRESETS: DemoPreset[] = [
  {
    id: 'demo-vqa',
    title: 'Port Question Answering',
    mode: 'VQA',
    query: 'What type of maritime port or facility is shown in this satellite image?',
    meta: 'Qwen2.5-VL-3B · ~50s',
    primaryAsset: 'sample_satellite_port.jpg',
  },
  {
    id: 'demo-grounding',
    title: 'Vessel Target Localization',
    mode: 'GROUNDING',
    query: 'Locate the ships in this satellite image.',
    meta: 'Grounding DINO · ~8s',
    primaryAsset: 'sample_satellite_port.jpg',
  },
  {
    id: 'demo-change',
    title: 'Bi-Temporal Difference Detection',
    mode: 'CHANGE_DETECTION',
    query: 'Identify differences and what changed between these two images',
    meta: 'Siamese ResNet · <1s',
    primaryAsset: 'sample_satellite_port.jpg',
    secondAsset: 'sample_satellite_port_t2_synthetic.jpg',
  },
  {
    id: 'demo-sar',
    title: 'Optical + SAR Radiometric Synergy',
    mode: 'OPTICAL_SAR',
    query: 'Analyze optical and SAR radar cross-modal backscatter imagery',
    meta: 'Dual-Stream · <0.5s',
    primaryAsset: 'sample_satellite_port.jpg',
    sarAsset: 'sample_sentinel1_sar_mauritius.jpg',
  },
];

export const AnalysisPage: React.FC = () => {
  const {
    state,
    setTaskMode,
    setQuery,
    setPrimaryImage,
    setSecondImage,
    setSarImage,
    setParameter,
    resetInputs,
    loadPreset,
    loading,
    elapsedSeconds,
    activeStage,
    error,
    clearError,
    executeAnalysis,
  } = useAnalysis();

  const { routeState } = useRouter();

  useEffect(() => {
    if (routeState?.taskMode) {
      setTaskMode(routeState.taskMode);
    }
    if (routeState?.preset) {
      loadPreset(routeState.preset);
    }
  }, [routeState, setTaskMode, loadPreset]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    executeAnalysis();
  };

  const isChange = state.taskMode === 'CHANGE_DETECTION' || state.taskMode === 'AUTO';
  const isSar = state.taskMode === 'OPTICAL_SAR' || state.taskMode === 'AUTO';

  return (
    <div className="workspace-page">
      {/* Active Validation or Clarification Banner */}
      {error && (
        <ErrorBanner
          status={error.status}
          errorType={error.errorType}
          message={error.message}
          clarificationPrompt={error.clarificationPrompt}
          validationErrors={error.validationErrors}
          onDismiss={clearError}
        />
      )}

      {/* Top Segmented Task Selector */}
      <div className="workspace-task-bar">
        <div className="task-segmented-group">
          {(['AUTO', 'VQA', 'GROUNDING', 'CHANGE_DETECTION', 'OPTICAL_SAR'] as TaskMode[]).map((mode) => (
            <button
              key={mode}
              type="button"
              className={`task-segment-btn ${state.taskMode === mode ? 'active' : ''}`}
              onClick={() => setTaskMode(mode)}
              disabled={loading}
            >
              {mode.replace('_', ' ')}
            </button>
          ))}
        </div>

        <span className="workspace-status-tag">
          {loading ? `EXECUTING · ${elapsedSeconds.toFixed(1)}S` : 'WORKSTATION READY'}
        </span>
      </div>

      {/* 3-Column Geospatial Workstation Layout */}
      <div className="workspace-workstation-grid">
        {/* COLUMN 1: Ingestion & Presets (Left Rail) */}
        <div className="workstation-rail-left">
          <div className="rail-section-header">
            <span>INPUT RASTER SOURCES</span>
            <button
              type="button"
              style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '0.7rem', cursor: 'pointer' }}
              onClick={resetInputs}
              disabled={loading}
            >
              RESET ALL
            </button>
          </div>

          <div className="rail-scroll-content">
            {/* Primary Optical */}
            <DropZone
              label="T1 / Base Scene"
              sublabel="Optical multispectral raster"
              badge="REQUIRED"
              file={state.primaryImage}
              previewUrl={state.primaryPreview}
              onFileSelect={(f) => setPrimaryImage(f)}
              onFileRemove={() => setPrimaryImage(null)}
              disabled={loading}
            />

            {/* Post-Event T2 for Change */}
            {isChange && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <DropZone
                  label="T2 Post-Event Scene"
                  sublabel="Co-registered comparative scene"
                  badge="CHANGE"
                  file={state.secondImage}
                  previewUrl={state.secondPreview}
                  onFileSelect={(f) => setSecondImage(f)}
                  onFileRemove={() => setSecondImage(null)}
                  disabled={loading}
                />
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                  Evaluated on controlled synthetic pair (LEVIR-CD slice).
                </span>
              </div>
            )}

            {/* SAR Radar for Optical-SAR */}
            {isSar && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <DropZone
                  label="Microwave SAR Channel"
                  sublabel="Radar backscatter intensity"
                  badge="PROXY SAR"
                  file={state.sarImage}
                  previewUrl={state.sarPreview}
                  onFileSelect={(f) => setSarImage(f)}
                  onFileRemove={() => setSarImage(null)}
                  disabled={loading}
                />
                <span style={{ fontSize: '0.68rem', color: 'var(--color-warning)' }}>
                  DATA CLASSIFICATION: PROXY SAR
                </span>
              </div>
            )}

            {/* Standard Presets */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
              <span className="field-label-technical">VERIFIED BENCHMARK PRESETS</span>
              <div className="preset-list-clean">
                {DEMO_PRESETS.map((preset) => (
                  <button
                    key={preset.id}
                    type="button"
                    className="preset-row-btn"
                    onClick={() => loadPreset(preset)}
                    disabled={loading}
                  >
                    <span className="preset-row-title">{preset.title}</span>
                    <span className="preset-row-meta">{preset.meta}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* COLUMN 2: Center Geospatial Canvas (Largest Area) */}
        <div className="workstation-canvas-center">
          {state.primaryPreview ? (
            <ImageViewer
              primarySrc={state.primaryPreview}
              secondarySrc={state.secondPreview || state.sarPreview}
              mode={state.secondPreview || state.sarPreview ? 'side-by-side' : 'single'}
              title={`${state.taskMode} · 512 × 512 GSD`}
            />
          ) : (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-3)', background: '#040608', color: 'var(--text-muted)' }}>
              <span style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)' }}>NO SATELLITE RASTER LOADED IN VIEWPORT</span>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => loadPreset(DEMO_PRESETS[0])}
              >
                Load Port of Santos Sample
              </button>
            </div>
          )}
        </div>

        {/* COLUMN 3: Analysis Controls & Query Panel (Right) */}
        <div className="workstation-panel-right">
          <div className="rail-section-header">
            <span>ANALYTICAL QUERY &amp; EXECUTION</span>
          </div>

          <form onSubmit={handleSubmit} className="query-form-block">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label htmlFor="technical-query-input" className="field-label-technical">
                Query Specification
              </label>
              <textarea
                id="technical-query-input"
                className="query-input-technical"
                placeholder="e.g. What type of maritime port or facility is shown in this satellite image?"
                value={state.query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
              />
            </div>

            {/* Compact Suggested Query Chips */}
            <QueryChips
              taskMode={state.taskMode}
              onSelectQuery={(q) => setQuery(q)}
            />

            {/* Allowlisted Parameters Accordion */}
            <div className="parameters-section-compact">
              <span className="field-label-technical">ALLOWLISTED PARAMETERS</span>

              {state.taskMode === 'GROUNDING' && (
                <div className="param-slider-row">
                  <div className="param-label-split">
                    <span>Box Threshold:</span>
                    <span className="param-val-mono">{state.parameters.box_threshold ?? 0.35}</span>
                  </div>
                  <input
                    type="range"
                    min="0.1"
                    max="0.9"
                    step="0.05"
                    value={state.parameters.box_threshold ?? 0.35}
                    onChange={(e) => setParameter('box_threshold', parseFloat(e.target.value))}
                    disabled={loading}
                  />
                </div>
              )}

              {state.taskMode === 'CHANGE_DETECTION' && (
                <div className="param-slider-row">
                  <div className="param-label-split">
                    <span>Difference Threshold (τ):</span>
                    <span className="param-val-mono">{state.parameters.threshold ?? 0.40}</span>
                  </div>
                  <input
                    type="range"
                    min="0.1"
                    max="0.9"
                    step="0.05"
                    value={state.parameters.threshold ?? 0.40}
                    onChange={(e) => setParameter('threshold', parseFloat(e.target.value))}
                    disabled={loading}
                  />
                </div>
              )}

              {(state.taskMode === 'VQA' || state.taskMode === 'AUTO') && (
                <div className="param-slider-row">
                  <div className="param-label-split">
                    <span>Max Generated Tokens:</span>
                    <span className="param-val-mono">{state.parameters.max_new_tokens ?? 100}</span>
                  </div>
                  <input
                    type="range"
                    min="32"
                    max="256"
                    step="16"
                    value={state.parameters.max_new_tokens ?? 100}
                    onChange={(e) => setParameter('max_new_tokens', parseInt(e.target.value, 10))}
                    disabled={loading}
                  />
                </div>
              )}
            </div>

            {/* Run Analysis Action */}
            <button
              type="submit"
              className="btn-analyze-technical"
              disabled={loading || !state.query.trim()}
            >
              {loading ? `RUNNING PIPELINE (${elapsedSeconds.toFixed(1)}s)...` : 'RUN ANALYSIS →'}
            </button>
          </form>

          {/* Live Operational Pipeline Stages */}
          {loading && (
            <LiveAnalysisStages
              activeStage={activeStage}
              elapsedSeconds={elapsedSeconds}
              selectedTool={state.taskMode === 'AUTO' ? 'AgentRouter' : state.taskMode}
            />
          )}
        </div>
      </div>
    </div>
  );
};
