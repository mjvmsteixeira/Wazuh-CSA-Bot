import { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { AlertCircle, Search, CheckSquare, Square, X, CheckCircle } from 'lucide-react';
import { SCACheck } from '../services/api';

interface Props {
  checks: SCACheck[];
  onAnalyze: (check: SCACheck) => void;
  onAnalyzeBatch?: (checks: SCACheck[]) => void;
  analyzedCheckIds?: Set<number>; // IDs of checks that have been analyzed
}

export default function ChecksList({ checks, onAnalyze, onAnalyzeBatch, analyzedCheckIds }: Props) {
  const { t } = useTranslation();
  const [selectedChecks, setSelectedChecks] = useState<Set<number>>(new Set());
  const [sortBy, setSortBy] = useState<'id' | 'title' | 'compliance'>('id');
  const [filterFramework, setFilterFramework] = useState<string>('all');
  const [titleFilter, setTitleFilter] = useState<string>('');

  // Helper to check if a check was analyzed
  const isAnalyzed = (checkId: number): boolean => {
    return analyzedCheckIds?.has(checkId) ?? false;
  };

  // Helper function to extract compliance frameworks with values
  const getComplianceData = (compliance?: Array<{ key: string; value: string }>): Array<{ key: string; value: string }> => {
    if (!compliance || compliance.length === 0) return [];

    // Debug log
    console.log('Raw compliance data:', compliance);

    // Filter and format compliance data
    const complianceData = compliance
      .filter(item => item && typeof item === 'object' && item.key && item.value)
      .map(item => ({
        key: item.key,
        value: item.value
      }));

    console.log('Extracted compliance data:', complianceData);
    return complianceData;
  };

  // Format framework name for display
  const formatFrameworkName = (key: string): string => {
    return key
      .replace(/_/g, ' ')
      .toUpperCase()
      .replace(/V(\d)/g, 'v$1'); // Keep version numbers lowercase
  };

  // Get all unique compliance frameworks
  const allFrameworks = useMemo(() => {
    const frameworks = new Set<string>();
    checks.forEach(check => {
      const complianceData = getComplianceData(check.compliance);
      complianceData.forEach(item => frameworks.add(item.key));
    });
    return Array.from(frameworks).sort();
  }, [checks]);

  // Filter and sort checks
  const filteredAndSortedChecks = useMemo(() => {
    let result = [...checks];

    // Apply title filter
    if (titleFilter.trim()) {
      const searchTerm = titleFilter.toLowerCase();
      result = result.filter(check =>
        check.title.toLowerCase().includes(searchTerm)
      );
    }

    // Apply framework filter
    if (filterFramework !== 'all') {
      result = result.filter(check => {
        const complianceData = getComplianceData(check.compliance);
        return complianceData.some(item => item.key === filterFramework);
      });
    }

    // Apply sorting
    result.sort((a, b) => {
      switch (sortBy) {
        case 'id':
          return a.id - b.id;
        case 'title':
          return a.title.localeCompare(b.title);
        case 'compliance':
          const aFrameworks = getComplianceData(a.compliance).length;
          const bFrameworks = getComplianceData(b.compliance).length;
          return bFrameworks - aFrameworks; // More frameworks first
        default:
          return 0;
      }
    });

    return result;
  }, [checks, filterFramework, sortBy, titleFilter]);

  // Toggle individual check selection
  const toggleCheck = (checkId: number) => {
    const newSelected = new Set(selectedChecks);
    if (newSelected.has(checkId)) {
      newSelected.delete(checkId);
    } else {
      newSelected.add(checkId);
    }
    setSelectedChecks(newSelected);
  };

  // Toggle all checks
  const toggleAll = () => {
    if (selectedChecks.size === filteredAndSortedChecks.length) {
      setSelectedChecks(new Set());
    } else {
      setSelectedChecks(new Set(filteredAndSortedChecks.map(c => c.id)));
    }
  };

  // Handle batch analysis
  const handleBatchAnalysis = () => {
    if (!onAnalyzeBatch || selectedChecks.size === 0) return;
    const selectedChecksList = filteredAndSortedChecks.filter(c => selectedChecks.has(c.id));
    onAnalyzeBatch(selectedChecksList);
  };

  return (
    <div className="space-y-4">
      {/* Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
        <div className="flex items-center gap-4 flex-wrap">
          {/* Title Search Filter */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Search:</label>
            <div className="relative">
              <input
                type="text"
                value={titleFilter}
                onChange={(e) => setTitleFilter(e.target.value)}
                placeholder="Filter by title..."
                className="text-sm border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 pl-8 pr-3 py-1.5 w-64"
              />
              <Search className="w-4 h-4 text-gray-400 absolute left-2.5 top-1/2 transform -translate-y-1/2" />
              {titleFilter && (
                <button
                  onClick={() => setTitleFilter('')}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Sort By */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Sort by:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'id' | 'title' | 'compliance')}
              className="text-sm border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="id">Check ID</option>
              <option value="title">Title</option>
              <option value="compliance">Compliance Frameworks</option>
            </select>
          </div>

          {/* Filter by Framework */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Framework:</label>
            <select
              value={filterFramework}
              onChange={(e) => setFilterFramework(e.target.value)}
              className="text-sm border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="all">All Frameworks</option>
              {allFrameworks.map(fw => (
                <option key={fw} value={fw}>{formatFrameworkName(fw)}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Batch Actions */}
        {onAnalyzeBatch && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-600">
              {selectedChecks.size} selected
            </span>
            <button
              onClick={handleBatchAnalysis}
              disabled={selectedChecks.size === 0}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Search className="w-4 h-4 mr-2" />
              {t('dashboard.analyzeSelected')}
            </button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {onAnalyzeBatch && (
                <th className="px-6 py-3 text-left">
                  <button
                    onClick={toggleAll}
                    className="text-gray-500 hover:text-gray-700"
                    title={selectedChecks.size === filteredAndSortedChecks.length ? 'Deselect all' : 'Select all'}
                  >
                    {selectedChecks.size === filteredAndSortedChecks.length ? (
                      <CheckSquare className="w-5 h-5" />
                    ) : (
                      <Square className="w-5 h-5" />
                    )}
                  </button>
                </th>
              )}
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('dashboard.checkId')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('dashboard.title')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Compliance
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('dashboard.actions')}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAndSortedChecks.map((check) => {
              const complianceData = getComplianceData(check.compliance);
              const isSelected = selectedChecks.has(check.id);
              const analyzed = isAnalyzed(check.id);

              return (
                <tr
                  key={check.id}
                  className={`hover:bg-gray-50 ${isSelected ? 'bg-blue-50' : ''}`}
                >
                  {onAnalyzeBatch && (
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => toggleCheck(check.id)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        {isSelected ? (
                          <CheckSquare className="w-5 h-5 text-blue-600" />
                        ) : (
                          <Square className="w-5 h-5" />
                        )}
                      </button>
                    </td>
                  )}
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {check.id}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="flex items-start">
                      <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 mr-2 flex-shrink-0" />
                      <span className="line-clamp-2">{check.title}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {complianceData.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {complianceData.map((item, idx) => (
                          <span
                            key={idx}
                            className="inline-flex px-2 py-1 text-xs font-semibold rounded-md bg-blue-100 text-blue-800"
                            title={`${formatFrameworkName(item.key)}: ${item.value}`}
                          >
                            {formatFrameworkName(item.key)}: {item.value}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-xs text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {analyzed ? (
                      <button
                        onClick={() => onAnalyze(check)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                        title="Click to re-analyze"
                      >
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Analyzed
                      </button>
                    ) : (
                      <button
                        onClick={() => onAnalyze(check)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                      >
                        <Search className="w-4 h-4 mr-1" />
                        {t('dashboard.analyze')}
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
