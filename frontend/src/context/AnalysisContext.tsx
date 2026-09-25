import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type {
  AnalysisApiResponse,
  AnalyzePayload,
} from '../api/client';
import { analyzeRequest } from '../api/client';
import { useHistory } from './HistoryContext';
import { useToast } from './ToastContext';
import { useRouter } from './RouterContext';

export type TaskMode = 'AUTO' | 'VQA' | 'GROUNDING' | 'CHANGE_DETECTION' | 'OPTICAL_SAR';

export interface ActiveAnalysisState {
  taskMode: TaskMode;
  query: string;
  primaryImage: File | null;
  primaryPreview: string | null;
  secondImage: File | null;
  secondPreview: string | null;
  sarImage: File | null;
  sarPreview: string | null;
  parameters: Record<string, any>;
}

export interface ActiveError {
  status?: string | null;
  errorType?: string | null;
  message: string;
  clarificationPrompt?: string | null;
  validationErrors?: string[];
}

export type OperationalStage =
  | 'IDLE'
  | 'INPUT_VALIDATION'
  | 'ROUTER'
  | 'TOOL_SELECTED'
  | 'TOOL_EXECUTION'
  | 'EVIDENCE'
  | 'CONFIDENCE'
  | 'RESULT';

interface AnalysisContextType {
  state: ActiveAnalysisState;
  setTaskMode: (mode: TaskMode) => void;
  setQuery: (query: string) => void;
  setPrimaryImage: (file: File | null, previewUrl?: string | null) => void;
  setSecondImage: (file: File | null, previewUrl?: string | null) => void;
  setSarImage: (file: File | null, previewUrl?: string | null) => void;
  setParameter: (key: string, value: any) => void;
  resetInputs: () => void;
  loadPreset: (preset: {
    mode: TaskMode;
    query: string;
    primaryAsset: string;
    secondAsset?: string;
    sarAsset?: string;
  }) => Promise<void>;

  loading: boolean;
  elapsedSeconds: number;
  activeStage: OperationalStage;
  result: AnalysisApiResponse | null;
  error: ActiveError | null;
  clearError: () => void;
  executeAnalysis: () => Promise<AnalysisApiResponse | null>;
  setResultDirectly: (res: AnalysisApiResponse, previews?: { primary?: string | null; second?: string | null; sar?: string | null }, q?: string) => void;
}

const AnalysisContext = createContext<AnalysisContextType | null>(null);

export const AnalysisProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { addHistoryEntry } = useHistory();
  const toast = useToast();
  const { navigate } = useRouter();

  const [state, setState] = useState<ActiveAnalysisState>({
    taskMode: 'AUTO',
    query: '',
    primaryImage: null,
    primaryPreview: null,
    secondImage: null,
    secondPreview: null,
    sarImage: null,
    sarPreview: null,
    parameters: {},
  });

  const [loading, setLoading] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [activeStage, setActiveStage] = useState<OperationalStage>('IDLE');
  const [result, setResult] = useState<AnalysisApiResponse | null>(null);
  const [error, setError] = useState<ActiveError | null>(null);

  // Live stopwatch when loading
  useEffect(() => {
    let timer: any;
    if (loading) {
      setElapsedSeconds(0);
      const start = performance.now();
      timer = setInterval(() => {
        setElapsedSeconds(Math.round((performance.now() - start) / 100) / 10);
      }, 100);
    } else {
      setElapsedSeconds(0);
    }
    return () => clearInterval(timer);
  }, [loading]);

  const setTaskMode = useCallback((taskMode: TaskMode) => {
    setState((prev) => ({ ...prev, taskMode }));
  }, []);

  const setQuery = useCallback((query: string) => {
    setState((prev) => ({ ...prev, query }));
  }, []);

  const setPrimaryImage = useCallback((file: File | null, previewUrl?: string | null) => {
    setState((prev) => {
      // Clean up previous blob preview if needed
      if (prev.primaryPreview && prev.primaryPreview.startsWith('blob:')) {
        URL.revokeObjectURL(prev.primaryPreview);
      }
      const newPreview = previewUrl !== undefined ? previewUrl : file ? URL.createObjectURL(file) : null;
      return { ...prev, primaryImage: file, primaryPreview: newPreview };
    });
  }, []);

  const setSecondImage = useCallback((file: File | null, previewUrl?: string | null) => {
    setState((prev) => {
      if (prev.secondPreview && prev.secondPreview.startsWith('blob:')) {
        URL.revokeObjectURL(prev.secondPreview);
      }
      const newPreview = previewUrl !== undefined ? previewUrl : file ? URL.createObjectURL(file) : null;
      return { ...prev, secondImage: file, secondPreview: newPreview };
    });
  }, []);

  const setSarImage = useCallback((file: File | null, previewUrl?: string | null) => {
    setState((prev) => {
      if (prev.sarPreview && prev.sarPreview.startsWith('blob:')) {
        URL.revokeObjectURL(prev.sarPreview);
      }
      const newPreview = previewUrl !== undefined ? previewUrl : file ? URL.createObjectURL(file) : null;
      return { ...prev, sarImage: file, sarPreview: newPreview };
    });
  }, []);

  const setParameter = useCallback((key: string, value: any) => {
    setState((prev) => ({
      ...prev,
      parameters: { ...prev.parameters, [key]: value },
    }));
  }, []);

  const resetInputs = useCallback(() => {
    setState({
      taskMode: 'AUTO',
      query: '',
      primaryImage: null,
      primaryPreview: null,
      secondImage: null,
      secondPreview: null,
      sarImage: null,
      sarPreview: null,
      parameters: {},
    });
    setResult(null);
    setError(null);
    setActiveStage('IDLE');
  }, []);

  const loadPreset = useCallback(
    async (preset: {
      mode: TaskMode;
      query: string;
      primaryAsset: string;
      secondAsset?: string;
      sarAsset?: string;
    }) => {
      try {
        setTaskMode(preset.mode);
        setQuery(preset.query);

        // Fetch primary
        const primRes = await fetch(`/samples/${preset.primaryAsset}`);
        const primBlob = await primRes.blob();
        const primFile = new File([primBlob], preset.primaryAsset, {
          type: primBlob.type || 'image/jpeg',
        });
        setPrimaryImage(primFile, `/samples/${preset.primaryAsset}`);

        // Fetch second if any
        if (preset.secondAsset) {
          const secRes = await fetch(`/samples/${preset.secondAsset}`);
          const secBlob = await secRes.blob();
          const secFile = new File([secBlob], preset.secondAsset, {
            type: secBlob.type || 'image/jpeg',
          });
          setSecondImage(secFile, `/samples/${preset.secondAsset}`);
        } else {
          setSecondImage(null, null);
        }

        // Fetch SAR if any
        if (preset.sarAsset) {
          const sarRes = await fetch(`/samples/${preset.sarAsset}`);
          const sarBlob = await sarRes.blob();
          const sarFile = new File([sarBlob], preset.sarAsset, {
            type: sarBlob.type || 'image/jpeg',
          });
          setSarImage(sarFile, `/samples/${preset.sarAsset}`);
        } else {
          setSarImage(null, null);
        }

        toast.info('Sample Preset Loaded', `Loaded ${preset.mode} sample inputs.`);
      } catch (err: any) {
        console.error('Failed to load preset assets:', err);
        toast.error('Preset Load Failed', 'Could not fetch sample satellite images.');
      }
    },
    [setPrimaryImage, setQuery, setSarImage, setSecondImage, setTaskMode, toast]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const setResultDirectly = useCallback(
    (
      res: AnalysisApiResponse,
      previews?: { primary?: string | null; second?: string | null; sar?: string | null },
      q?: string
    ) => {
      setResult(res);
      if (q) setQuery(q);
      if (previews?.primary) setState((p) => ({ ...p, primaryPreview: previews.primary || null }));
      if (previews?.second) setState((p) => ({ ...p, secondPreview: previews.second || null }));
      if (previews?.sar) setState((p) => ({ ...p, sarPreview: previews.sar || null }));
    },
    [setQuery]
  );

  const executeAnalysis = useCallback(async (): Promise<AnalysisApiResponse | null> => {
    if (!state.query.trim()) {
      toast.warning('Query Required', 'Please enter an analytical question or objective.');
      return null;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setActiveStage('INPUT_VALIDATION');
    toast.info('Analysis Started', `Submitting query to agentic pipeline...`);

    // Advance operational stages reflecting real pipeline steps
    let stageTimer: any;
    stageTimer = setTimeout(() => setActiveStage('ROUTER'), 250);
    setTimeout(() => setActiveStage('TOOL_SELECTED'), 600);
    setTimeout(() => setActiveStage('TOOL_EXECUTION'), 1000);

    const payload: AnalyzePayload = {
      query: state.query.trim(),
      image: state.primaryImage,
      second_image: state.secondImage,
      sar_image: state.sarImage,
      task: state.taskMode === 'AUTO' ? null : state.taskMode,
      parameters: Object.keys(state.parameters).length > 0 ? state.parameters : null,
    };

    try {
      const apiResult = await analyzeRequest(payload);
      clearTimeout(stageTimer);
      setActiveStage('EVIDENCE');
      setTimeout(() => setActiveStage('CONFIDENCE'), 150);
      setTimeout(() => setActiveStage('RESULT'), 300);

      // Handle backend status
      if (apiResult.status === 'NEEDS_CLARIFICATION') {
        setError({
          status: apiResult.status,
          errorType: apiResult.error_type || 'NEEDS_CLARIFICATION',
          message: apiResult.answer,
          clarificationPrompt: apiResult.metadata?.clarification_prompt,
        });
        setResult(apiResult);
        toast.warning('Clarification Needed', 'Query requires more specific analytical intent.');
      } else if (apiResult.status === 'INVALID_INPUT' || apiResult.status === 'ERROR') {
        setError({
          status: apiResult.status,
          errorType: apiResult.error_type,
          message: apiResult.answer,
          validationErrors: apiResult.metadata?.validation_errors,
        });
        setResult(apiResult);
        toast.error('Validation Error', apiResult.answer);
      } else {
        setResult(apiResult);
        toast.success(
          'Analysis Completed',
          `Executed via ${apiResult.selected_tool || 'tool'} in ${(apiResult.latency_ms / 1000).toFixed(1)}s`
        );

        // Record in persistent history
        const confObj = typeof apiResult.confidence === 'object' && apiResult.confidence !== null
          ? apiResult.confidence as any
          : null;
        const confLevel = confObj ? confObj.level : (typeof apiResult.confidence === 'number' ? (apiResult.confidence >= 0.7 ? 'HIGH' : apiResult.confidence >= 0.4 ? 'MEDIUM' : 'LOW') : null);
        const confScore = confObj ? confObj.score : (typeof apiResult.confidence === 'number' ? apiResult.confidence : null);

        addHistoryEntry({
          task: apiResult.selected_tool || state.taskMode,
          query: state.query,
          model: apiResult.model,
          status: apiResult.status,
          confidenceLevel: confLevel,
          confidenceScore: confScore,
          primaryPreview: state.primaryPreview,
          secondPreview: state.secondPreview,
          sarPreview: state.sarPreview,
          result: apiResult,
        });

        // Navigate seamlessly to results page!
        navigate('/results');
      }

      return apiResult;
    } catch (err: any) {
      clearTimeout(stageTimer);
      setActiveStage('IDLE');
      const msg = err?.message || 'Unable to communicate with SatQuery AI backend at http://127.0.0.1:8000.';
      setError({
        status: 'NETWORK_ERROR',
        errorType: 'API_CONNECTION_ERROR',
        message: msg,
      });
      toast.error('Connection Failed', msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, [
    state.query,
    state.primaryImage,
    state.secondImage,
    state.sarImage,
    state.taskMode,
    state.parameters,
    state.primaryPreview,
    state.secondPreview,
    state.sarPreview,
    toast,
    addHistoryEntry,
    navigate,
  ]);

  return (
    <AnalysisContext.Provider
      value={{
        state,
        setTaskMode,
        setQuery,
        setPrimaryImage,
        setSecondImage,
        setSarImage,
        setParameter,
        resetInputs,
        loadPreset,
        loading,
        elapsedSeconds,
        activeStage,
        result,
        error,
        clearError,
        executeAnalysis,
        setResultDirectly,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
};

export function useAnalysis(): AnalysisContextType {
  const ctx = useContext(AnalysisContext);
  if (!ctx) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return ctx;
}
