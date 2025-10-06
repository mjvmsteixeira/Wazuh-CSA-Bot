import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import AgentSelector from '../components/AgentSelector';
import ChecksList from '../components/ChecksList';
import AnalysisPanel from '../components/AnalysisPanel';
import AIProviderSelector from '../components/AIProviderSelector';
import AIStatus from '../components/AIStatus';
import api, { Agent, SCACheck } from '../services/api';

export default function Dashboard() {
  const { t, i18n } = useTranslation();
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [selectedPolicy, setSelectedPolicy] = useState<string>('');
  const [selectedCheck, setSelectedCheck] = useState<SCACheck | null>(null);
  const [aiProvider, setAIProvider] = useState<'vllm' | 'openai'>('vllm');

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

  // Auto-select first policy
  if (policies && policies.length > 0 && !selectedPolicy) {
    setSelectedPolicy(policies[0].policy_id);
  }

  return (
    <div className="space-y-6">
      {/* AI Status Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <AIStatus />
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <AgentSelector
          selectedAgent={selectedAgent}
          onSelectAgent={setSelectedAgent}
        />

        <AIProviderSelector
          selectedProvider={aiProvider}
          onSelectProvider={setAIProvider}
        />

        {policies && policies.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('dashboard.selectPolicy')}
            </label>
            <select
              value={selectedPolicy}
              onChange={(e) => setSelectedPolicy(e.target.value)}
              className="input"
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

      {/* Checks List */}
      {selectedAgent && selectedPolicy && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">
            {t('dashboard.failedChecks')} ({checks?.length || 0})
          </h2>

          {checksLoading ? (
            <div className="text-center py-8 text-gray-500">
              {t('common.loading')}
            </div>
          ) : checks && checks.length > 0 ? (
            <ChecksList
              checks={checks}
              onAnalyze={(check) => setSelectedCheck(check)}
            />
          ) : (
            <div className="text-center py-8 text-gray-500">
              {t('dashboard.noChecks')}
            </div>
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
    </div>
  );
}
