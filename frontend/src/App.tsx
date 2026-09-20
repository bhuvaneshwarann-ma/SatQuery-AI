import { useState, useEffect, useCallback } from 'react';
import type {
  HealthResponse,
  AnalysisApiResponse,
  AnalyzePayload,
} from './api/client';
import { fetchHealth, analyzeRequest } from './api/client';
import { Header } from './components/Header';
import { AnalysisForm } from './components/AnalysisForm';
import { ResultView } from './components/ResultView';
import { ErrorBanner } from './components/ErrorBanner';

interface ActiveError {
  status?: string | null;
  errorType?: string | null;
  message: string;
  clarificationPrompt?: string | null;
  validationErrors?: string[];
}

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(false);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisApiResponse | null>(null);
  const [error, setError] = useState<ActiveError | null>(null);

  const [submittedQuery, setSubmittedQuery] = useState<string>('');
  const [submittedPreviews, setSubmittedPreviews] = useState<{
    primary: string | null;
    second: string | null;
    sar: string | null;
  }>({
    primary: null,
    second: null,
    sar: null,
  });

  // Poll health telemetry
  const loadHealth = useCallback(async () => {
    try {
      setLoadingHealth(true);
      const data = await fetchHealth();
      setHealth(data);
      setHealthError(null);
    } catch (err: any) {
      setHealth(null);
      setHealthError(err?.message || 'Failed to connect to SatQuery AI backend.');
    } finally {
      setLoadingHealth(false);
    }
  }, []);

  useEffect(() => {
    loadHealth();
    const interval = setInterval(loadHealth, 12000);
    return () => clearInterval(interval);
  }, [loadHealth]);

  const handleAnalyze = async (
    payload: AnalyzePayload,
    previews: { primary: string | null; second: string | null; sar: string | null }
  ) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setSubmittedQuery(payload.query);
    setSubmittedPreviews(previews);

    try {
      const apiResult = await analyzeRequest(payload);

      // Check if backend returned non-success or needs clarification
      if (apiResult.status === 'NEEDS_CLARIFICATION') {
        setError({
          status: apiResult.status,
          errorType: apiResult.error_type || 'NEEDS_CLARIFICATION',
          message: apiResult.answer,
          clarificationPrompt: apiResult.metadata?.clarification_prompt,
        });
        setResult(apiResult);
      } else if (apiResult.status === 'INVALID_INPUT' || apiResult.status === 'ERROR') {
        setError({
          status: apiResult.status,
          errorType: apiResult.error_type,
          message: apiResult.answer,
          validationErrors: apiResult.metadata?.validation_errors,
        });
        setResult(apiResult);
      } else {
        setResult(apiResult);
      }
    } catch (err: any) {
      setError({
        status: 'NETWORK_ERROR',
        errorType: 'API_CONNECTION_ERROR',
        message: err?.message || 'Unable to communicate with SatQuery AI backend at http://127.0.0.1:8000.',
      });
    } finally {
      setLoading(false);
      // Refresh VRAM telemetry after analysis pass
      loadHealth();
    }
  };

  return (
    <div className="satquery-app">
      <Header
        health={health}
        healthError={healthError}
        loadingHealth={loadingHealth}
      />

      <main className="main-content-container">
        {error && (
          <ErrorBanner
            status={error.status}
            errorType={error.errorType}
            message={error.message}
            clarificationPrompt={error.clarificationPrompt}
            validationErrors={error.validationErrors}
            onDismiss={() => setError(null)}
          />
        )}

        <AnalysisForm onAnalyze={handleAnalyze} loading={loading} />

        {result && (
          <ResultView
            result={result}
            query={submittedQuery}
            primaryPreview={submittedPreviews.primary}
            secondPreview={submittedPreviews.second}
            sarPreview={submittedPreviews.sar}
          />
        )}
      </main>

      <footer className="footer-container">
        <span>SatQuery AI · Smart India Hackathon Production MVP · AdaptLLM Qwen2.5-VL-3B · Grounding DINO · Siamese ResNet18</span>
      </footer>
    </div>
  );
}

export default App;
