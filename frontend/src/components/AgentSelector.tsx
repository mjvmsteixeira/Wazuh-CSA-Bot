import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Search } from 'lucide-react';
import api, { Agent } from '../services/api';

interface Props {
  selectedAgent: Agent | null;
  onSelectAgent: (agent: Agent | null) => void;
}

export default function AgentSelector({ selectedAgent, onSelectAgent }: Props) {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');

  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents', search],
    queryFn: () => api.getAgents(search || undefined),
  });

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {t('dashboard.selectAgent')}
      </label>

      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>

        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={t('dashboard.selectAgentPlaceholder')}
          className="input pl-10"
        />
      </div>

      {search && agents && agents.length > 0 && (
        <div className="mt-2 max-h-48 overflow-y-auto border border-gray-200 rounded-md bg-white shadow-lg">
          {agents.map((agent) => (
            <button
              key={agent.id}
              onClick={() => {
                onSelectAgent(agent);
                setSearch('');
              }}
              className="w-full text-left px-4 py-2 hover:bg-gray-50 focus:bg-gray-50 focus:outline-none"
            >
              <div className="font-medium text-gray-900">{agent.name}</div>
              <div className="text-sm text-gray-500">ID: {agent.id}</div>
            </button>
          ))}
        </div>
      )}

      {selectedAgent && (
        <div className="mt-2 flex items-center justify-between p-3 bg-primary-50 rounded-md">
          <div>
            <div className="font-medium text-primary-900">{selectedAgent.name}</div>
            <div className="text-sm text-primary-600">ID: {selectedAgent.id}</div>
          </div>
          <button
            onClick={() => onSelectAgent(null)}
            className="text-sm text-primary-600 hover:text-primary-800"
          >
            ✕
          </button>
        </div>
      )}

      {isLoading && (
        <div className="mt-2 text-sm text-gray-500">{t('common.loading')}</div>
      )}
    </div>
  );
}
