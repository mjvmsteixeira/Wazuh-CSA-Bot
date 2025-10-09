import React, { useState, useEffect } from 'react';
import { api, AnalysisHistory, AnalysisHistoryListResponse } from '../services/api';
import ReactMarkdown from 'react-markdown';
import ScriptViewer from './ScriptViewer';

interface HistoryPanelProps {
  agentId: string;
  agentName: string;
  checkId?: number;
  language: 'pt' | 'en';
}

const HistoryPanel: React.FC<HistoryPanelProps> = ({
  agentId,
  agentName,
  checkId,
  language,
}) => {
  const [history, setHistory] = useState<AnalysisHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisHistory | null>(null);
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'completed' | 'failed'>('all');
  const [page, setPage] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const limit = 10;

  const translations = {
    en: {
      title: 'Analysis History',
      checkHistory: 'Check History',
      noHistory: 'No analysis history found',
      loadingHistory: 'Loading history...',
      errorLoading: 'Error loading history',
      status: 'Status',
      all: 'All',
      pending: 'Pending',
      completed: 'Completed',
      failed: 'Failed',
      provider: 'Provider',
      date: 'Date',
      execTime: 'Execution Time',
      viewReport: 'View Report',
      closeReport: 'Close Report',
      deleteAnalysis: 'Delete',
      confirmDelete: 'Are you sure you want to delete this analysis?',
      cached: 'CACHED',
      seconds: 's',
      page: 'Page',
      of: 'of',
      previous: 'Previous',
      next: 'Next',
      downloadPDF: 'Download PDF',
    },
    pt: {
      title: 'Histórico de Análises',
      checkHistory: 'Histórico da Verificação',
      noHistory: 'Nenhum histórico de análise encontrado',
      loadingHistory: 'Carregando histórico...',
      errorLoading: 'Erro ao carregar histórico',
      status: 'Estado',
      all: 'Todos',
      pending: 'Pendente',
      completed: 'Concluído',
      failed: 'Falhou',
      provider: 'Provedor',
      date: 'Data',
      execTime: 'Tempo de Execução',
      viewReport: 'Ver Relatório',
      closeReport: 'Fechar Relatório',
      deleteAnalysis: 'Eliminar',
      confirmDelete: 'Tem certeza de que deseja eliminar esta análise?',
      cached: 'CACHE',
      seconds: 's',
      page: 'Página',
      of: 'de',
      previous: 'Anterior',
      next: 'Próximo',
      downloadPDF: 'Baixar PDF',
    },
  };

  const t = translations[language];

  useEffect(() => {
    loadHistory();
  }, [agentId, checkId, statusFilter, page]);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);

    try {
      let response: AnalysisHistoryListResponse;

      if (checkId) {
        response = await api.getCheckHistory(agentId, checkId, limit);
      } else {
        const statusParam = statusFilter === 'all' ? undefined : statusFilter;
        response = await api.getAgentHistory(agentId, limit, page * limit, statusParam);
      }

      setHistory(response.analyses);
      setTotalCount(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (analysisId: string) => {
    if (!confirm(t.confirmDelete)) return;

    try {
      await api.deleteAnalysis(analysisId);
      loadHistory();
      if (selectedAnalysis?.id === analysisId) {
        setSelectedAnalysis(null);
      }
    } catch (err) {
      console.error('Failed to delete analysis:', err);
      alert('Failed to delete analysis');
    }
  };

  const handleDownloadPDF = async (analysis: AnalysisHistory) => {
    try {
      const response = await api.generatePDF({
        agent_name: agentName,
        check_id: analysis.check_id,
        report_text: analysis.report_text,
        language: analysis.language,
      });
      const downloadUrl = api.downloadPDF(response.filename);
      window.open(downloadUrl, '_blank');
    } catch (err) {
      console.error('Failed to generate PDF:', err);
      alert('Failed to generate PDF report');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString(language === 'pt' ? 'pt-BR' : 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      completed: 'bg-green-100 text-green-800 border-green-300',
      failed: 'bg-red-100 text-red-800 border-red-300',
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    };

    return (
      <span
        className={`px-2 py-1 text-xs font-semibold rounded border ${
          statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {t[status as keyof typeof t] || status}
      </span>
    );
  };

  const totalPages = Math.ceil(totalCount / limit);

  if (loading && history.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">{t.loadingHistory}</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-red-600">
          {t.errorLoading}: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            {checkId ? t.checkHistory : t.title}
          </h3>
          {!checkId && (
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as any);
                setPage(0);
              }}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">{t.all}</option>
              <option value="completed">{t.completed}</option>
              <option value="failed">{t.failed}</option>
              <option value="pending">{t.pending}</option>
            </select>
          )}
        </div>
      </div>

      {/* History List */}
      <div className="divide-y divide-gray-200">
        {history.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">{t.noHistory}</div>
        ) : (
          history.map((analysis) => (
            <div
              key={analysis.id}
              className="px-6 py-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="text-sm font-medium text-gray-900 truncate">
                      {analysis.check_title}
                    </h4>
                    {getStatusBadge(analysis.status)}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-600">
                    <div>
                      <span className="font-medium">{t.date}:</span>{' '}
                      {formatDate(analysis.analysis_date)}
                    </div>
                    <div>
                      <span className="font-medium">{t.provider}:</span>{' '}
                      {analysis.ai_provider.toUpperCase()}
                    </div>
                    {analysis.execution_time_seconds && (
                      <div>
                        <span className="font-medium">{t.execTime}:</span>{' '}
                        {analysis.execution_time_seconds.toFixed(2)}
                        {t.seconds}
                      </div>
                    )}
                    <div>
                      <span className="font-medium">Check ID:</span> {analysis.check_id}
                    </div>
                  </div>

                  {analysis.error_message && (
                    <div className="mt-2 text-xs text-red-600">
                      Error: {analysis.error_message}
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  {analysis.status === 'completed' && (
                    <>
                      <button
                        onClick={() => setSelectedAnalysis(analysis)}
                        className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded border border-blue-300 transition-colors"
                      >
                        {t.viewReport}
                      </button>
                      <button
                        onClick={() => handleDownloadPDF(analysis)}
                        className="px-3 py-1 text-sm text-green-600 hover:bg-green-50 rounded border border-green-300 transition-colors"
                      >
                        {t.downloadPDF}
                      </button>
                    </>
                  )}
                  <button
                    onClick={() => handleDelete(analysis.id)}
                    className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded border border-red-300 transition-colors"
                  >
                    {t.deleteAnalysis}
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {!checkId && totalPages > 1 && (
        <div className="border-t border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {t.page} {page + 1} {t.of} {totalPages}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              {t.previous}
            </button>
            <button
              onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
              disabled={page >= totalPages - 1}
              className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              {t.next}
            </button>
          </div>
        </div>
      )}

      {/* Report Modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
            <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedAnalysis.check_title}
              </h3>
              <button
                onClick={() => setSelectedAnalysis(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-6 py-4">
              <div className="prose max-w-none">
                <ReactMarkdown>{selectedAnalysis.report_text}</ReactMarkdown>
              </div>

              {/* Remediation Script */}
              {selectedAnalysis.remediation_script && (
                <div className="mt-6">
                  <ScriptViewer
                    script={selectedAnalysis.remediation_script}
                    checkTitle={selectedAnalysis.check_title}
                  />
                </div>
              )}
            </div>
            <div className="border-t border-gray-200 px-6 py-4 flex justify-end space-x-2">
              <button
                onClick={() => handleDownloadPDF(selectedAnalysis)}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
              >
                {t.downloadPDF}
              </button>
              <button
                onClick={() => setSelectedAnalysis(null)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
              >
                {t.closeReport}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryPanel;
