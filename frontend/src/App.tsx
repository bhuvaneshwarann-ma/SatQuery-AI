import React from 'react';
import { RouterProvider, useRouter } from './context/RouterContext';
import { ToastProvider } from './context/ToastContext';
import { HistoryProvider } from './context/HistoryContext';
import { AnalysisProvider } from './context/AnalysisContext';
import { AppShell } from './components/layout/AppShell';

import { HomePage } from './pages/HomePage';
import { AnalysisPage } from './pages/AnalysisPage';
import { ResultsPage } from './pages/ResultsPage';
import { HistoryPage } from './pages/HistoryPage';
import { SceneExplorerPage } from './pages/SceneExplorerPage';
import { ModelsPage } from './pages/ModelsPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { AboutPage } from './pages/AboutPage';

const PageOutlet: React.FC = () => {
  const { currentPath } = useRouter();

  switch (currentPath) {
    case '/':
      return <HomePage />;
    case '/analyze':
      return <AnalysisPage />;
    case '/results':
      return <ResultsPage />;
    case '/history':
      return <HistoryPage />;
    case '/scenes':
      return <SceneExplorerPage />;
    case '/models':
      return <ModelsPage />;
    case '/evaluation':
      return <EvaluationPage />;
    case '/about':
      return <AboutPage />;
    default:
      return <HomePage />;
  }
};

export function App() {
  return (
    <RouterProvider>
      <ToastProvider>
        <HistoryProvider>
          <AnalysisProvider>
            <AppShell>
              <PageOutlet />
            </AppShell>
          </AnalysisProvider>
        </HistoryProvider>
      </ToastProvider>
    </RouterProvider>
  );
}

export default App;
