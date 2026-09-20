import { useState } from 'react';
import type {
  AnalysisApiResponse,
  AnalyzePayload,
} from './api/client';
import { analyzeRequest } from './api/client';
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
    }
  };

  return (
    <div className="satquery-app">
      <Header />

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
        <span>SatQuery AI · Production MVP · AdaptLLM Qwen2.5-VL-3B · Grounding DINO · Siamese ResNet18</span>
      </footer>
    </div>
  );
}

export default App;
