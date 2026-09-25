import React from 'react';
import { useRouter, type RoutePath } from '../../context/RouterContext';
import { IconSearch } from '../common/Icons';

interface TopNavProps {
  onOpenMobileSidebar: () => void;
  onOpenCommandPalette: () => void;
}

const ROUTE_LABELS: Record<RoutePath, { section: string; title: string }> = {
  '/': { section: 'Overview', title: 'Workstation' },
  '/analyze': { section: 'Workspace', title: 'Analysis' },
  '/results': { section: 'Analysis', title: 'Report & Evidence' },
  '/history': { section: 'Audit', title: 'History' },
  '/scenes': { section: 'Catalog', title: 'Scene Explorer' },
  '/models': { section: 'Registry', title: 'AI Models' },
  '/evaluation': { section: 'Benchmarks', title: 'Evaluation (N=20)' },
  '/about': { section: 'System', title: 'Architecture' },
};

export const TopNav: React.FC<TopNavProps> = ({
  onOpenMobileSidebar,
  onOpenCommandPalette,
}) => {
  const { currentPath, navigate } = useRouter();
  const routeInfo = ROUTE_LABELS[currentPath] || { section: 'Workspace', title: 'SatQuery AI' };

  return (
    <header className="app-top-nav">
      <div className="top-nav-left">
        <button
          type="button"
          className="mobile-menu-btn"
          onClick={onOpenMobileSidebar}
          aria-label="Open Navigation"
        >
          ☰
        </button>

        <div className="top-nav-breadcrumbs">
          <span className="crumb-section">{routeInfo.section}</span>
          <span className="crumb-separator">/</span>
          <span className="crumb-title">{routeInfo.title}</span>
        </div>
      </div>

      <div className="top-nav-right">
        {/* Search Trigger */}
        <button
          type="button"
          className="search-shortcut-btn"
          onClick={onOpenCommandPalette}
          title="Search tools, scenes, models (Ctrl+K)"
        >
          <IconSearch size={14} />
          <span>Search</span>
          <kbd className="search-kbd">Ctrl K</kbd>
        </button>

        {/* Primary Action Button */}
        {currentPath !== '/analyze' && (
          <button
            type="button"
            className="top-nav-action-btn"
            onClick={() => navigate('/analyze')}
          >
            New Analysis
          </button>
        )}
      </div>
    </header>
  );
};
