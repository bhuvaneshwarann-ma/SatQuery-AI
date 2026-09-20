import React from 'react';
import type { HealthResponse } from '../api/client';

interface HeaderProps {
  health: HealthResponse | null;
  healthError: string | null;
  loadingHealth: boolean;
}

export const Header: React.FC<HeaderProps> = ({ health, healthError, loadingHealth }) => {
  const isHealthy = health && health.status === 'healthy' && !healthError;

  return (
    <header className="header-container">
      <div className="header-branding">
        <div className="brand-logo-badge">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="satellite-icon">
            <path d="m2 10 4 4" />
            <path d="m17 22 4-4" />
            <path d="M7 14.5a3.5 3.5 0 0 0 5-5" />
            <path d="M12 9.5a3.5 3.5 0 0 0 5-5" />
            <path d="m14 17 5 5" />
            <path d="m3 6 5 5" />
            <path d="M6.5 12.5 11 8" />
            <path d="m11.5 17.5 4.5-4.5" />
          </svg>
          <span className="brand-title">SatQuery AI</span>
        </div>
        <p className="brand-subtitle">
          Agentic Multi-Modal Remote Sensing &amp; Satellite Visual QA System
        </p>
      </div>

      <div className="header-telemetry-pill">
        <div className="telemetry-header">
          <span className={`status-indicator-dot ${isHealthy ? 'status-online' : 'status-offline'}`} />
          <span className="telemetry-label">Live System Status</span>
          {loadingHealth && <span className="telemetry-refreshing">●</span>}
        </div>

        {isHealthy ? (
          <div className="telemetry-details">
            <span className="telemetry-item" title={health.gpu_name}>
              <strong>GPU:</strong> {health.gpu_name.replace('NVIDIA GeForce ', '').replace(' Laptop GPU', '')}
            </span>
            <span className="telemetry-separator">|</span>
            <span className="telemetry-item">
              <strong>VRAM:</strong> {Math.round(health.free_vram_mb)} / {Math.round(health.total_vram_mb)} MB
            </span>
            <span className="telemetry-separator">|</span>
            <span className="telemetry-item">
              <strong>Tools:</strong> {health.registered_tools.length} active
            </span>
          </div>
        ) : (
          <div className="telemetry-details telemetry-error">
            <span>{healthError ? 'Backend Offline' : 'Connecting to API...'}</span>
          </div>
        )}
      </div>
    </header>
  );
};
