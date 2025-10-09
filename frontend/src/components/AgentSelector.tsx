import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Circle, AlertCircle, ZoomIn, X } from 'lucide-react';
import api, { Agent } from '../services/api';

interface Props {
  selectedAgent: Agent | null;
  onSelectAgent: (agent: Agent | null) => void;
}

export default function AgentSelector({ selectedAgent, onSelectAgent }: Props) {
  const { t } = useTranslation();
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [showOnlineOnly, setShowOnlineOnly] = useState(false);

  const { data: agents, isLoading, error } = useQuery({
    queryKey: ['agents'],
    queryFn: () => api.getAgents(),
  });

  // Filter agents based on online/offline toggle
  const filteredAgents = useMemo(() => {
    if (!agents) return [];
    if (!showOnlineOnly) return agents;
    return agents.filter(agent => agent.status?.toLowerCase() === 'active');
  }, [agents, showOnlineOnly]);

  const getStatusColor = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'text-green-500';
      case 'disconnected':
        return 'text-red-500';
      case 'never_connected':
        return 'text-gray-400';
      default:
        return 'text-yellow-500';
    }
  };

  const getStatusLabel = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'Active';
      case 'disconnected':
        return 'Disconnected';
      case 'never_connected':
        return 'Never Connected';
      default:
        return 'Unknown';
    }
  };

  return (
    <>
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">
            Wazuh Agent
          </label>

          {/* Online/Offline Toggle Switch */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-600">
              {showOnlineOnly ? 'Online Only' : 'All Agents'}
            </span>
            <button
              onClick={() => setShowOnlineOnly(!showOnlineOnly)}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                showOnlineOnly ? 'bg-green-600' : 'bg-gray-300'
              }`}
              role="switch"
              aria-checked={showOnlineOnly}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  showOnlineOnly ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        </div>

        <div className="relative">
          <select
            value={selectedAgent?.id || ''}
            onChange={(e) => {
              const agent = filteredAgents?.find(a => a.id === e.target.value);
              onSelectAgent(agent || null);
            }}
            className="input pr-10 appearance-none"
            disabled={isLoading || !!error}
          >
            <option value="">
              {isLoading ? t('common.loading') : error ? 'Error loading agents' : t('dashboard.selectAgentPlaceholder')}
            </option>
            {filteredAgents?.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} (ID: {agent.id}) - {getStatusLabel(agent.status)}
              </option>
            ))}
          </select>

          {/* Custom dropdown arrow */}
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-2 p-3 bg-red-50 rounded-md border border-red-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
                <span className="text-sm text-red-700">Failed to load agents</span>
              </div>
              <button
                onClick={() => setShowErrorModal(true)}
                className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded border border-red-300 transition-colors"
              >
                Details
                <ZoomIn className="w-3 h-3" />
              </button>
            </div>
          </div>
        )}

        {selectedAgent && (
          <div className="mt-2 p-3 bg-primary-50 rounded-md border border-primary-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Circle
                  className={`h-3 w-3 fill-current ${getStatusColor(selectedAgent.status)}`}
                />
                <div>
                  <div className="font-medium text-primary-900">{selectedAgent.name}</div>
                  <div className="text-sm text-primary-600">
                    ID: {selectedAgent.id} • Status: {getStatusLabel(selectedAgent.status)}
                  </div>
                  {selectedAgent.ip && (
                    <div className="text-xs text-primary-500">IP: {selectedAgent.ip}</div>
                  )}
                </div>
              </div>
              <button
                onClick={() => onSelectAgent(null)}
                className="text-sm text-primary-600 hover:text-primary-800 font-medium"
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Error Details Modal */}
      {showErrorModal && error && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
            <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Error Loading Agents
                </h3>
              </div>
              <button
                onClick={() => setShowErrorModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-6 py-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <pre className="text-sm text-red-800 whitespace-pre-wrap font-mono">
                  {error instanceof Error ? error.message : String(error)}
                </pre>
              </div>
              <div className="mt-4 text-sm text-gray-600">
                <p className="font-medium mb-2">Troubleshooting Steps:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Verify Wazuh API is running and accessible</li>
                  <li>Check API credentials in .env file</li>
                  <li>Ensure network connectivity to Wazuh server</li>
                  <li>Review backend logs for detailed error information</li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-200 px-6 py-4 flex justify-end gap-2">
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Retry
              </button>
              <button
                onClick={() => setShowErrorModal(false)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
