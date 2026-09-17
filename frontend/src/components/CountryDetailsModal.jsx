import React, { useState, useEffect } from 'react';
import { X, Shield, TrendingUp, Calendar, FileText, ExternalLink, Activity, Sparkles, Download, Layers } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, Cell } from 'recharts';
import RiskExplainer from './RiskExplainer';
import { api } from '../api/client';

export default function CountryDetailsModal({
  iso,
  onClose,
  onOpenDossier,
}) {
  const [riskData, setRiskData] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [summaryData, setSummaryData] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [historyRange, setHistoryRange] = useState(30);

  useEffect(() => {
    if (!iso) return;
    let isMounted = true;
    setLoading(true);

    Promise.all([
      api.getCountryRisk(iso),
      api.getCountryHistory(iso, historyRange),
      api.getCountrySummary(iso),
      api.getCountryEvents(iso, 10),
    ])
      .then(([risk, history, summary, evs]) => {
        if (!isMounted) return;
        setRiskData(risk);
        setHistoryData(history);
        setSummaryData(summary);
        setEvents(evs);
      })
      .catch((err) => console.error("Error fetching country details:", err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [iso, historyRange]);

  if (!iso) return null;

  const getTierBadge = (tier) => {
    if (tier === 'Severe') return 'bg-rose-950/80 text-rose-300 border-rose-700/60';
    if (tier === 'Moderate') return 'bg-amber-950/80 text-amber-300 border-amber-700/60';
    return 'bg-emerald-950/80 text-emerald-300 border-emerald-700/60';
  };

  const categoryBarData = riskData
    ? [
        { name: 'Conflict', score: riskData.contributing_factors.conflict_score || 0, fill: '#ef4444' },
        { name: 'Security', score: riskData.contributing_factors.security_score || 0, fill: '#f59e0b' },
        { name: 'Economy', score: riskData.contributing_factors.economy_score || 0, fill: '#3b82f6' },
        { name: 'Diplomacy', score: riskData.contributing_factors.diplomacy_score || 0, fill: '#10b981' },
      ]
    : [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-sm overflow-y-auto">
      <div className="glass-panel w-full max-w-5xl rounded-2xl border border-sentinel-700/80 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-sentinel-700/80 bg-sentinel-950/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400 font-mono font-bold text-base">
              {iso}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-white tracking-wide">
                  {riskData?.country_name || iso}
                </h2>
                {riskData && (
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getTierBadge(riskData.risk_tier)}`}>
                    {riskData.risk_tier} Risk
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Lat: {riskData?.latitude?.toFixed(2)} &bull; Lon: {riskData?.longitude?.toFixed(2)} &bull; Monitored Window: 30 Days
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onOpenDossier(iso)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-md transition-all"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Export Dossier</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-md bg-sentinel-900 hover:bg-sentinel-800 border border-sentinel-700 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="flex items-center justify-center py-20 text-cyan-400 font-mono text-sm animate-pulse">
              Synthesizing Country Telemetry &amp; Evidence...
            </div>
          ) : (
            <>
              {/* Top Row: Executive Summary & Score Gauge */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Score Gauge Card */}
                <div className="glass-panel p-4 rounded-xl border border-sentinel-700/60 flex flex-col items-center justify-center text-center">
                  <span className="text-xs uppercase font-mono tracking-wider text-slate-400 mb-1">
                    Country Risk Index R_c(t)
                  </span>
                  <div className="relative my-2">
                    <div className="text-5xl font-extrabold font-mono text-white tracking-tight">
                      {riskData?.risk_index?.toFixed(1)}
                    </div>
                    <span className="text-xs text-slate-400 font-mono">/ 100</span>
                  </div>
                  <div className="w-full bg-sentinel-900 h-2.5 rounded-full overflow-hidden border border-sentinel-700 mt-2">
                    <div
                      className="h-full transition-all duration-700 rounded-full"
                      style={{
                        width: `${riskData?.risk_index || 0}%`,
                        backgroundColor:
                          riskData?.risk_index > 60
                            ? '#ef4444'
                            : riskData?.risk_index >= 30
                            ? '#f59e0b'
                            : '#10b981',
                      }}
                    />
                  </div>
                  <div className="text-[11px] text-slate-400 mt-2 font-mono">
                    Based on {riskData?.event_count} events &bull; &lambda;=ln(2)/7 decay
                  </div>
                </div>

                {/* BART 3-Bullet Executive Briefing */}
                <div className="md:col-span-2 glass-panel p-4 rounded-xl border border-sentinel-700/60 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-cyan-400" />
                        <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-200">
                          BART Abstractive Executive Briefing (Target ROUGE-L &ge; 0.40)
                        </h3>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sentinel-950 text-cyan-400 border border-cyan-800/40">
                        {summaryData?.model_version || 'bart-geosentinel-v1'}
                      </span>
                    </div>

                    <div className="space-y-2 mt-2">
                      {(summaryData?.bullet_points || []).map((bullet, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-xs text-slate-200 leading-relaxed bg-sentinel-950/50 p-2 rounded-lg border border-sentinel-800/40">
                          <span className="text-cyan-400 font-bold mt-0.5">&bull;</span>
                          <span>{bullet}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {summaryData?.evidence_links && summaryData.evidence_links.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-sentinel-800 flex items-center gap-2 text-[11px] text-slate-400">
                      <span className="font-mono text-cyan-400">Primary Citation:</span>
                      <a
                        href={summaryData.evidence_links[0].url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-slate-300 hover:text-cyan-300 truncate underline flex items-center gap-1"
                      >
                        {summaryData.evidence_links[0].title}
                        <ExternalLink className="w-3 h-3 flex-shrink-0" />
                      </a>
                    </div>
                  )}
                </div>
              </div>

              {/* Explainability Breakdown Component */}
              <RiskExplainer
                explanation={riskData?.explanation}
                countryName={riskData?.country_name}
                riskIndex={riskData?.risk_index || 0}
                riskTier={riskData?.risk_tier || 'Low'}
              />

              {/* Middle Row: Trend Charts & Category Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Historical Risk Trajectory */}
                <div className="glass-panel p-4 rounded-xl border border-sentinel-700/60 flex flex-col h-[280px]">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-cyan-400" />
                      <h4 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-200">
                        Risk Score Trajectory
                      </h4>
                    </div>
                    <div className="flex items-center gap-1 text-[11px] font-mono">
                      {[7, 14, 30].map((d) => (
                        <button
                          key={d}
                          onClick={() => setHistoryRange(d)}
                          className={`px-2 py-0.5 rounded transition-colors ${
                            historyRange === d
                              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                              : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          {d}d
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex-1 w-full mt-2">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={historyData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#162234" />
                        <XAxis
                          dataKey="timestamp"
                          stroke="#64748b"
                          tick={{ fontSize: 10 }}
                          tickFormatter={(val) => new Date(val).toLocaleDateString(undefined, { month: 'numeric', day: 'numeric' })}
                        />
                        <YAxis stroke="#64748b" domain={[0, 100]} tick={{ fontSize: 10 }} />
                        <Tooltip
                          contentStyle={{ background: '#0e1724', borderColor: '#1e3048', fontSize: '11px' }}
                          labelFormatter={(l) => new Date(l).toLocaleString()}
                        />
                        <Line type="monotone" dataKey="risk_score" stroke="#38bdf8" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Domain Composition Bar Chart */}
                <div className="glass-panel p-4 rounded-xl border border-sentinel-700/60 flex flex-col h-[280px]">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Layers className="w-4 h-4 text-cyan-400" />
                      <h4 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-200">
                        Domain Severity Points
                      </h4>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">w_i &times; S_i &times; c_i</span>
                  </div>

                  <div className="flex-1 w-full mt-2">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={categoryBarData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#162234" />
                        <XAxis type="number" stroke="#64748b" tick={{ fontSize: 10 }} />
                        <YAxis dataKey="name" type="category" stroke="#64748b" tick={{ fontSize: 11 }} width={75} />
                        <Tooltip contentStyle={{ background: '#0e1724', borderColor: '#1e3048', fontSize: '11px' }} />
                        <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                          {categoryBarData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Bottom: Evidence Drill-Down / Recent Events */}
              <div className="glass-panel p-4 rounded-xl border border-sentinel-700/60">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-200 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    Auditable Evidence Trail: Primary Events &amp; Articles
                  </h4>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Showing top {events.length} chronological records
                  </span>
                </div>

                <div className="space-y-2">
                  {events.length === 0 ? (
                    <div className="text-xs text-slate-400 py-4 text-center font-mono">
                      No active events recorded for this country.
                    </div>
                  ) : (
                    events.map((ev) => (
                      <div
                        key={ev.event_id}
                        className="p-3 rounded-lg bg-sentinel-950/70 border border-sentinel-800/60 hover:border-sentinel-700 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                                ev.category === 'CONFLICT'
                                  ? 'bg-rose-950/80 text-rose-300 border border-rose-800/50'
                                  : ev.category === 'SECURITY'
                                  ? 'bg-amber-950/80 text-amber-300 border border-amber-800/50'
                                  : ev.category === 'ECONOMY'
                                  ? 'bg-blue-950/80 text-blue-300 border border-blue-800/50'
                                  : 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/50'
                              }`}
                            >
                              {ev.category}
                            </span>
                            <span className="text-xs text-slate-400 font-mono">
                              {new Date(ev.timestamp).toLocaleDateString()}
                            </span>
                            <span className="text-[11px] text-slate-400">
                              via <strong className="text-slate-300">{ev.source_name}</strong>
                            </span>
                          </div>
                          <p className="text-xs font-medium text-slate-200">
                            {ev.article_title}
                          </p>
                          <div className="flex items-center gap-3 text-[10px] text-slate-400 font-mono">
                            <span>Sentiment: <strong className={ev.sentiment < 0 ? 'text-rose-400' : 'text-emerald-400'}>{ev.sentiment.toFixed(2)}</strong></span>
                            <span>Severity: <strong className="text-amber-400">{(ev.severity * 100).toFixed(0)}%</strong></span>
                            <span>Model: <strong className="text-slate-300">{ev.model_version}</strong></span>
                          </div>
                        </div>

                        <a
                          href={ev.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center gap-1 text-xs font-semibold text-cyan-400 hover:text-cyan-300 px-3 py-1.5 rounded bg-sentinel-900 hover:bg-sentinel-800 border border-sentinel-700 transition-colors flex-shrink-0"
                        >
                          <span>Inspect Source</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
