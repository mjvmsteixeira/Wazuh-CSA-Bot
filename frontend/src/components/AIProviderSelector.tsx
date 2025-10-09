import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { Brain, Cloud, AlertCircle } from 'lucide-react';
import { useEffect } from 'react';
import api from '../services/api';

interface Props {
  selectedProvider: 'vllm' | 'openai';
  onSelectProvider: (provider: 'vllm' | 'openai') => void;
}

export default function AIProviderSelector({ selectedProvider, onSelectProvider }: Props) {
  const { t } = useTranslation();

  // Get AI status to check which providers are enabled
  const { data: status, isLoading } = useQuery({
    queryKey: ['ai-status'],
    queryFn: async () => {
      const response = await api.getAIStatus();
      return response;
    },
  });

  const aiMode = status?.ai_mode || 'mixed';
  const vllmEnabled = status?.vllm?.enabled ?? false;
  const openaiEnabled = status?.openai?.enabled ?? false;
  const vllmAvailable = status?.vllm?.available ?? false;
  const openaiAvailable = status?.openai?.available ?? false;

  // Auto-select the correct provider based on AI mode
  useEffect(() => {
    if (!status) return;

    // If current selection is not enabled, auto-switch to available provider
    if (selectedProvider === 'vllm' && !vllmEnabled && openaiEnabled) {
      onSelectProvider('openai');
    } else if (selectedProvider === 'openai' && !openaiEnabled && vllmEnabled) {
      onSelectProvider('vllm');
    }
  }, [status, selectedProvider, vllmEnabled, openaiEnabled, onSelectProvider]);

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('analysis.selectProvider')}
        </label>
        <div className="h-12 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  // Show warning if no providers are available
  if (!vllmEnabled && !openaiEnabled) {
    return (
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('analysis.selectProvider')}
        </label>
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span className="text-sm">No AI providers configured</span>
        </div>
      </div>
    );
  }

  // Determine grid layout based on number of enabled providers
  const gridClass = vllmEnabled && openaiEnabled ? 'grid-cols-2' : 'grid-cols-1';

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {t('analysis.selectProvider')}
        <span className="ml-2 text-xs text-gray-500">
          (Mode: {aiMode.toUpperCase()})
        </span>
      </label>

      <div className={`grid ${gridClass} gap-2`}>
        {/* vLLM - Only show if enabled (local or mixed mode) */}
        {vllmEnabled && (
          <button
            onClick={() => onSelectProvider('vllm')}
            disabled={!vllmAvailable}
            className={`flex items-center justify-center space-x-2 px-4 py-3 rounded-lg border-2 transition-colors ${
              selectedProvider === 'vllm'
                ? 'border-green-500 bg-green-50 text-green-700'
                : vllmAvailable
                ? 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                : 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
            title={vllmAvailable ? 'Local LLM available' : 'Local LLM not available'}
          >
            <Brain className="w-5 h-5" />
            <div className="flex flex-col items-start">
              <span className="text-sm font-medium">{t('analysis.local')}</span>
              {!vllmAvailable && (
                <span className="text-xs text-gray-500">Offline</span>
              )}
            </div>
          </button>
        )}

        {/* OpenAI - Only show if enabled (external or mixed mode) */}
        {openaiEnabled && (
          <button
            onClick={() => onSelectProvider('openai')}
            disabled={!openaiAvailable}
            className={`flex items-center justify-center space-x-2 px-4 py-3 rounded-lg border-2 transition-colors ${
              selectedProvider === 'openai'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : openaiAvailable
                ? 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                : 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
            title={openaiAvailable ? 'OpenAI available' : 'OpenAI not configured'}
          >
            <Cloud className="w-5 h-5" />
            <div className="flex flex-col items-start">
              <span className="text-sm font-medium">{t('analysis.openai')}</span>
              {!openaiAvailable && (
                <span className="text-xs text-gray-500">Not configured</span>
              )}
            </div>
          </button>
        )}
      </div>
    </div>
  );
}
