import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Agent {
  id: string;
  name: string;
  ip?: string;
  status?: string;
  os?: any;
}

export interface SCAPolicy {
  policy_id: string;
  name: string;
  description?: string;
}

export interface SCACheck {
  id: number;
  title: string;
  description?: string;
  rationale?: string;
  remediation?: string;
  result: string;
  compliance?: Array<{ key: string; value: string }>;
}

export interface AnalysisRequest {
  agent_id: string;
  policy_id: string;
  check_id: number;
  language: 'pt' | 'en';
  ai_provider: 'vllm' | 'openai';
}

export interface RemediationScript {
  script_content: string;
  script_language: 'bash' | 'powershell' | 'python';
  validation_command: string;
  estimated_duration?: string;
  requires_root: boolean;
  risks: string[];
}

export interface AnalysisResponse {
  check_id: number;
  report: string;
  remediation_script?: RemediationScript;
  ai_provider: string;
  language: string;
  cached_from_agent?: string;
}

export interface PDFRequest {
  agent_name: string;
  check_id: number;
  report_text: string;
  language: 'pt' | 'en';
}

export interface PDFResponse {
  filename: string;
  download_url: string;
}

export interface AnalysisHistory {
  id: string;
  agent_id: string;
  agent_name: string;
  policy_id: string;
  check_id: number;
  check_title: string;
  check_description?: string;
  analysis_date: string;
  language: 'pt' | 'en';
  ai_provider: 'vllm' | 'openai';
  report_text: string;
  remediation_script?: RemediationScript;
  status: 'pending' | 'completed' | 'failed';
  error_message?: string;
  execution_time_seconds?: number;
}

export interface AnalysisHistoryListResponse {
  analyses: AnalysisHistory[];
  total: number;
  limit: number;
  offset: number;
}

export interface CacheStats {
  total_analyses: number;
  completed: number;
  failed: number;
  cached_valid: number;
  cache_enabled: boolean;
  cache_ttl_hours: number;
}

// API functions
export const api = {
  // Agents
  getAgents: async (search?: string): Promise<Agent[]> => {
    const response = await apiClient.get('/agents', {
      params: search ? { search } : {},
    });
    return response.data;
  },

  getAgentByName: async (agentName: string): Promise<Agent> => {
    const response = await apiClient.get(`/agents/name/${agentName}`);
    return response.data;
  },

  // SCA
  getAgentPolicies: async (agentId: string): Promise<SCAPolicy[]> => {
    const response = await apiClient.get(`/sca/${agentId}/policies`);
    return response.data;
  },

  getFailedChecks: async (agentId: string, policyId: string): Promise<SCACheck[]> => {
    const response = await apiClient.get(`/sca/${agentId}/checks/${policyId}/failed`);
    return response.data;
  },

  getCheckDetails: async (
    agentId: string,
    policyId: string,
    checkId: number
  ): Promise<SCACheck> => {
    const response = await apiClient.get(`/sca/${agentId}/checks/${policyId}/${checkId}`);
    return response.data;
  },

  // Analysis
  analyzeCheck: async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    const response = await apiClient.post('/analysis', request);
    return response.data;
  },

  getAIProviders: async (): Promise<string[]> => {
    const response = await apiClient.get('/analysis/providers');
    return response.data.providers;
  },

  getAIStatus: async (): Promise<any> => {
    const response = await apiClient.get('/analysis/status');
    return response.data;
  },

  getSystemStatus: async (): Promise<any> => {
    const response = await apiClient.get('/analysis/system-status');
    return response.data;
  },

  // PDF Reports
  generatePDF: async (request: PDFRequest): Promise<PDFResponse> => {
    const response = await apiClient.post('/reports/pdf', request);
    return response.data;
  },

  downloadPDF: (filename: string): string => {
    return `${API_BASE_URL}/reports/download/${filename}`;
  },

  // History
  getAgentHistory: async (
    agentId: string,
    limit: number = 50,
    offset: number = 0,
    status?: 'pending' | 'completed' | 'failed'
  ): Promise<AnalysisHistoryListResponse> => {
    const params: any = { limit, offset };
    if (status) params.status = status;
    const response = await apiClient.get(`/history/agent/${agentId}`, { params });
    return response.data;
  },

  getCheckHistory: async (
    agentId: string,
    checkId: number,
    limit: number = 20
  ): Promise<AnalysisHistoryListResponse> => {
    const response = await apiClient.get(`/history/check/${agentId}/${checkId}`, {
      params: { limit },
    });
    return response.data;
  },

  getAnalysisById: async (analysisId: string): Promise<AnalysisHistory> => {
    const response = await apiClient.get(`/history/${analysisId}`);
    return response.data;
  },

  deleteAnalysis: async (analysisId: string): Promise<void> => {
    await apiClient.delete(`/history/${analysisId}`);
  },

  getCacheStats: async (): Promise<CacheStats> => {
    const response = await apiClient.get('/history/stats/cache');
    return response.data;
  },

  getRecentAnalyses: async (
    hours: number = 24,
    limit: number = 100
  ): Promise<AnalysisHistoryListResponse> => {
    const response = await apiClient.get('/history/recent', {
      params: { hours, limit },
    });
    return response.data;
  },
};

export default api;
