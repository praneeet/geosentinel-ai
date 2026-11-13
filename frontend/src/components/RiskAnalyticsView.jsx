import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';
import {
  TrendingUp,
  BarChart2,
  Calendar,
  Globe,
  Eye,
  Filter,
  ShieldAlert,
  ArrowUpRight,
  ArrowDownRight,
  Layers,
} from 'lucide-react';
import { api } from '../api/client';

export default function RiskAnalyticsView({ countries = [], onSelectCountry }) {
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedDays, setSelectedDays] = useState(30);
  const [searchTable, setSearchTable] = useState('');
  const [filterTier, setFilterTier] = useState('ALL');

  useEffect(() => {
    setLoading(true);
    api.getTrends(selectedDays)
      .then((data) => setTrendData(data))
      .catch((err) => console.error('Error fetching trends:', err))
      .finally(() => setLoading(false));
  }, [selectedDays]);

  const timeline = trendData?.timeline || [];
  const catDist = trendData?.category_distribution || {};

  const categoryBarData = Object.entries(catDist).map(([key, value]) => ({
    category: key,
    count: value,
  }));

  const categoryColors = {
    CONFLICT: '#EF4444',
    SECURITY: '#F59E0B',
    ECONOMY: '#38BDF8',
    DIPLOMACY: '#818CF8',
  };

  // Filtered and sorted countries
  const filteredCountries = countries
    .filter((c) => {
      const matchTier = filterTier === 'ALL' || c.risk_tier?.toUpperCase() === filterTier;
      const matchSearch =
        !searchTable ||
        c.country_name?.toLowerCase().includes(searchTable.toLowerCase()) ||
        c.country_iso?.toLowerCase().includes(searchTable.toLowerCase());
      return matchTier && matchSearch;
    })
    .sort((a, b) => b.risk_index - a.risk_index);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[#111C2D] p-5 rounded-xl border border-slate-800/80 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-5 h-5 text-sky-400" />
            <h2 className="text-base font-bold font-mono text-slate-100 uppercase tracking-wider">
              Longitudinal Risk Analytics &amp; Forecasting
            </h2>
          </div>
          <p className="text-xs text-slate-400 font-sans">
            7-Day Exponential Half-Life Modeling, Threat Velocity Distributions, and Sovereign Ranking Matrix
          </p>
        </div>

        {/* Time Window Selector */}
        <div className="flex items-center gap-1.5 bg-[#0D1422] p-1 rounded-lg border border-slate-800">
          <Calendar className="w-3.5 h-3.5 text-slate-400 ml-1.5" />
          {[14, 30, 60, 90].map((d) => (
            <button
              key={d}
              onClick={() => setSelectedDays(d)}
              className={`px-2.5 py-1 rounded text-xs font-mono font-medium transition-colors ${
                selectedDays === d
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {d}D
            </button>
          ))}
        </div>
      </div>

      {/* Two-Column Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Longitudinal Incident & Threat Velocity Area Chart */}
        <div className="lg:col-span-2 bg-[#111C2D] p-5 rounded-xl border border-slate-800/80 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="font-mono font-semibold text-xs text-slate-200 uppercase tracking-wider">
                Geopolitical Event Velocity (Last {selectedDays} Days)
              </div>
              <div className="text-[11px] text-slate-400">
                Daily frequency of verified conflict, security, and diplomatic events
              </div>
            </div>
            <div className="text-xs font-mono px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
              Avg Sentiment: {trendData?.overall_average_sentiment ? Number(trendData.overall_average_sentiment).toFixed(2) : '-0.24'}
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#38BDF8" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.08)" vertical={false} />
                <XAxis
                  dataKey="date"
                  stroke="#476999"
                  fontSize={10}
                  tickLine={false}
                  tickFormatter={(val) => (val ? val.slice(5) : '')}
                />
                <YAxis stroke="#476999" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0D1422',
                    borderColor: 'rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    fontSize: '11px',
                    color: '#F1F5F9',
                  }}
                  itemStyle={{ color: '#38BDF8' }}
                  labelStyle={{ color: '#94A3B8', fontFamily: 'monospace' }}
                />
                <Area
                  type="monotone"
                  dataKey="event_count"
                  name="Event Count"
                  stroke="#38BDF8"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#areaGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Categorical Event Classification Breakdown */}
        <div className="bg-[#111C2D] p-5 rounded-xl border border-slate-800/80 shadow-sm flex flex-col">
          <div className="mb-4">
            <div className="font-mono font-semibold text-xs text-slate-200 uppercase tracking-wider">
              Classification Breakdown
            </div>
            <div className="text-[11px] text-slate-400">
              Taxonomy distribution across event classifications
            </div>
          </div>

          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryBarData} layout="vertical" margin={{ top: 0, right: 15, left: 20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.08)" horizontal={false} />
                <XAxis type="number" stroke="#476999" fontSize={10} tickLine={false} />
                <YAxis dataKey="category" type="category" stroke="#94A3B8" fontSize={10} tickLine={false} width={75} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0D1422',
                    borderColor: 'rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    fontSize: '11px',
                    color: '#F1F5F9',
                  }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {categoryBarData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={categoryColors[entry.category] || '#38BDF8'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 grid grid-cols-2 gap-2 text-[11px] font-mono">
            {Object.entries(catDist).map(([k, v]) => (
              <div key={k} className="flex items-center justify-between p-1.5 rounded bg-[#0D1422]">
                <div className="flex items-center gap-1.5">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: categoryColors[k] || '#94A3B8' }}
                  />
                  <span className="text-slate-300">{k}</span>
                </div>
                <span className="font-bold text-white">{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sovereign Threat Ranking Table */}
      <div className="bg-[#111C2D] rounded-xl border border-slate-800/80 shadow-sm overflow-hidden">
        {/* Table Filter Toolbar */}
        <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-sky-400" />
            <h3 className="text-xs font-mono font-bold text-slate-100 uppercase tracking-wider">
              Sovereign Risk Ranking Matrix ({filteredCountries.length} Countries)
            </h3>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {/* Search Input */}
            <input
              type="text"
              value={searchTable}
              onChange={(e) => setSearchTable(e.target.value)}
              placeholder="Filter country or ISO..."
              className="px-3 py-1 bg-[#0D1422] border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-500/40 font-mono w-48"
            />

            {/* Risk Tier Toggle */}
            <div className="flex items-center bg-[#0D1422] p-0.5 rounded-lg border border-slate-800 text-[11px] font-mono">
              {['ALL', 'SEVERE', 'MODERATE', 'LOW'].map((t) => (
                <button
                  key={t}
                  onClick={() => setFilterTier(t)}
                  className={`px-2 py-0.5 rounded transition-colors ${
                    filterTier === t
                      ? 'bg-sky-500/20 text-sky-300 font-bold'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Table Body */}
        <div className="overflow-x-auto">
          <table className="w-full text-left intel-table">
            <thead>
              <tr>
                <th className="w-12 text-center">#</th>
                <th>Sovereign Nation</th>
                <th>ISO Code</th>
                <th>Composite Risk (0-100)</th>
                <th>Threat Tier</th>
                <th>Active Events</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredCountries.map((c, idx) => {
                const risk = c.risk_index || 0;
                const isSevere = risk > 60;
                const isModerate = risk >= 30 && risk <= 60;
                const tierColor = isSevere
                  ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                  : isModerate
                  ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                  : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30';

                return (
                  <tr key={c.country_iso} className="transition-colors">
                    <td className="text-center font-mono text-slate-400 text-[11px]">{idx + 1}</td>
                    <td className="font-semibold text-slate-100 flex items-center gap-2">
                      <span className="text-sm">{c.country_name || c.country_iso}</span>
                    </td>
                    <td className="font-mono text-sky-400 text-xs">{c.country_iso}</td>
                    <td>
                      <div className="flex items-center gap-2.5">
                        <div className="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              isSevere ? 'bg-rose-500' : isModerate ? 'bg-amber-500' : 'bg-emerald-500'
                            }`}
                            style={{ width: `${Math.min(100, risk)}%` }}
                          />
                        </div>
                        <span className="font-mono font-bold text-xs text-slate-100">
                          {risk.toFixed(1)}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${tierColor}`}>
                        {c.risk_tier}
                      </span>
                    </td>
                    <td className="font-mono text-xs text-slate-300">{c.event_count || 0}</td>
                    <td>
                      <button
                        onClick={() => onSelectCountry(c.country_iso)}
                        className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-850 hover:bg-slate-800 text-sky-400 border border-slate-750 hover:border-sky-500/40 text-[11px] font-mono transition-colors"
                      >
                        <Eye className="w-3 h-3" />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

