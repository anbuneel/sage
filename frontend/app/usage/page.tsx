'use client';

import { useEffect, useState } from 'react';
import { getUsageSummary, UsageSummary } from '@/lib/api';
import { ChartBar, Clock, CurrencyDollar, Lightning, Spinner } from '@phosphor-icons/react';

export default function UsagePage() {
  const [summary, setSummary] = useState<UsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(7);

  useEffect(() => {
    async function fetchUsage() {
      setLoading(true);
      setError(null);
      try {
        const data = await getUsageSummary(days);
        setSummary(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load usage data');
      } finally {
        setLoading(false);
      }
    }
    fetchUsage();
  }, [days]);

  const formatNumber = (n: number) => n.toLocaleString();
  const formatCost = (n: number) => `$${n.toFixed(4)}`;
  const formatDuration = (ms: number) => ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`;

  if (loading) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <div className="flex items-center gap-3 text-ink-light">
          <Spinner className="w-6 h-6 animate-spin" />
          <span>Loading usage data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">Error Loading Usage</h2>
          <p className="text-red-600">{error}</p>
          <p className="text-red-500 text-sm mt-2">
            Make sure the database is configured and the backend is running.
          </p>
        </div>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  return (
    <div className="min-h-screen bg-paper">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-display text-3xl text-ink-dark">LLM Usage Dashboard</h1>
            <p className="text-ink-light mt-1">Track token usage and costs across all AI services</p>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-ink-light text-sm">Period:</label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="bg-white border border-sage-light/30 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-sage"
            >
              <option value={1}>Last 24 hours</option>
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg border border-sage-light/30 p-5 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-sage-light/20 rounded-lg">
                <Lightning className="w-5 h-5 text-sage" weight="fill" />
              </div>
              <span className="text-ink-light text-sm">Total Tokens</span>
            </div>
            <div className="text-2xl font-mono font-semibold text-ink-dark">
              {formatNumber(summary.totals.tokens_total)}
            </div>
            <div className="text-xs text-ink-lighter mt-1">
              {formatNumber(summary.totals.tokens_input)} in / {formatNumber(summary.totals.tokens_output)} out
            </div>
          </div>

          <div className="bg-white rounded-lg border border-sage-light/30 p-5 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-gold/20 rounded-lg">
                <CurrencyDollar className="w-5 h-5 text-gold" weight="fill" />
              </div>
              <span className="text-ink-light text-sm">Total Cost</span>
            </div>
            <div className="text-2xl font-mono font-semibold text-ink-dark">
              {formatCost(summary.totals.cost_usd)}
            </div>
            <div className="text-xs text-ink-lighter mt-1">
              ~${(summary.totals.cost_usd / Math.max(1, summary.totals.requests) * 1000).toFixed(2)}/1K requests
            </div>
          </div>

          <div className="bg-white rounded-lg border border-sage-light/30 p-5 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <ChartBar className="w-5 h-5 text-blue-600" weight="fill" />
              </div>
              <span className="text-ink-light text-sm">Total Requests</span>
            </div>
            <div className="text-2xl font-mono font-semibold text-ink-dark">
              {formatNumber(summary.totals.requests)}
            </div>
            <div className="text-xs text-ink-lighter mt-1">
              {summary.by_service.length} service{summary.by_service.length !== 1 ? 's' : ''}
            </div>
          </div>

          <div className="bg-white rounded-lg border border-sage-light/30 p-5 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Clock className="w-5 h-5 text-purple-600" weight="fill" />
              </div>
              <span className="text-ink-light text-sm">Avg Duration</span>
            </div>
            <div className="text-2xl font-mono font-semibold text-ink-dark">
              {formatDuration(summary.totals.avg_duration_ms)}
            </div>
            <div className="text-xs text-ink-lighter mt-1">per request</div>
          </div>
        </div>

        {/* Breakdowns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* By Service */}
          <div className="bg-white rounded-lg border border-sage-light/30 p-5 shadow-sm">
            <h2 className="font-semibold text-ink-dark mb-4">Usage by Service</h2>
            {summary.by_service.length === 0 ? (
              <p className="text-ink-lighter text-sm">No usage data yet</p>
            ) : (
              <div className="space-y-3">
                {summary.by_service.map((s) => (
                  <div key={s.service} className="flex items-center justify-between">
                    <div>
                      <span className="font-mono text-sm text-ink-dark">{s.service}</span>
                      <span className="text-xs text-ink-lighter ml-2">({s.requests} requests)</span>
                    </div>
                    <div className="text-right">
                      <span className="font-mono text-sm text-ink-dark">{formatNumber(s.tokens)}</span>
                      <span className="text-xs text-ink-lighter ml-2">{formatCost(s.cost)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* By Request Type */}
          <div className="bg-white rounded-lg border border-sage-light/30 p-5 shadow-sm">
            <h2 className="font-semibold text-ink-dark mb-4">Usage by Request Type</h2>
            {summary.by_request_type.length === 0 ? (
              <p className="text-ink-lighter text-sm">No usage data yet</p>
            ) : (
              <div className="space-y-3">
                {summary.by_request_type.map((t) => (
                  <div key={t.request_type} className="flex items-center justify-between">
                    <div>
                      <span className="font-mono text-sm text-ink-dark">{t.request_type}</span>
                      <span className="text-xs text-ink-lighter ml-2">({t.requests} requests)</span>
                    </div>
                    <div className="text-right">
                      <span className="font-mono text-sm text-ink-dark">{formatNumber(t.tokens)}</span>
                      <span className="text-xs text-ink-lighter ml-2">{formatCost(t.cost)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Requests */}
        <div className="bg-white rounded-lg border border-sage-light/30 p-5 shadow-sm">
          <h2 className="font-semibold text-ink-dark mb-4">Recent Requests</h2>
          {summary.recent_requests.length === 0 ? (
            <p className="text-ink-lighter text-sm">No requests yet. Use SAGE features to generate usage data.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-sage-light/30">
                    <th className="text-left py-2 px-3 text-ink-light font-medium">Time</th>
                    <th className="text-left py-2 px-3 text-ink-light font-medium">Service</th>
                    <th className="text-left py-2 px-3 text-ink-light font-medium">Type</th>
                    <th className="text-right py-2 px-3 text-ink-light font-medium">Tokens</th>
                    <th className="text-right py-2 px-3 text-ink-light font-medium">Cost</th>
                    <th className="text-right py-2 px-3 text-ink-light font-medium">Duration</th>
                    <th className="text-center py-2 px-3 text-ink-light font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.recent_requests.map((req) => (
                    <tr key={req.id} className="border-b border-sage-light/10 hover:bg-sage-light/5">
                      <td className="py-2 px-3 font-mono text-xs text-ink-lighter">
                        {new Date(req.created_at).toLocaleString()}
                      </td>
                      <td className="py-2 px-3 font-mono text-ink-dark">{req.service}</td>
                      <td className="py-2 px-3 text-ink-light">{req.request_type}</td>
                      <td className="py-2 px-3 font-mono text-ink-dark text-right">
                        {formatNumber(req.tokens_input + req.tokens_output)}
                      </td>
                      <td className="py-2 px-3 font-mono text-ink-dark text-right">
                        {formatCost(req.cost)}
                      </td>
                      <td className="py-2 px-3 font-mono text-ink-dark text-right">
                        {formatDuration(req.duration_ms)}
                      </td>
                      <td className="py-2 px-3 text-center">
                        {req.success ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-800">
                            OK
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-red-100 text-red-800">
                            Error
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer note */}
        <div className="mt-6 text-center text-sm text-ink-lighter">
          <p>
            Costs are estimated based on Claude Sonnet 4 pricing ($3/M input, $15/M output).
            <br />
            Data is stored in PostgreSQL and persists across sessions.
          </p>
        </div>
      </div>
    </div>
  );
}
