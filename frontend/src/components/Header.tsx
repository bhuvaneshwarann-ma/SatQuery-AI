import React from 'react';

export const Header: React.FC = () => {
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
    </header>
  );
};

