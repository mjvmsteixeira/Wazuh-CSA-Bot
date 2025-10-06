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
}

export interface AnalysisRequest {
  agent_id: string;
  policy_id: string;
  check_id: number;
  language: 'pt' | 'en';
  ai_provider: 'vllm' | 'openai';
}

export interface AnalysisResponse {
  check_id: number;
  report: string;
  ai_provider: string;
  language: string;
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

  // PDF Reports
  generatePDF: async (request: PDFRequest): Promise<PDFResponse> => {
    const response = await apiClient.post('/reports/pdf', request);
    return response.data;
  },

  downloadPDF: (filename: string): string => {
    return `${API_BASE_URL}/reports/download/${filename}`;
  },
};

export default api;
