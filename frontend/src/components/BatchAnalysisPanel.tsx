import { useState } from 'react';
import { X, CheckCircle, XCircle, Loader, Download } from 'lucide-react';
import { SCACheck } from '../services/api';
import api from '../services/api';

interface Props {
  checks: SCACheck[];
  agentId: string;
  agentName: string;
  policyId: string;
  aiProvider: 'vllm' | 'openai';
  language: 'pt' | 'en';
  onClose: () => void;
}

interface AnalysisResult {
  checkId: number;
  title: string;
  status: 'pending' | 'analyzing' | 'completed' | 'error';
  report?: string;
  error?: string;
}

export default function BatchAnalysisPanel({
  checks,
  agentId,
  agentName,
  policyId,
  aiProvider,
  language,
  onClose,
}: Props) {
  const [results, setResults] = useState<AnalysisResult[]>(
    checks.map(c => ({
      checkId: c.id,
      title: c.title,
      status: 'pending',
    }))
  );
  const [isRunning, setIsRunning] = useState(false);
  const exportFormat = import.meta.env.VITE_EXPORT_FORMAT || 'pdf';

  const startBatchAnalysis = async () => {
    setIsRunning(true);

    for (let i = 0; i < checks.length; i++) {
      const check = checks[i];

      // Update status to analyzing
      setResults(prev =>
        prev.map(r =>
          r.checkId === check.id ? { ...r, status: 'analyzing' } : r
        )
      );

      try {
        // Analyze individual check
        const response = await api.analyzeCheck({
          agent_id: agentId,
          policy_id: policyId,
          check_id: check.id,
          language,
          ai_provider: aiProvider,
        });

        // Update with result
        setResults(prev =>
          prev.map(r =>
            r.checkId === check.id
              ? { ...r, status: 'completed', report: response.report }
              : r
          )
        );
      } catch (error: any) {
        // Update with error
        setResults(prev =>
          prev.map(r =>
            r.checkId === check.id
              ? { ...r, status: 'error', error: error.message || 'Analysis failed' }
              : r
          )
        );
      }
    }

    setIsRunning(false);
  };

  const getStatusIcon = (status: AnalysisResult['status']) => {
    switch (status) {
      case 'pending':
        return <div className="w-5 h-5 rounded-full border-2 border-gray-300" />;
      case 'analyzing':
        return <Loader className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />;
    }
  };

  const getStatusColor = (status: AnalysisResult['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-50';
      case 'analyzing':
        return 'bg-blue-50';
      case 'completed':
        return 'bg-green-50';
      case 'error':
        return 'bg-red-50';
    }
  };

  const completedCount = results.filter(r => r.status === 'completed').length;
  const errorCount = results.filter(r => r.status === 'error').length;
  const progress = ((completedCount + errorCount) / results.length) * 100;

  const downloadAllReports = async () => {
    const successfulResults = results.filter(r => r.status === 'completed' && r.report);
    const exportFormat = import.meta.env.VITE_EXPORT_FORMAT || 'pdf';

    if (exportFormat === 'pdf') {
      // Generate PDFs for each successful result
      for (const result of successfulResults) {
        try {
          const response = await api.generatePDF({
            agent_name: agentName,
            check_id: result.checkId,
            report_text: result.report || '',
            language,
          });

          // Download the PDF
          const downloadUrl = api.downloadPDF(response.filename);
          window.open(downloadUrl, '_blank');

          // Small delay between downloads
          await new Promise(resolve => setTimeout(resolve, 500));
        } catch (error) {
          console.error(`Failed to generate PDF for check ${result.checkId}:`, error);
        }
      }
    } else {
      // Markdown export (original behavior)
      let combinedReport = `# Batch Analysis Report - ${agentName}\n\n`;
      combinedReport += `**Date:** ${new Date().toLocaleString()}\n`;
      combinedReport += `**Total Checks:** ${checks.length}\n`;
      combinedReport += `**Successful:** ${completedCount}\n`;
      combinedReport += `**Failed:** ${errorCount}\n\n`;
      combinedReport += `---\n\n`;

      successfulResults.forEach((result, idx) => {
        combinedReport += `\n## Check ${idx + 1}: ${result.title}\n\n`;
        combinedReport += result.report;
        combinedReport += `\n\n---\n\n`;
      });

      const blob = new Blob([combinedReport], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `batch-analysis-${agentName}-${Date.now()}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Batch Analysis
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Analyzing {checks.length} checks for {agentName}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
            disabled={isRunning}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4 border-b">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Progress: {completedCount + errorCount} / {results.length}
            </span>
            <span className="text-sm text-gray-500">
              {progress.toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex gap-4 mt-2 text-sm">
            <span className="text-green-600">✓ {completedCount} completed</span>
            <span className="text-red-600">✗ {errorCount} failed</span>
          </div>
        </div>

        {/* Results List */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-2">
            {results.map((result) => (
              <div
                key={result.checkId}
                className={`p-4 rounded-lg border ${getStatusColor(result.status)}`}
              >
                <div className="flex items-start gap-3">
                  {getStatusIcon(result.status)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">
                        Check {result.checkId}
                      </span>
                      {result.status === 'analyzing' && (
                        <span className="text-xs text-blue-600 font-medium">
                          Analyzing...
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1 truncate">
                      {result.title}
                    </p>
                    {result.error && (
                      <p className="text-sm text-red-600 mt-2">
                        Error: {result.error}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={isRunning}
          >
            {isRunning ? 'Running...' : 'Close'}
          </button>
          <div className="flex gap-3">
            {completedCount > 0 && !isRunning && (
              <button
                onClick={downloadAllReports}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Download className="w-4 h-4 mr-2" />
                {exportFormat === 'pdf'
                  ? `Download All as PDF (${completedCount})`
                  : 'Download Combined Report (MD)'}
              </button>
            )}
            {!isRunning && completedCount + errorCount === 0 && (
              <button
                onClick={startBatchAnalysis}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Start Analysis
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
