import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import AgentSelector from '../components/AgentSelector';
import ChecksList from '../components/ChecksList';
import AnalysisPanel from '../components/AnalysisPanel';
import BatchAnalysisPanel from '../components/BatchAnalysisPanel';
import AIProviderSelector from '../components/AIProviderSelector';
import SystemStatus from '../components/SystemStatus';
import HistoryPanel from '../components/HistoryPanel';
import CacheStats from '../components/CacheStats';
import api, { Agent, SCACheck } from '../services/api';

export default function Dashboard() {
  const { t, i18n } = useTranslation();
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [selectedPolicy, setSelectedPolicy] = useState<string>('');
  const [selectedCheck, setSelectedCheck] = useState<SCACheck | null>(null);
  const [batchChecks, setBatchChecks] = useState<SCACheck[] | null>(null);
  const [aiProvider, setAIProvider] = useState<'vllm' | 'openai'>('openai'); // Default to openai
  const [activeTab, setActiveTab] = useState<'checks' | 'history' | 'stats'>('checks');

  // Get system status to determine initial AI provider
  const { data: systemStatus } = useQuery({
    queryKey: ['system-status-init'],
    queryFn: async () => {
      const response = await api.getSystemStatus();
      return response;
    },
  });

  // Set initial AI provider based on AI mode
  useEffect(() => {
    if (!systemStatus) return;

    const aiMode = systemStatus.ai_mode;
    const vllmAvailable = systemStatus.vllm?.available;
    const openaiAvailable = systemStatus.openai?.available;

    // Auto-select provider based on AI mode and availability
    if (aiMode === 'local' && vllmAvailable) {
      setAIProvider('vllm');
    } else if (aiMode === 'external' && openaiAvailable) {
      setAIProvider('openai');
    } else if (aiMode === 'mixed') {
      // In mixed mode, prefer vLLM if available, otherwise OpenAI
      if (vllmAvailable) {
        setAIProvider('vllm');
      } else if (openaiAvailable) {
        setAIProvider('openai');
      }
    }
  }, [systemStatus]);

  // Fetch policies when agent is selected
  const { data: policies } = useQuery({
    queryKey: ['policies', selectedAgent?.id],
    queryFn: () => api.getAgentPolicies(selectedAgent!.id),
    enabled: !!selectedAgent,
  });

  // Fetch failed checks when policy is selected
  const { data: checks, isLoading: checksLoading } = useQuery({
    queryKey: ['checks', selectedAgent?.id, selectedPolicy],
    queryFn: () => api.getFailedChecks(selectedAgent!.id, selectedPolicy),
    enabled: !!selectedAgent && !!selectedPolicy,
  });

  // Fetch agent history to determine which checks have been analyzed
  const { data: historyData } = useQuery({
    queryKey: ['agent-history', selectedAgent?.id],
    queryFn: () => api.getAgentHistory(selectedAgent!.id, 1000), // Get large number to cover all
    enabled: !!selectedAgent,
    refetchInterval: 30000, // Refetch every 30 seconds to update analyzed state
  });

  // Create a Set of analyzed check IDs for quick lookup
  const analyzedCheckIds = useMemo(() => {
    if (!historyData?.analyses) return new Set<number>();
    const ids = new Set(
      historyData.analyses
        .filter(a => a.status === 'completed')
        .map(a => a.check_id)
    );
    console.log('[Dashboard] Analyzed check IDs:', Array.from(ids));
    console.log('[Dashboard] History data:', historyData.analyses.length, 'analyses');
    return ids;
  }, [historyData]);

  // Auto-select first policy
  if (policies && policies.length > 0 && !selectedPolicy) {
    setSelectedPolicy(policies[0].policy_id);
  }

  return (
    <div className="space-y-6">
      {/* System Status Panel */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h2 className="text-lg font-semibold mb-4 text-gray-900">System Status</h2>
        <SystemStatus />
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AgentSelector
          selectedAgent={selectedAgent}
          onSelectAgent={setSelectedAgent}
        />

        <AIProviderSelector
          selectedProvider={aiProvider}
          onSelectProvider={setAIProvider}
        />
      </div>

      {/* SCA Policy Info */}
      {policies && policies.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">{t('dashboard.scaPolicy')}</p>
                <p className="text-lg font-semibold text-gray-900">{policies[0].name}</p>
                {policies[0].description && (
                  <p className="text-sm text-gray-600 mt-1">{policies[0].description}</p>
                )}
              </div>
            </div>
            {policies.length > 1 && (
              <div className="flex-shrink-0">
                <select
                  value={selectedPolicy}
                  onChange={(e) => setSelectedPolicy(e.target.value)}
                  className="text-sm border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  {policies.map((policy) => (
                    <option key={policy.policy_id} value={policy.policy_id}>
                      {policy.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tabs */}
      {selectedAgent && selectedPolicy && (
        <div>
          {/* Tab Navigation */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('checks')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'checks'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {t('dashboard.failedChecks')} ({checks?.length || 0})
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'history'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Analysis History
              </button>
              <button
                onClick={() => setActiveTab('stats')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'stats'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Cache Statistics
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === 'checks' && (
            <div className="card">
              {checksLoading ? (
                <div className="text-center py-8 text-gray-500">
                  {t('common.loading')}
                </div>
              ) : checks && checks.length > 0 ? (
                <ChecksList
                  checks={checks}
                  onAnalyze={(check) => setSelectedCheck(check)}
                  onAnalyzeBatch={(checks) => setBatchChecks(checks)}
                  analyzedCheckIds={analyzedCheckIds}
                />
              ) : (
                <div className="text-center py-8 text-gray-500">
                  {t('dashboard.noChecks')}
                </div>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <HistoryPanel
              agentId={selectedAgent.id}
              agentName={selectedAgent.name}
              language={i18n.language as 'pt' | 'en'}
            />
          )}

          {activeTab === 'stats' && (
            <CacheStats language={i18n.language as 'pt' | 'en'} />
          )}
        </div>
      )}

      {!selectedAgent && (
        <div className="card text-center py-12 text-gray-500">
          {t('dashboard.noAgent')}
        </div>
      )}

      {/* Analysis Panel */}
      {selectedCheck && selectedAgent && (
        <AnalysisPanel
          check={selectedCheck}
          agentId={selectedAgent.id}
          agentName={selectedAgent.name}
          policyId={selectedPolicy}
          aiProvider={aiProvider}
          language={i18n.language as 'pt' | 'en'}
          onClose={() => setSelectedCheck(null)}
        />
      )}

      {/* Batch Analysis Panel */}
      {batchChecks && selectedAgent && (
        <BatchAnalysisPanel
          checks={batchChecks}
          agentId={selectedAgent.id}
          agentName={selectedAgent.name}
          policyId={selectedPolicy}
          aiProvider={aiProvider}
          language={i18n.language as 'pt' | 'en'}
          onClose={() => setBatchChecks(null)}
        />
      )}
    </div>
  );
}
