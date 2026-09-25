import React from 'react';
import { useRouter, type RoutePath } from '../../context/RouterContext';
import {
  IconOverview,
  IconAnalyze,
  IconResults,
  IconHistory,
  IconScenes,
  IconModels,
  IconEvaluation,
  IconArchitecture,
} from '../common/Icons';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

interface NavItem {
  path: RoutePath;
  label: string;
  icon: React.ReactNode;
  badge?: string;
}

interface NavGroup {
  group: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    group: 'WORKSPACE',
    items: [
      { path: '/', label: 'Overview', icon: <IconOverview /> },
      { path: '/analyze', label: 'Analyze', icon: <IconAnalyze /> },
      { path: '/results', label: 'Results', icon: <IconResults /> },
      { path: '/scenes', label: 'Scenes', icon: <IconScenes /> },
      { path: '/history', label: 'History', icon: <IconHistory /> },
    ],
  },
  {
    group: 'INTELLIGENCE',
    items: [
      { path: '/models', label: 'Models', icon: <IconModels /> },
      { path: '/evaluation', label: 'Evaluation', icon: <IconEvaluation />, badge: 'N=20' },
    ],
  },
  {
    group: 'SYSTEM',
    items: [
      { path: '/about', label: 'Architecture', icon: <IconArchitecture /> },
    ],
  },
];

export const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  onToggleCollapse,
  mobileOpen,
  onCloseMobile,
}) => {
  const { currentPath, navigate } = useRouter();

  const handleNavClick = (path: RoutePath) => {
    navigate(path);
    onCloseMobile();
  };

  return (
    <>
      {mobileOpen && (
        <div className="sidebar-mobile-backdrop" onClick={onCloseMobile} />
      )}

      <aside
        className={`app-sidebar ${collapsed ? 'sidebar-collapsed' : ''} ${
          mobileOpen ? 'sidebar-mobile-open' : ''
        }`}
      >
        <div className="sidebar-header">
          <div className="sidebar-brand" onClick={() => handleNavClick('/')}>
            <span className="brand-dot" />
            {!collapsed && <span className="brand-name">SATQUERY AI</span>}
          </div>
          <button
            type="button"
            className="sidebar-collapse-btn"
            onClick={onToggleCollapse}
            title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            aria-label="Toggle Sidebar"
          >
            {collapsed ? '›' : '‹'}
          </button>
        </div>

        <nav className="sidebar-nav">
          {NAV_GROUPS.map((group) => (
            <div key={group.group} className="sidebar-nav-group">
              {!collapsed && (
                <div className="sidebar-group-heading">{group.group}</div>
              )}
              <ul className="sidebar-nav-list">
                {group.items.map((item) => {
                  const isActive = currentPath === item.path;
                  return (
                    <li key={item.path}>
                      <button
                        type="button"
                        className={`sidebar-nav-btn ${isActive ? 'nav-btn-active' : ''}`}
                        onClick={() => handleNavClick(item.path)}
                        title={collapsed ? item.label : undefined}
                      >
                        <span className="nav-item-icon">{item.icon}</span>
                        {!collapsed && <span className="nav-item-label">{item.label}</span>}
                        {!collapsed && item.badge && (
                          <span className="nav-item-badge">{item.badge}</span>
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          {!collapsed ? (
            <div className="sidebar-footer-text">
              <span className="system-status-indicator" />
              <span>Engine Active · Port Santos</span>
            </div>
          ) : (
            <div className="sidebar-footer-collapsed" title="Engine Active">
              <span className="system-status-indicator" />
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
