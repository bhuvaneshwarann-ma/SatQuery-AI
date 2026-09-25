import React from 'react';
import type { TaskMode } from '../../context/AnalysisContext';

interface QueryChipsProps {
  taskMode: TaskMode;
  onSelectQuery: (query: string) => void;
}

const QUERY_SUGGESTIONS: Record<TaskMode, string[]> = {
  AUTO: [
    'Describe the main features of this satellite image.',
    'Locate the ships in this satellite image.',
    'Identify differences and what changed between these two images',
    'Analyze optical and SAR radar cross-modal backscatter imagery',
  ],
  VQA: [
    'Describe this scene',
    'What objects are visible?',
    'What is the dominant land/water pattern?',
    'What infrastructure is visible?',
    'What type of maritime port or facility is shown?',
  ],
  GROUNDING: [
    'Locate ships',
    'Locate buildings',
    'Locate roads',
    'Locate aircraft',
    'Locate dock infrastructure and piers',
  ],
  CHANGE_DETECTION: [
    'Identify differences and what changed between these two images',
    'Detect new construction and infrastructure expansion',
    'Highlight temporal alterations in land cover',
  ],
  OPTICAL_SAR: [
    'Analyze optical and SAR radar cross-modal backscatter imagery',
    'Correlate optical reflectance with radar-dominant surface roughness',
    'Detect high-backscatter anomalies in radar channel',
  ],
};

export const QueryChips: React.FC<QueryChipsProps> = ({ taskMode, onSelectQuery }) => {
  const suggestions = QUERY_SUGGESTIONS[taskMode] || QUERY_SUGGESTIONS.AUTO;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      <span style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.08em', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
        SUGGESTED QUERIES
      </span>
      <div className="chips-list-compact">
        {suggestions.map((suggestion, idx) => (
          <button
            key={idx}
            type="button"
            className="chip-technical"
            onClick={() => onSelectQuery(suggestion)}
            title={`Use query: "${suggestion}"`}
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
};
