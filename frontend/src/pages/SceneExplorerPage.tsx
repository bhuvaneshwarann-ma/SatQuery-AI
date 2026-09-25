import React, { useState } from 'react';
import { useRouter } from '../context/RouterContext';
import { useAnalysis, type TaskMode } from '../context/AnalysisContext';

interface SceneAsset {
  id: string;
  name: string;
  filename: string;
  modality: 'Optical' | 'SAR' | 'Temporal Pair' | 'Multi-modal';
  dimensions: string;
  location: string;
  description: string;
  supportedTasks: TaskMode[];
  badge: string;
  isProxy?: boolean;
  querySuggestion: string;
}

const SCENE_CATALOG: SceneAsset[] = [
  {
    id: 'scene-port-rgb',
    name: 'PORT_SANTOS_BASE_T1',
    filename: 'sample_satellite_port.jpg',
    modality: 'Optical',
    dimensions: '512 × 512 · RGB',
    location: 'Santos, São Paulo, Brazil',
    description: 'Optical multispectral raster capturing deepwater container terminal berths and maritime vessel traffic.',
    supportedTasks: ['VQA', 'GROUNDING', 'CHANGE_DETECTION', 'OPTICAL_SAR'],
    badge: 'OPTICAL',
    querySuggestion: 'What type of maritime port or facility is shown in this satellite image?',
  },
  {
    id: 'scene-port-t2',
    name: 'PORT_SANTOS_TEMPORAL_T2',
    filename: 'sample_satellite_port_t2_synthetic.jpg',
    modality: 'Temporal Pair',
    dimensions: '512 × 512 · RGB',
    location: 'Controlled Synthetic Pair',
    description: 'Co-registered temporal counterpart simulating 2.5% area change (vessel transit and dock variations).',
    supportedTasks: ['CHANGE_DETECTION'],
    badge: 'SYNTHETIC T2',
    querySuggestion: 'Identify differences and what changed between these two images',
  },
  {
    id: 'scene-port-proxy-sar',
    name: 'PORT_SANTOS_PROXY_SAR',
    filename: 'sample_satellite_port_proxy_sar.png',
    modality: 'SAR',
    dimensions: '512 × 512 · C-BAND VV',
    location: 'Santos Estuary (Simulated)',
    description: 'High-frequency microwave roughness proxy simulating metallic dihedral reflection on coastal infrastructure.',
    supportedTasks: ['OPTICAL_SAR'],
    badge: 'PROXY SAR',
    isProxy: true,
    querySuggestion: 'Analyze optical and SAR radar cross-modal backscatter imagery',
  },
  {
    id: 'scene-sentinel1-sar',
    name: 'SENTINEL1_MAURITIUS_COAST',
    filename: 'sample_sentinel1_sar_mauritius.jpg',
    modality: 'SAR',
    dimensions: '512 × 512 · C-BAND SAR',
    location: 'Port Louis Coastal Shelf, Mauritius',
    description: 'Spaceborne Sentinel-1 C-band synthetic aperture radar backscatter capturing coastal maritime boundaries.',
    supportedTasks: ['OPTICAL_SAR'],
    badge: 'SPACEBORNE SAR',
    querySuggestion: 'Analyze optical and SAR radar cross-modal backscatter imagery',
  },
];

export const SceneExplorerPage: React.FC = () => {
  const { navigate } = useRouter();
  const { loadPreset, setTaskMode } = useAnalysis();
  const [filterModality, setFilterModality] = useState<string>('ALL');

  const filtered = SCENE_CATALOG.filter((s) => {
    if (filterModality === 'ALL') return true;
    return s.modality === filterModality;
  });

  const handleOpenScene = async (scene: SceneAsset) => {
    const targetMode = scene.supportedTasks[0] || 'VQA';
    setTaskMode(targetMode);

    if (targetMode === 'CHANGE_DETECTION') {
      await loadPreset({
        mode: 'CHANGE_DETECTION',
        query: scene.querySuggestion,
        primaryAsset: 'sample_satellite_port.jpg',
        secondAsset: 'sample_satellite_port_t2_synthetic.jpg',
      });
    } else if (targetMode === 'OPTICAL_SAR') {
      await loadPreset({
        mode: 'OPTICAL_SAR',
        query: scene.querySuggestion,
        primaryAsset: 'sample_satellite_port.jpg',
        sarAsset: scene.filename.includes('sar') ? scene.filename : 'sample_sentinel1_sar_mauritius.jpg',
      });
    } else {
      await loadPreset({
        mode: targetMode,
        query: scene.querySuggestion,
        primaryAsset: scene.filename,
      });
    }

    navigate('/analyze');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', maxWidth: '1280px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>SCENE EXPLORER</h2>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Curated remote sensing raster assets available for inspection, grounding, and temporal differencing.
          </span>
        </div>

        {/* Filter Segmented Controls */}
        <div style={{ display: 'flex', gap: '4px', background: 'var(--surface-primary)', padding: '3px', borderRadius: 'var(--radius-control)', border: '1px solid var(--border-default)' }}>
          {['ALL', 'Optical', 'SAR', 'Temporal Pair'].map((mod) => (
            <button
              key={mod}
              type="button"
              className={`task-segment-btn ${filterModality === mod ? 'active' : ''}`}
              onClick={() => setFilterModality(mod)}
              style={{ fontSize: '0.72rem', padding: '4px 8px' }}
            >
              {mod}
            </button>
          ))}
        </div>
      </div>

      {/* Gallery Grid */}
      <div className="scene-gallery-grid">
        {filtered.map((scene) => (
          <div key={scene.id} className="scene-card-technical">
            <div className="scene-card-img-wrap">
              <img src={`/samples/${scene.filename}`} alt={scene.name} />
              <span style={{
                position: 'absolute',
                top: 8,
                left: 8,
                fontSize: '0.62rem',
                fontFamily: 'var(--font-mono)',
                fontWeight: 700,
                background: 'rgba(8, 11, 13, 0.85)',
                color: scene.isProxy ? 'var(--color-warning)' : 'var(--accent-teal)',
                border: `1px solid ${scene.isProxy ? 'var(--color-warning)' : 'var(--border-default)'}`,
                padding: '2px 5px',
                borderRadius: '2px',
              }}>
                {scene.badge}
              </span>
            </div>

            <div className="scene-card-body">
              <div className="scene-title-technical">{scene.name}</div>
              <div className="scene-meta-strip">{scene.dimensions} · {scene.location}</div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                {scene.description}
              </p>

              <button
                type="button"
                className="btn-primary"
                style={{ width: '100%', marginTop: 'var(--space-2)', fontSize: '0.76rem', padding: '6px' }}
                onClick={() => handleOpenScene(scene)}
              >
                LOAD IN WORKSPACE →
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
