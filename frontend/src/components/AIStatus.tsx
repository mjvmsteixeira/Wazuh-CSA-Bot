import { useQuery } from '@tanstack/react-query';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import api from '../services/api';

export default function AIStatus() {
  const { data: status, isLoading } = useQuery({
    queryKey: ['ai-status'],
    queryFn: async () => {
      const response = await api.getAIStatus();
      return response;
    },
    refetchInterval: 30000, // Refresh every 30s
  });

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span>Checking AI status...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-4 text-sm">
      {/* AI Mode Badge */}
      {status?.ai_mode && (
        <div className="px-2 py-1 bg-purple-100 text-purple-800 rounded-md text-xs font-medium">
          Mode: {status.ai_mode.toUpperCase()}
        </div>
      )}

      {/* vLLM Status - Only show if enabled */}
      {status?.vllm?.enabled && (
        <div className="flex items-center gap-2">
          {status?.vllm?.available ? (
            <>
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-gray-700">
                Local LLM: <span className="font-medium text-green-600">Online</span>
              </span>
            </>
          ) : (
            <>
              <XCircle className="w-4 h-4 text-gray-400" />
              <span className="text-gray-500">
                Local LLM: <span className="font-medium">Offline</span>
              </span>
            </>
          )}
        </div>
      )}

      {/* OpenAI Status - Only show if enabled */}
      {status?.openai?.enabled && (
        <div className="flex items-center gap-2">
          {status?.openai?.available ? (
            <>
              <CheckCircle className="w-4 h-4 text-blue-500" />
              <span className="text-gray-700">
                OpenAI: <span className="font-medium text-blue-600">Configured</span>
              </span>
            </>
          ) : (
            <>
              <XCircle className="w-4 h-4 text-gray-400" />
              <span className="text-gray-500">
                OpenAI: <span className="font-medium">Not Configured</span>
              </span>
            </>
          )}
        </div>
      )}
    </div>
  );
}
