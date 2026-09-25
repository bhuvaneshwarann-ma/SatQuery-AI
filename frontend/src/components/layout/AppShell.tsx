import React, { useState, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';
import { CommandPalette } from './CommandPalette';
import { ToastContainer } from './ToastContainer';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);

  // Global Ctrl+K / Cmd+K shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="satquery-app-shell">
      {/* Toast Notifications */}
      <ToastContainer />

      {/* Global Command Palette */}
      <CommandPalette
        isOpen={paletteOpen}
        onClose={() => setPaletteOpen(false)}
      />

      {/* Application Sidebar */}
      <Sidebar
        collapsed={collapsed}
        onToggleCollapse={() => setCollapsed(!collapsed)}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />

      {/* Main Workspace Body */}
      <div className={`shell-main-wrapper ${collapsed ? 'shell-main-expanded' : ''}`}>
        <TopNav
          onOpenMobileSidebar={() => setMobileOpen(true)}
          onOpenCommandPalette={() => setPaletteOpen(true)}
        />

        <main className="shell-page-content">{children}</main>

        <footer className="shell-footer">
          <div className="footer-left">
            <span>SatQuery AI · Agentic Earth Observation Intelligence</span>
            <span className="footer-sep">|</span>
            <span className="footer-citation">
              Remote Sensing Qwen2.5-VL-3B · Grounding DINO · Siamese ResNet-18
            </span>
          </div>
          <div className="footer-right">
            <span className="footer-semantic-notice">Model-derived • Uncalibrated Semantics</span>
          </div>
        </footer>
      </div>
    </div>
  );
};
