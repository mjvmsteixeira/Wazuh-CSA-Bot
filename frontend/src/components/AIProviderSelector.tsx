import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { Brain, Cloud } from 'lucide-react';
import api from '../services/api';

interface Props {
  selectedProvider: 'vllm' | 'openai';
  onSelectProvider: (provider: 'vllm' | 'openai') => void;
}

export default function AIProviderSelector({ selectedProvider, onSelectProvider }: Props) {
  const { t } = useTranslation();

  // Get AI status to check which providers are enabled
  const { data: status } = useQuery({
    queryKey: ['ai-status'],
    queryFn: async () => {
      const response = await api.getAIStatus();
      return response;
    },
  });

  const vllmEnabled = status?.vllm?.enabled ?? true;
  const openaiEnabled = status?.openai?.enabled ?? true;

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {t('analysis.selectProvider')}
      </label>

      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={() => onSelectProvider('vllm')}
          disabled={!vllmEnabled}
          className={`flex items-center justify-center space-x-2 px-4 py-3 rounded-lg border-2 transition-colors ${
            selectedProvider === 'vllm'
              ? 'border-primary-500 bg-primary-50 text-primary-700'
              : vllmEnabled
              ? 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              : 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
          }`}
        >
          <Brain className="w-5 h-5" />
          <span className="text-sm font-medium">{t('analysis.local')}</span>
        </button>

        <button
          onClick={() => onSelectProvider('openai')}
          disabled={!openaiEnabled}
          className={`flex items-center justify-center space-x-2 px-4 py-3 rounded-lg border-2 transition-colors ${
            selectedProvider === 'openai'
              ? 'border-primary-500 bg-primary-50 text-primary-700'
              : openaiEnabled
              ? 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              : 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
          }`}
        >
          <Cloud className="w-5 h-5" />
          <span className="text-sm font-medium">{t('analysis.openai')}</span>
        </button>
      </div>
    </div>
  );
}
