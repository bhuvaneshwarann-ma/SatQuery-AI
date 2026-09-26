/**
 * SatQuery AI — API Client Layer (Phase 8A)
 * Strictly typed HTTP client communicating with the live FastAPI backend at /api.
 * Provides multipart upload formatting and artifact resolution without fabricating data.
 */

export interface ObservableTraceStep {
  step: string;
  status: string;
  selected_task?: string | null;
  selected_tool?: string | null;
  model?: string | null;
  permitted_parameters?: Record<string, any>;
  input_references?: string[];
  latency_ms?: number | null;
  output_reference?: string | null;
  evidence_reference?: string | null;
  error?: string | null;
}

export interface ConfidenceInfo {
  level: 'LOW' | 'MEDIUM' | 'HIGH';
  score?: number | null;
  type: string;
  explanation: string;
  signals?: Record<string, any>;
  box_count?: number;
  changed_pixels?: number;
  correlation?: number;
}

export interface VisualEvidenceItem {
  category: string;
  description: string;
}

export interface TaskPlanStepInfo {
  tool: string;
  purpose: string;
  required_inputs: string[];
  parameters: Record<string, any>;
}

export interface StructuredTaskPlanInfo {
  intent: string;
  target?: string | null;
  requires_temporal_pair: boolean;
  requires_spatial_evidence: boolean;
  is_multi_tool: boolean;
  policy_validated: boolean;
  policy_notes: string[];
  plan: TaskPlanStepInfo[];
}

export interface AnalysisApiResponse {
  status: 'SUCCESS' | 'ERROR' | 'INVALID_INPUT' | 'NEEDS_CLARIFICATION' | 'UNREGISTERED_TOOL';
  selected_tool: string | null;
  model: string;
  answer: string;
  confidence: ConfidenceInfo | number | null;
  image_description?: string | null;
  visual_evidence?: VisualEvidenceItem[] | null;
  evidence: Record<string, any> | null;
  task_plan?: StructuredTaskPlanInfo | null;
  metadata: Record<string, any>;
  observable_execution_trace: ObservableTraceStep[];
  latency_ms: number;
  error_type: string | null;
}


export interface HealthResponse {
  status: string;
  version: string;
  gpu_available: boolean;
  gpu_name: string;
  free_vram_mb: number;
  total_vram_mb: number;
  registered_tools: string[];
}

export interface ToolParameterSpec {
  name: string;
  type: string;
  default: any;
  description: string;
  min_value?: number | null;
  max_value?: number | null;
  allowed_values?: any[] | null;
}

export interface ToolDefinitionModel {
  tool_name: string;
  description: string;
  accepted_input_types: string[];
  required_inputs: string[];
  permitted_parameters: Record<string, ToolParameterSpec>;
  model_or_engine: string;
  output_type: string;
  evidence_type: string;
  confidence_supported: boolean;
  resource_notes: string;
}

export interface AnalyzePayload {
  query: string;
  image?: File | null;
  second_image?: File | null;
  sar_image?: File | null;
  task?: string | null;
  parameters?: Record<string, any> | null;
}

const API_BASE = ''; // Uses Vite proxy to http://127.0.0.1:8000/api or relative /api

export async function fetchHealth(): Promise<HealthResponse> {
  const resp = await fetch(`${API_BASE}/api/health`);
  if (!resp.ok) {
    throw new Error(`Health check failed with status ${resp.status}`);
  }
  return resp.json();
}

export async function fetchTools(): Promise<ToolDefinitionModel[]> {
  const resp = await fetch(`${API_BASE}/api/tools`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch tools registry: status ${resp.status}`);
  }
  return resp.json();
}

export async function analyzeRequest(payload: AnalyzePayload): Promise<AnalysisApiResponse> {
  const formData = new FormData();
  formData.append('query', payload.query);

  if (payload.image) {
    formData.append('image', payload.image);
  }
  if (payload.second_image) {
    formData.append('second_image', payload.second_image);
  }
  if (payload.sar_image) {
    formData.append('sar_image', payload.sar_image);
  }
  if (payload.task && payload.task !== 'AUTO') {
    formData.append('task', payload.task);
  }
  if (payload.parameters && Object.keys(payload.parameters).length > 0) {
    formData.append('parameters', JSON.stringify(payload.parameters));
  }

  const resp = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  const data = await resp.json();
  if (!resp.ok && !data.status) {
    throw new Error(data.detail || `Server returned error ${resp.status}`);
  }
  return data;
}

/**
 * Resolves a backend-returned artifact path to the public static artifacts endpoint.
 * Returns null if no artifact is referenced.
 */
export function getArtifactUrl(artifactRef?: string | null): string | null {
  if (!artifactRef || typeof artifactRef !== 'string') {
    return null;
  }
  // Extract filename from relative path (e.g. docs\\results\\grounding_execution_artifact.jpg)
  const cleanPath = artifactRef.replace(/\\/g, '/');
  const filename = cleanPath.split('/').pop();
  if (!filename) {
    return null;
  }
  return `${API_BASE}/api/artifacts/${filename}`;
}
