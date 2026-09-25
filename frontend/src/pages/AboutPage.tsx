import React, { useState } from 'react';
import { IconShield, IconTerminal, IconInfo, IconChevronRight } from '../components/common/Icons';

interface ArchNode {
  id: string;
  stageNum: string;
  title: string;
  subtitle: string;
  role: string;
  securityGuarantee: string;
}

const ARCH_NODES: ArchNode[] = [
  {
    id: 'node-client',
    stageNum: '01',
    title: 'Client Web Workstation',
    subtitle: 'React 19 + TypeScript SPA',
    role: 'Provides multi-page geospatial navigation, drag-and-drop ingestion, pan/zoom overlays, and side-by-side temporal inspection.',
    securityGuarantee: 'Client-side raster integrity validation and zero tracking telemetry.',
  },
  {
    id: 'node-fastapi',
    stageNum: '02',
    title: 'FastAPI Service Gateway',
    subtitle: 'Uvicorn ASGI Server (:8000)',
    role: 'Exposes strictly typed REST endpoints (/api/analyze, /api/health, /api/tools, /api/artifacts).',
    securityGuarantee: 'Strict Pydantic payload models, 25MB upload ceiling, and CORS boundary controls.',
  },
  {
    id: 'node-validator',
    stageNum: '03',
    title: 'Pre-Execution Input Validator',
    subtitle: 'Integrity & Contract Auditor',
    role: 'Validates presence of required raster assets (e.g. T2 for Change, SAR for Dual-Stream) before GPU invocation.',
    securityGuarantee: 'Catches missing or corrupted inputs in <5ms without activating heavy GPU model weights.',
  },
  {
    id: 'node-router',
    stageNum: '04',
    title: 'Agentic Tool Router',
    subtitle: 'Deterministic Semantic Dispatcher',
    role: 'Classifies analytical intent and routes queries to allowlisted specialist tools with parameter firewalling.',
    securityGuarantee: 'Rejects prompt-injection attacks and unknown tools (NEEDS_CLARIFICATION / UNREGISTERED_TOOL).',
  },
  {
    id: 'node-tools',
    stageNum: '05',
    title: 'Specialist Analytical Engines',
    subtitle: 'VLM / Grounding / Siamese / SAR',
    role: 'Executes AdaptLLM Qwen2.5-VL-3B, Grounding DINO, Siamese ResNet-18, or Dual-Stream engine on CUDA.',
    securityGuarantee: 'Isolated tool executions; parameters filtered strictly against allowlisted registry.',
  },
  {
    id: 'node-evidence',
    stageNum: '06',
    title: 'Visual Evidence Extractor',
    subtitle: 'Spatial & Matrix Grounding',
    role: 'Generates bounding box coordinates, differential heatmaps, and cross-modal Pearson correlation matrices.',
    securityGuarantee: 'All claims cross-referenced with observable tensor signals; zero speculative hallucinations.',
  },
  {
    id: 'node-confidence',
    stageNum: '07',
    title: 'Evidence Strength Heuristic',
    subtitle: '5-Signal Uncalibrated Engine',
    role: 'Evaluates evidence availability, answer consistency, query specificity, visual sufficiency, and hedge factor.',
    securityGuarantee: 'Hard uncertainty ceilings (max MEDIUM on ambiguity, max LOW on contradiction).',
  },
  {
    id: 'node-result',
    stageNum: '08',
    title: 'Observable Trace & Payload Composition',
    subtitle: 'Audit Log & API Payload',
    role: 'Packages final answer, scene description, dynamic evidence cards, and 6-stage operational audit trace.',
    securityGuarantee: 'Strictly ZERO ungrounded chain-of-thought tokens or reasoning traces leaked to caller.',
  },
];

export const AboutPage: React.FC = () => {
  const [activeNode, setActiveNode] = useState<ArchNode>(ARCH_NODES[3]); // default to Router

  return (
    <div className="about-page-container">
      {/* Header */}
      <div className="about-header">
        <div>
          <h2 className="page-title">System Architecture &amp; Agentic Security</h2>
          <p className="page-subtitle">
            Controlled allowlisted tool execution, parameter firewalls, and observable operational audit traces in SatQuery AI.
          </p>
        </div>

        <div className="about-badge">
          <span className="font-mono text-xs text-accent">ZERO-COT AUDITED PIPELINE</span>
        </div>
      </div>

      {/* Interactive Pipeline Architecture Flow */}
      <div className="arch-interactive-section">
        <div className="flex items-center justify-between mb-2">
          <h3 className="arch-section-title">End-to-End Execution Pipeline Architecture</h3>
          <span className="text-xs text-muted font-mono">CLICK STAGE TO INSPECT ROLE &amp; CONTRACTS</span>
        </div>
        <p className="arch-section-sub">
          Every query flows sequentially through an 8-stage audited pipeline with rigorous pre-validation, semantic dispatching, parameter firewalls, and visual evidence extraction.
        </p>

        <div className="arch-diagram-flow">
          {ARCH_NODES.map((node, idx) => {
            const isSelected = activeNode.id === node.id;
            return (
              <React.Fragment key={node.id}>
                <div
                  className={`arch-node-box ${isSelected ? 'arch-node-selected' : ''}`}
                  onClick={() => setActiveNode(node)}
                >
                  <div className="node-num-tag">{node.stageNum}</div>
                  <h4 className="node-title">{node.title}</h4>
                  <span className="node-sub">{node.subtitle}</span>
                </div>
                {idx < ARCH_NODES.length - 1 && (
                  <div className="arch-node-arrow">
                    <IconChevronRight size={14} />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Selected Node Details Panel */}
        {activeNode && (
          <div className="active-node-inspector-card">
            <div className="inspector-header">
              <div className="flex items-center gap-2">
                <span className="geo-badge">STAGE {activeNode.stageNum}</span>
                <h4 className="inspector-title">{activeNode.title}</h4>
                <span className="text-xs text-muted font-mono">({activeNode.subtitle})</span>
              </div>
            </div>

            <div className="inspector-grid">
              <div className="inspector-col">
                <span className="col-label">OPERATIONAL ROLE</span>
                <p className="col-text">{activeNode.role}</p>
              </div>

              <div className="inspector-col col-security">
                <div className="flex items-center gap-1 mb-1">
                  <IconShield size={14} className="text-accent" />
                  <span className="col-label text-accent">SECURITY &amp; INTEGRITY GUARANTEE</span>
                </div>
                <p className="col-text">{activeNode.securityGuarantee}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Agentic Execution Principles */}
      <div className="agentic-philosophy-section">
        <h3 className="arch-section-title">Core Principles of Controlled Agentic Execution</h3>
        <p className="arch-section-sub">
          Mission-critical remote sensing demands verifiable safety boundaries, not unconstrained autonomous tool hallucination.
        </p>

        <div className="principles-grid">
          <div className="principle-card">
            <div className="principle-card-header">
              <IconShield size={16} className="text-accent" />
              <h4 className="principle-title">Allowlisted Tool Execution</h4>
            </div>
            <p className="principle-desc">
              SatQuery AI never allows an agent to execute arbitrary shell commands, load unvetted packages, or generate unverified code. Every execution path resolves strictly to one of four pre-registered specialist analytical engines.
            </p>
          </div>

          <div className="principle-card">
            <div className="principle-card-header">
              <IconShield size={16} className="text-accent" />
              <h4 className="principle-title">Parameter Firewall Enforcement</h4>
            </div>
            <p className="principle-desc">
              All user-supplied and router-derived parameters are validated against strict per-tool schemas. Unrecognized, missing, or out-of-range parameters are intercepted in &lt;20ms before any GPU tensor allocations occur.
            </p>
          </div>

          <div className="principle-card">
            <div className="principle-card-header">
              <IconTerminal size={16} className="text-accent" />
              <h4 className="principle-title">Observable Trace (Zero CoT)</h4>
            </div>
            <p className="principle-desc">
              Unlike systems that leak stochastic chain-of-thought tokens, SatQuery AI logs verifiable operational events: validated inputs, selected tools, authorized arguments, tensor latencies, and output artifacts.
            </p>
          </div>

          <div className="principle-card">
            <div className="principle-card-header">
              <IconInfo size={16} className="text-accent" />
              <h4 className="principle-title">Scientific Rigor &amp; Disclosures</h4>
            </div>
            <p className="principle-desc">
              Confidence levels are communicated as uncalibrated evidence strength heuristics. Baseline numbers are explicitly marked (<em>N=20</em>), radar proxies are stamped, and open roadmap milestones are displayed openly.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
