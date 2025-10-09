import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Copy, Download, CheckCircle, AlertTriangle, Terminal, Clock } from 'lucide-react';
import { RemediationScript } from '../services/api';

interface Props {
  script: RemediationScript;
  checkTitle?: string;
}

export default function ScriptViewer({ script, checkTitle }: Props) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  const handleCopyScript = async () => {
    await navigator.clipboard.writeText(script.script_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadScript = () => {
    const extensions: Record<string, string> = {
      bash: 'sh',
      powershell: 'ps1',
      python: 'py',
    };
    const ext = extensions[script.script_language] || 'txt';
    const filename = `remediation_${checkTitle?.replace(/\s+/g, '_') || 'script'}.${ext}`;

    const blob = new Blob([script.script_content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getLanguageColor = () => {
    switch (script.script_language) {
      case 'bash':
        return 'bg-green-100 text-green-800';
      case 'powershell':
        return 'bg-blue-100 text-blue-800';
      case 'python':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="mt-6 border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5" />
            <h4 className="font-semibold">
              {t('script.title', { defaultValue: 'Automated Remediation Script' })}
            </h4>
          </div>
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getLanguageColor()}`}>
            {script.script_language.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Metadata */}
      <div className="px-4 py-3 bg-white border-b border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
          {/* Requires Root */}
          <div className="flex items-center gap-2">
            {script.requires_root ? (
              <>
                <AlertTriangle className="w-4 h-4 text-yellow-600" />
                <span className="text-yellow-700 font-medium">
                  {t('script.requiresRoot', { defaultValue: 'Requires Root/Admin' })}
                </span>
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-green-700">
                  {t('script.noRootRequired', { defaultValue: 'No Root Required' })}
                </span>
              </>
            )}
          </div>

          {/* Estimated Duration */}
          {script.estimated_duration && (
            <div className="flex items-center gap-2 text-gray-600">
              <Clock className="w-4 h-4" />
              <span>{script.estimated_duration}</span>
            </div>
          )}

          {/* Validation Command */}
          {script.validation_command && (
            <div className="text-gray-600">
              <span className="font-medium">
                {t('script.validation', { defaultValue: 'Validation:' })}
              </span>{' '}
              <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                {script.validation_command}
              </code>
            </div>
          )}
        </div>
      </div>

      {/* Risks Warning */}
      {script.risks && script.risks.length > 0 && (
        <div className="px-4 py-3 bg-yellow-50 border-b border-yellow-200">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h5 className="text-sm font-semibold text-yellow-800 mb-1">
                {t('script.risks', { defaultValue: 'Potential Risks' })}
              </h5>
              <ul className="text-sm text-yellow-700 space-y-1">
                {script.risks.map((risk, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>{risk}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Script Content - Terminal Style */}
      <div className="relative bg-gray-900">
        {/* Terminal Header */}
        <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <span className="text-xs text-gray-400 font-mono ml-2">
              remediation.{script.script_language === 'bash' ? 'sh' : script.script_language === 'powershell' ? 'ps1' : 'py'}
            </span>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <button
              onClick={handleCopyScript}
              className="inline-flex items-center px-2.5 py-1 text-xs font-medium rounded bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors"
              title={t('script.copyScript', { defaultValue: 'Copy Script' })}
            >
              {copied ? (
                <>
                  <CheckCircle className="w-3 h-3 mr-1" />
                  {t('script.copied', { defaultValue: 'Copied!' })}
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3 mr-1" />
                  {t('script.copy', { defaultValue: 'Copy' })}
                </>
              )}
            </button>

            <button
              onClick={handleDownloadScript}
              className="inline-flex items-center px-2.5 py-1 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-500 transition-colors"
              title={t('script.downloadScript', { defaultValue: 'Download Script' })}
            >
              <Download className="w-3 h-3 mr-1" />
              {t('script.download', { defaultValue: 'Download' })}
            </button>
          </div>
        </div>

        {/* Terminal Content */}
        <pre className="px-4 py-3 text-green-400 font-mono text-sm overflow-x-auto max-h-96 bg-gray-900">
          <code className="text-green-400">{script.script_content}</code>
        </pre>
      </div>

      {/* Footer Note */}
      <div className="px-4 py-2 bg-gray-100 border-t border-gray-200">
        <p className="text-xs text-gray-600">
          ⚠️ {t('script.warning', {
            defaultValue: 'Review the script carefully before execution. Test in a safe environment first.'
          })}
        </p>
      </div>
    </div>
  );
}
