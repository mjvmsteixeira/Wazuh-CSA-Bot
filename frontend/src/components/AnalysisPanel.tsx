import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { X, Copy, Download, Loader2, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import api, { SCACheck } from '../services/api';

interface Props {
  check: SCACheck;
  agentId: string;
  agentName: string;
  policyId: string;
  aiProvider: 'vllm' | 'openai';
  language: 'pt' | 'en';
  onClose: () => void;
}

export default function AnalysisPanel({
  check,
  agentId,
  agentName,
  policyId,
  aiProvider,
  language,
  onClose,
}: Props) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  // Analysis mutation
  const analysisMutation = useMutation({
    mutationFn: () =>
      api.analyzeCheck({
        agent_id: agentId,
        policy_id: policyId,
        check_id: check.id,
        language,
        ai_provider: aiProvider,
      }),
  });

  // PDF generation mutation
  const pdfMutation = useMutation({
    mutationFn: (reportText: string) =>
      api.generatePDF({
        agent_name: agentName,
        check_id: check.id,
        report_text: reportText,
        language,
      }),
    onSuccess: (data) => {
      window.open(api.downloadPDF(data.filename), '_blank');
    },
  });

  const handleCopy = async () => {
    if (analysisMutation.data?.report) {
      await navigator.clipboard.writeText(analysisMutation.data.report);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownloadPDF = () => {
    if (analysisMutation.data?.report) {
      pdfMutation.mutate(analysisMutation.data.report);
    }
  };

  // Auto-start analysis
  if (!analysisMutation.data && !analysisMutation.isPending && !analysisMutation.isError) {
    analysisMutation.mutate();
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-gray-900">
                {t('analysis.title')} - Check #{check.id}
              </h3>
              {/* AI Provider Badge */}
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  aiProvider === 'vllm'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-green-100 text-green-800'
                }`}
              >
                {aiProvider === 'vllm' ? '🖥️ Local LLM' : '☁️ OpenAI'}
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-1">{check.title}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500 focus:outline-none"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {analysisMutation.isPending && (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
              <p className="text-gray-600">{t('analysis.analyzing')}</p>
              <p className="text-sm text-gray-500 mt-2">
                Using {aiProvider === 'vllm' ? 'Local LLM (vLLM)' : 'OpenAI (Cloud)'}
              </p>
            </div>
          )}

          {analysisMutation.isError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {t('analysis.error')}
            </div>
          )}

          {analysisMutation.data && (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{analysisMutation.data.report}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Footer */}
        {analysisMutation.data && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-end space-x-3">
            <button
              onClick={handleCopy}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {copied ? (
                <>
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 mr-2" />
                  {t('analysis.copyReport')}
                </>
              )}
            </button>

            <button
              onClick={handleDownloadPDF}
              disabled={pdfMutation.isPending}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {pdfMutation.isPending ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Download className="w-4 h-4 mr-2" />
              )}
              {t('analysis.downloadPDF')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
