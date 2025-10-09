import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { CheckCircle, XCircle, Loader2, AlertCircle, Server, Cpu, Cloud, ZoomIn, X } from 'lucide-react';
import api from '../services/api';

interface StatusIndicatorProps {
  icon: React.ReactNode;
  label: string;
  status: 'online' | 'offline' | 'unknown';
  details?: string;
  error?: string;
}

function StatusIndicator({ icon, label, status, details, error }: StatusIndicatorProps) {
  const [showErrorModal, setShowErrorModal] = useState(false);

  const getStatusIcon = () => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'offline':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'online':
        return <span className="font-medium text-green-600">Online</span>;
      case 'offline':
        return <span className="font-medium text-red-600">Offline</span>;
      default:
        return <span className="font-medium text-gray-500">Unknown</span>;
    }
  };

  return (
    <>
      <div className="flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow">
        <div className="flex-shrink-0 mt-0.5">
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="text-sm font-medium text-gray-900">{label}</span>
          </div>
          <div className="mt-1 text-sm">
            Status: {getStatusText()}
          </div>
          {details && (
            <div className="mt-1 text-xs text-gray-500 truncate" title={details}>
              {details}
            </div>
          )}
          {error && (
            <div className="mt-1 flex items-center gap-2">
              <button
                onClick={() => setShowErrorModal(true)}
                className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-red-700 bg-red-50 hover:bg-red-100 rounded border border-red-200 transition-colors"
              >
                <AlertCircle className="w-3 h-3" />
                Error Details
                <ZoomIn className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Error Details Modal */}
      {showErrorModal && error && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
            <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Error Details - {label}
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
                  {error}
                </pre>
              </div>
              {details && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Connection Details:</h4>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                    <code className="text-sm text-gray-800">{details}</code>
                  </div>
                </div>
              )}
            </div>
            <div className="border-t border-gray-200 px-6 py-4 flex justify-end">
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

export default function SystemStatus() {
  const { data: status, isLoading } = useQuery({
    queryKey: ['system-status'],
    queryFn: async () => {
      const response = await api.getSystemStatus();
      return response;
    },
    refetchInterval: 30000, // Refresh every 30s
  });

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 p-4 bg-gray-50 rounded-lg">
        <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
        <span className="text-sm text-gray-600">Checking system status...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* AI Mode Badge */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-gray-700">AI Mode:</span>
        <div className="px-3 py-1 bg-purple-100 text-purple-800 rounded-md text-sm font-medium">
          {status?.ai_mode?.toUpperCase() || 'UNKNOWN'}
        </div>
      </div>

      {/* Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Wazuh API Status */}
        <StatusIndicator
          icon={<Server className="w-5 h-5 text-blue-600" />}
          label="Wazuh API"
          status={status?.wazuh?.available ? 'online' : 'offline'}
          details={status?.wazuh?.url}
          error={status?.wazuh?.error}
        />

        {/* Local LLM Status - Only show if enabled */}
        {status?.vllm?.enabled && (
          <StatusIndicator
            icon={<Cpu className="w-5 h-5 text-green-600" />}
            label="Local LLM (vLLM)"
            status={status?.vllm?.available ? 'online' : 'offline'}
            details={status?.vllm?.model}
            error={status?.vllm?.error}
          />
        )}

        {/* OpenAI Status - Only show if enabled */}
        {status?.openai?.enabled && (
          <StatusIndicator
            icon={<Cloud className="w-5 h-5 text-blue-500" />}
            label="OpenAI API"
            status={status?.openai?.available ? 'online' : 'offline'}
            details={status?.openai?.model}
            error={status?.openai?.error}
          />
        )}
      </div>

      {/* Additional Info */}
      <div className="text-xs text-gray-500 mt-2">
        Status refreshes automatically every 30 seconds
      </div>
    </div>
  );
}
