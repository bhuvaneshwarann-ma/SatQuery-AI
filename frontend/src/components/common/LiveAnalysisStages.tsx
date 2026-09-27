import React from 'react';
import type { OperationalStage } from '../../context/AnalysisContext';
interface Props { activeStage: OperationalStage; elapsedSeconds: number; selectedTool?: string | null; model?: string | null }
export const LiveAnalysisStages: React.FC<Props> = ({ activeStage, elapsedSeconds, selectedTool, model }) => (
  <div className="operational-pipeline-log" role="status" aria-live="polite">
    <div className="pipeline-live-title"><span className="pipeline-spinner" />{activeStage === 'RESULT' ? 'Response received' : activeStage === 'IDLE' ? 'Ready' : `${activeStage.replace(/_/g, ' ')} in progress`}</div>
    <span> · {elapsedSeconds.toFixed(1)}s</span>
    <p>{selectedTool ? `${selectedTool} is coordinating the analysis.` : 'Loading the selected remote-sensing specialist.'} {model ? `Model: ${model}` : 'The model may take a few seconds to load on first use.'}</p>
    <small>Processing continues safely in the background. The completed trace will appear in the report.</small>
  </div>
);
