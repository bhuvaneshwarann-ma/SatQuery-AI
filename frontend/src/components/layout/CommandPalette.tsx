import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from '../../context/RouterContext';
import { useAnalysis } from '../../context/AnalysisContext';
import { IconSearch } from '../common/Icons';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

interface CommandItem {
  id: string;
  category: 'NAVIGATION' | 'ANALYSIS_MODE' | 'INTELLIGENCE' | 'SCENES';
  title: string;
  subtitle: string;
  action: () => void;
  keywords: string[];
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const { navigate } = useRouter();
  const { setTaskMode } = useAnalysis();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const commands: CommandItem[] = [
    {
      id: 'nav-home',
      category: 'NAVIGATION',
      title: 'Workstation Overview',
      subtitle: 'Platform overview, capabilities, and system flow',
      action: () => { navigate('/'); onClose(); },
      keywords: ['home', 'overview', 'landing', 'start', 'dashboard'],
    },
    {
      id: 'task-vqa',
      category: 'ANALYSIS_MODE',
      title: 'VQA (Visual Question Answering)',
      subtitle: 'Ask natural language questions about satellite imagery via AdaptLLM',
      action: () => { setTaskMode('VQA'); navigate('/analyze'); onClose(); },
      keywords: ['vqa', 'question', 'qwen', 'reasoning', 'natural language', 'vlm'],
    },
    {
      id: 'task-grounding',
      category: 'ANALYSIS_MODE',
      title: 'Visual Grounding',
      subtitle: 'Locate queried objects spatially with bounding boxes via Grounding DINO',
      action: () => { setTaskMode('GROUNDING'); navigate('/analyze'); onClose(); },
      keywords: ['grounding', 'dino', 'bbox', 'localize', 'detect', 'ships', 'buildings'],
    },
    {
      id: 'task-change',
      category: 'ANALYSIS_MODE',
      title: 'Change Detection',
      subtitle: 'Bi-temporal differential change comparison via Siamese ResNet-18',
      action: () => { setTaskMode('CHANGE_DETECTION'); navigate('/analyze'); onClose(); },
      keywords: ['change', 'temporal', 'difference', 'siamese', 'resnet', 'bitemporal', 't1', 't2'],
    },
    {
      id: 'task-sar',
      category: 'ANALYSIS_MODE',
      title: 'Optical + SAR Fusion',
      subtitle: 'Analyze complementary optical & microwave SAR radar backscatter',
      action: () => { setTaskMode('OPTICAL_SAR'); navigate('/analyze'); onClose(); },
      keywords: ['sar', 'radar', 'optical', 'sentinel', 'backscatter', 'cross modal', 'proxy sar'],
    },
    {
      id: 'nav-history',
      category: 'NAVIGATION',
      title: 'Audit History',
      subtitle: 'Review previously completed queries and uncalibrated confidence scores',
      action: () => { navigate('/history'); onClose(); },
      keywords: ['history', 'past', 'saved', 'previous', 'records', 'results'],
    },
    {
      id: 'nav-scenes',
      category: 'SCENES',
      title: 'Scene Explorer',
      subtitle: 'Explore sample satellite scenes (Port Santos, Sentinel-1 SAR)',
      action: () => { navigate('/scenes'); onClose(); },
      keywords: ['scenes', 'samples', 'port', 'satellite', 'images', 'assets', 'explorer'],
    },
    {
      id: 'nav-models',
      category: 'INTELLIGENCE',
      title: 'AI Models & Engines',
      subtitle: 'Inspect Remote Sensing Qwen2.5, Grounding DINO, and Siamese ResNet',
      action: () => { navigate('/models'); onClose(); },
      keywords: ['models', 'vlm', 'dino', 'engines', 'qwen', 'neural', 'weights'],
    },
    {
      id: 'nav-evaluation',
      category: 'INTELLIGENCE',
      title: 'Evaluation & Benchmarks',
      subtitle: 'RSVQA-LR & LEVIR-CD N=20 baselines, latency telemetry, honest limitations',
      action: () => { navigate('/evaluation'); onClose(); },
      keywords: ['evaluation', 'benchmark', 'metrics', 'accuracy', 'rsvqa', 'levir', 'performance'],
    },
    {
      id: 'nav-about',
      category: 'NAVIGATION',
      title: 'Architecture & System',
      subtitle: 'Agentic router, allowlisted tools, parameter firewall, and security',
      action: () => { navigate('/about'); onClose(); },
      keywords: ['about', 'architecture', 'system', 'router', 'firewall', 'agent', 'safety'],
    },
  ];

  const filtered = commands.filter((cmd) => {
    if (!query.trim()) return true;
    const q = query.toLowerCase();
    return (
      cmd.title.toLowerCase().includes(q) ||
      cmd.subtitle.toLowerCase().includes(q) ||
      cmd.keywords.some((k) => k.includes(q))
    );
  });

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % (filtered.length || 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + filtered.length) % (filtered.length || 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered[selectedIndex]) {
        filtered[selectedIndex].action();
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="command-palette-backdrop" onClick={onClose}>
      <div
        className="command-palette-modal"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        <div className="palette-search-header">
          <IconSearch size={16} />
          <input
            ref={inputRef}
            type="text"
            className="palette-search-input"
            placeholder="Search commands, destinations, tools..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <kbd className="palette-esc-kbd" onClick={onClose}>ESC</kbd>
        </div>

        <div className="palette-results-list">
          {filtered.length === 0 ? (
            <div className="palette-empty-state">
              <span>No matching command found for "{query}"</span>
            </div>
          ) : (
            filtered.map((cmd, idx) => (
              <div
                key={cmd.id}
                className={`palette-item ${idx === selectedIndex ? 'palette-item-selected' : ''}`}
                onClick={cmd.action}
                onMouseEnter={() => setSelectedIndex(idx)}
              >
                <div className="palette-item-content">
                  <div className="palette-item-title-row">
                    <span className="palette-item-title">{cmd.title}</span>
                    <span className="palette-item-category">{cmd.category}</span>
                  </div>
                  <span className="palette-item-subtitle">{cmd.subtitle}</span>
                </div>
                <span className="palette-enter-hint">↵</span>
              </div>
            ))
          )}
        </div>

        <div className="palette-footer">
          <span>Navigate <kbd>↑</kbd> <kbd>↓</kbd> · Select <kbd>↵</kbd></span>
          <span>SatQuery AI</span>
        </div>
      </div>
    </div>
  );
};
