import React, { useState, useEffect } from 'react';
import { api, CacheStats as CacheStatsType } from '../services/api';

interface CacheStatsProps {
  language: 'pt' | 'en';
}

const CacheStats: React.FC<CacheStatsProps> = ({ language }) => {
  const [stats, setStats] = useState<CacheStatsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const translations = {
    en: {
      title: 'Cache Statistics',
      totalAnalyses: 'Total Analyses',
      completed: 'Completed',
      failed: 'Failed',
      cachedValid: 'Valid Cache Entries',
      cacheStatus: 'Cache Status',
      enabled: 'Enabled',
      disabled: 'Disabled',
      cacheTTL: 'Cache TTL',
      hours: 'hours',
      hitRate: 'Cache Hit Rate',
      loadingStats: 'Loading statistics...',
      errorLoading: 'Error loading statistics',
      refresh: 'Refresh',
    },
    pt: {
      title: 'Estatísticas de Cache',
      totalAnalyses: 'Total de Análises',
      completed: 'Concluídas',
      failed: 'Falhadas',
      cachedValid: 'Entradas de Cache Válidas',
      cacheStatus: 'Estado do Cache',
      enabled: 'Ativado',
      disabled: 'Desativado',
      cacheTTL: 'TTL do Cache',
      hours: 'horas',
      hitRate: 'Taxa de Acerto do Cache',
      loadingStats: 'Carregando estatísticas...',
      errorLoading: 'Erro ao carregar estatísticas',
      refresh: 'Atualizar',
    },
  };

  const t = translations[language];

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await api.getCacheStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Failed to load cache stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">{t.loadingStats}</span>
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-red-600 text-center">
          {t.errorLoading}: {error}
        </div>
      </div>
    );
  }

  const hitRate =
    stats.completed > 0
      ? ((stats.cached_valid / stats.completed) * 100).toFixed(1)
      : '0.0';

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">{t.title}</h3>
        <button
          onClick={loadStats}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center"
        >
          <svg
            className="w-4 h-4 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          {t.refresh}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          {/* Total Analyses */}
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="text-sm font-medium text-blue-900 mb-1">
              {t.totalAnalyses}
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {stats.total_analyses}
            </div>
          </div>

          {/* Completed */}
          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <div className="text-sm font-medium text-green-900 mb-1">
              {t.completed}
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
          </div>

          {/* Failed */}
          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
            <div className="text-sm font-medium text-red-900 mb-1">{t.failed}</div>
            <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
          </div>

          {/* Valid Cache Entries */}
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="text-sm font-medium text-purple-900 mb-1">
              {t.cachedValid}
            </div>
            <div className="text-2xl font-bold text-purple-600">
              {stats.cached_valid}
            </div>
          </div>

          {/* Cache Hit Rate */}
          <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
            <div className="text-sm font-medium text-indigo-900 mb-1">
              {t.hitRate}
            </div>
            <div className="text-2xl font-bold text-indigo-600">{hitRate}%</div>
          </div>

          {/* Cache TTL */}
          <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
            <div className="text-sm font-medium text-yellow-900 mb-1">{t.cacheTTL}</div>
            <div className="text-2xl font-bold text-yellow-600">
              {stats.cache_ttl_hours}
              <span className="text-sm font-normal ml-1">{t.hours}</span>
            </div>
          </div>
        </div>

        {/* Cache Status Badge */}
        <div className="flex items-center justify-center">
          <div
            className={`px-4 py-2 rounded-full text-sm font-semibold ${
              stats.cache_enabled
                ? 'bg-green-100 text-green-800 border border-green-300'
                : 'bg-gray-100 text-gray-800 border border-gray-300'
            }`}
          >
            {t.cacheStatus}:{' '}
            {stats.cache_enabled ? t.enabled.toUpperCase() : t.disabled.toUpperCase()}
          </div>
        </div>

        {/* Visual Progress Bar for Hit Rate */}
        {stats.completed > 0 && (
          <div className="mt-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>{t.hitRate}</span>
              <span>{hitRate}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${hitRate}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CacheStats;
