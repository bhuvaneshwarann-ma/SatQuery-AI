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
    id: 'demo-complete',
    title: 'Complete Multisensor Demo',
    mode: 'AUTO',
    query: 'Compare these dates and use the optical and SAR images together to explain built-up and water-covered regions.',
    meta: 'All inputs · recommended first run',
    primaryAsset: 'sample_satellite_port.jpg',
    secondAsset: 'sample_satellite_port_t2_synthetic.jpg',
    sarAsset: 'sample_sentinel1_sar_mauritius.jpg',
  },
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
    title: 'Optical + SAR Image Statistics',
    mode: 'OPTICAL_SAR',
    query: 'Analyze optical and SAR radar cross-modal backscatter imagery',
    meta: 'Intensity Overlay · <0.5s',
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
    setInputOptions,
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
  const inputChecks = [
    { label: 'Primary image', ok: Boolean(state.primaryImage || state.primaryPreview), required: true },
    ...(isChange ? [{ label: 'Second date / T2 image', ok: Boolean(state.secondImage || state.secondPreview), required: true }] : []),
    ...(isSar ? [{ label: 'SAR image', ok: Boolean(state.sarImage || state.sarPreview), required: true }] : []),
  ];
  const modeLabels: Record<TaskMode, string> = {
    AUTO: 'Agent router',
    VQA: 'Visual Q&A',
    GROUNDING: 'Find regions',
    CHANGE_DETECTION: 'Compare dates',
    OPTICAL_SAR: 'Optical + SAR',
  };
  const modeDescriptions: Record<TaskMode, string> = {
    AUTO: 'SatQuery selects the specialist workflow from your question and inputs.',
    VQA: 'Ask a question about one remote-sensing image.',
    GROUNDING: 'Locate a named object or region and return spatial evidence.',
    CHANGE_DETECTION: 'Compare two aligned observations and explain the change.',
    OPTICAL_SAR: 'Join optical context with co-located radar evidence.',
  };

  return (
    <div className="workspace-page">
      <div className="workspace-intro">
        <div>
          <span className="workspace-eyebrow">REMOTE-SENSING ANALYSIS</span>
          <h1>Ask your satellite data a question.</h1>
          <p>{modeDescriptions[state.taskMode]}</p>
        </div>
        <div className="workspace-intro-hint">
          <span className="intro-hint-dot" />
          <span>Evidence-first results with an auditable execution trace</span>
        </div>
      </div>
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
              {modeLabels[mode]}
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
            <span><b className="section-step-number">01</b> INPUT SOURCES</span>
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
                  Alignment must be verified; equal dimensions alone are insufficient.
                </span>
              </div>
            )}

            {/* SAR Radar for Optical-SAR */}
            {isSar && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <DropZone
                  label="Microwave SAR Channel"
                  sublabel="Radar backscatter intensity"
                  badge="SAR INPUT"
                  file={state.sarImage}
                  previewUrl={state.sarPreview}
                  onFileSelect={(f) => setSarImage(f)}
                  onFileRemove={() => setSarImage(null)}
                  disabled={loading}
                />
                <span style={{ fontSize: '0.68rem', color: 'var(--color-warning)' }}>
                  SAR PROVENANCE: UNVERIFIED
                </span>
              </div>
            )}

            {/* Standard Presets */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
              <span className="field-label-technical">SAMPLE INPUT PRESETS</span>
              <button type="button" className="complete-demo-btn" onClick={() => loadPreset(DEMO_PRESETS[0])} disabled={loading}>
                <span>Load complete demo</span><span>3 inputs · routed automatically</span>
              </button>
              <div className="preset-list-clean">
                {DEMO_PRESETS.slice(1).map((preset) => (
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
              title={`${state.taskMode} · Image Preview`}
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
            <span><b className="section-step-number">02</b> QUERY &amp; EXECUTION</span>
          </div>

          <form onSubmit={handleSubmit} className="query-form-block">
            <label style={{ display: 'block', marginBottom: 12 }}>
              <input type="checkbox" checked={state.evaluationMode ?? false} onChange={e => setInputOptions({ evaluationMode: e.target.checked })} />
              {' '}Evaluation mode — require verified benchmark images or matching geographic grids
            </label>
            <details style={{ marginBottom: 12 }}>
              <summary>Satellite image bands and source information</summary>
              <p>For multispectral TIFFs, enter the red, green and blue band positions (starting at 1). SAR previews use the first band unless you select another. Source information is recorded as user supplied.</p>
              {(['image_path', 'second_image_path', 'sar_image_path'] as const).map((key, index) => (
                <div key={key} style={{ margin: '8px 0' }}>
                  <label>{['Primary image', 'Second date', 'SAR image'][index]} source / sensor{' '}
                    <input type="text" value={state.inputMetadata?.[key]?.sensor ?? ''} onChange={e => setInputOptions({ inputMetadata: { ...state.inputMetadata, [key]: { ...state.inputMetadata?.[key], sensor: e.target.value } } })} />
                  </label>
                  <label>{' '}Band positions{' '}
                    <input type="text" placeholder={index === 2 ? '1,1,1' : '3,2,1'} pattern="[1-9][0-9]*,[1-9][0-9]*,[1-9][0-9]*" onChange={e => setInputOptions({ inputMetadata: { ...state.inputMetadata, [key]: { ...state.inputMetadata?.[key], rgb_bands: e.target.value ? e.target.value.split(',').map(x => Number(x) - 1) : undefined } } })} />
                  </label>
                </div>
              ))}
            </details>
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
              <div className="query-helper-row">
                <span>{state.query.length}/500 characters</span>
                <span>{state.query.trim() ? 'Ready to route' : 'Add a question to continue'}</span>
              </div>
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

            <div className="input-readiness-card" aria-live="polite">
              <div className="input-readiness-header"><span>INPUT READINESS</span><span>{inputChecks.filter((item) => item.ok).length}/{inputChecks.length}</span></div>
              {inputChecks.map((item) => <div className="input-check-row" key={item.label}><span className={item.ok ? 'check-ok' : 'check-missing'}>{item.ok ? '✓' : '○'}</span><span>{item.label}</span><span>{item.ok ? 'Ready' : 'Required'}</span></div>)}
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
