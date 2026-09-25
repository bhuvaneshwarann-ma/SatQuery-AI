import React from 'react';
import type { OperationalStage } from '../../context/AnalysisContext';

interface LiveAnalysisStagesProps {
  activeStage: OperationalStage;
  elapsedSeconds: number;
  selectedTool?: string | null;
  model?: string | null;
}

interface StageItem {
  key: OperationalStage;
  code: string;
  label: string;
}

const STAGES: StageItem[] = [
  { key: 'INPUT_VALIDATION', code: '01', label: 'INPUT VALIDATION' },
  { key: 'ROUTER', code: '02', label: 'AGENT ROUTER' },
  { key: 'TOOL_SELECTED', code: '03', label: 'TOOL SELECTION & FIREWALL' },
  { key: 'TOOL_EXECUTION', code: '04', label: 'ENGINE EXECUTION' },
  { key: 'EVIDENCE', code: '05', label: 'EVIDENCE EXTRACTION' },
  { key: 'CONFIDENCE', code: '06', label: 'CONFIDENCE HEURISTIC' },
  { key: 'RESULT', code: '07', label: 'RESULT PACKAGING' },
];

export const LiveAnalysisStages: React.FC<LiveAnalysisStagesProps> = ({
  activeStage,
  elapsedSeconds,
  selectedTool,
}) => {
  const getStageStatus = (stageKey: OperationalStage) => {
    const order: OperationalStage[] = [
      'INPUT_VALIDATION',
      'ROUTER',
      'TOOL_SELECTED',
      'TOOL_EXECUTION',
      'EVIDENCE',
      'CONFIDENCE',
      'RESULT',
    ];
    const currentIndex = order.indexOf(activeStage);
    const thisIndex = order.indexOf(stageKey);

    if (thisIndex < currentIndex) return 'done';
    if (thisIndex === currentIndex) return 'active';
    return 'wait';
  };

  return (
    <div className="operational-pipeline-log">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
        <span style={{ fontSize: '0.72rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
          PIPELINE AUDIT
        </span>
        <span style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: 'var(--color-warning)' }}>
          {elapsedSeconds.toFixed(1)}s
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
        {STAGES.map((s) => {
          const status = getStageStatus(s.key);
          return (
            <div key={s.key} className="pipeline-step-item">
              <span className="step-label-mono">
                {s.code} {s.label}
              </span>
              <span className={`step-status-chip status-chip-${status}`}>
                {status === 'done' ? '✓ OK' : status === 'active' ? '● RUNNING' : 'WAIT'}
              </span>
            </div>
          );
        })}
      </div>

      {selectedTool && (
        <div style={{ paddingTop: '4px', borderTop: '1px solid var(--border-subtle)', fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          TARGET: {selectedTool}
        </div>
      )}
    </div>
  );
};
