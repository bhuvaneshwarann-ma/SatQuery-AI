import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

export type RoutePath =
  | '/'
  | '/analyze'
  | '/results'
  | '/history'
  | '/scenes'
  | '/models'
  | '/evaluation'
  | '/about';

interface RouterContextType {
  currentPath: RoutePath;
  navigate: (path: RoutePath, state?: Record<string, any>) => void;
  routeState: Record<string, any> | null;
}

const RouterContext = createContext<RouterContextType | null>(null);

function normalizePath(rawPath: string): RoutePath {
  // Support hash routing or standard path routing gracefully
  let p = rawPath;
  if (p.startsWith('#')) {
    p = p.slice(1);
  }
  const clean = p.split('?')[0].split('#')[0] || '/';
  const validPaths: RoutePath[] = [
    '/',
    '/analyze',
    '/results',
    '/history',
    '/scenes',
    '/models',
    '/evaluation',
    '/about',
  ];
  return validPaths.includes(clean as RoutePath) ? (clean as RoutePath) : '/';
}

export const RouterProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentPath, setCurrentPath] = useState<RoutePath>(() => {
    // Check hash first (useful for static preview servers), else pathname
    if (window.location.hash) {
      return normalizePath(window.location.hash);
    }
    return normalizePath(window.location.pathname);
  });

  const [routeState, setRouteState] = useState<Record<string, any> | null>(() => {
    return window.history.state || null;
  });

  useEffect(() => {
    const handlePopState = (event: PopStateEvent) => {
      const path = window.location.hash
        ? normalizePath(window.location.hash)
        : normalizePath(window.location.pathname);
      setCurrentPath(path);
      setRouteState(event.state || null);
    };

    window.addEventListener('popstate', handlePopState);
    window.addEventListener('hashchange', () => {
      if (window.location.hash) {
        setCurrentPath(normalizePath(window.location.hash));
      }
    });

    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

  const navigate = useCallback((path: RoutePath, state?: Record<string, any>) => {
    const target = normalizePath(path);
    setCurrentPath(target);
    setRouteState(state || null);

    // Update window URL without reload
    try {
      window.history.pushState(state || {}, '', target);
    } catch {
      // Fallback to hash if pathname manipulation fails
      window.location.hash = target;
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  return (
    <RouterContext.Provider value={{ currentPath, navigate, routeState }}>
      {children}
    </RouterContext.Provider>
  );
};

export function useRouter(): RouterContextType {
  const ctx = useContext(RouterContext);
  if (!ctx) {
    throw new Error('useRouter must be used within a RouterProvider');
  }
  return ctx;
}
