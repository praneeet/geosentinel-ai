import React, { useState, useEffect, useMemo } from 'react';
import {
  X,
  Shield,
  TrendingUp,
  Calendar,
  Download,
  Printer,
  ExternalLink,
  Activity,
  Sparkles,
  Layers,
  Swords,
  ShieldAlert,
  Search,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Info,
  Clock,
  Compass,
  BarChart3,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  Cell,
  ReferenceLine,
} from 'recharts';
import { api } from '../api/client';

export default function CountryDetailsModal({
  iso,
  onClose,
}) {
  const [riskData, setRiskData] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [forecastData, setForecastData] = useState([]);
  const [summaryData, setSummaryData] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [historyRange, setHistoryRange] = useState(30);
  const [trajectoryMode, setTrajectoryMode] = useState('forecast'); // 'forecast' | 'history'
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAuditTelemetry, setShowAuditTelemetry] = useState(false);

  useEffect(() => {
    if (!iso) return;
    let isMounted = true;
    setLoading(true);

    // Use Promise.allSettled so no single endpoint failure crashes the modal
    Promise.allSettled([
      api.getCountryRisk(iso),
      api.getCountryForecast(iso, 7),
      api.getCountryHistory(iso, historyRange),
      api.getCountrySummary(iso),
      api.getCountryEvents(iso, 20),
    ])
      .then(([riskRes, forecastRes, historyRes, summaryRes, evsRes]) => {
        if (!isMounted) return;

        const risk = riskRes.status === 'fulfilled' ? riskRes.value : null;
        const forecast = forecastRes.status === 'fulfilled' ? forecastRes.value : [];
        const history = historyRes.status === 'fulfilled' ? historyRes.value : [];
        const summary = summaryRes.status === 'fulfilled' ? summaryRes.value : null;
        const evs = evsRes.status === 'fulfilled' ? evsRes.value : [];

        setRiskData(risk);
        setForecastData(forecast?.length ? forecast : risk?.forecast || []);
        setHistoryData(history || []);
        setSummaryData(summary);
        setEvents(evs || []);
      })
      .catch((err) => console.error('Error fetching country details:', err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [iso, historyRange]);

  // Robust domain score resolution supporting backend schema variations & sqlite string types
  const getDomainScore = (category) => {
    if (!riskData) return 0;
    const catUpper = category.toUpperCase();
    const catLower = category.toLowerCase();

    // 1. Direct top-level category_breakdown
    if (riskData.category_breakdown) {
      if (typeof riskData.category_breakdown[category] === 'number') return riskData.category_breakdown[category];
      if (typeof riskData.category_breakdown[catUpper] === 'number') return riskData.category_breakdown[catUpper];
    }

    // 2. Explanation category_breakdown
    if (riskData.explanation?.category_breakdown) {
      if (typeof riskData.explanation.category_breakdown[category] === 'number') return riskData.explanation.category_breakdown[category];
      if (typeof riskData.explanation.category_breakdown[catUpper] === 'number') return riskData.explanation.category_breakdown[catUpper];
    }

    // 3. Contributing factors (object or JSON string)
    let factors = riskData.contributing_factors;
    if (typeof factors === 'string') {
      try {
        factors = JSON.parse(factors);
      } catch {
        factors = {};
      }
    }
    if (factors && typeof factors === 'object') {
      const factorKey = `${catLower}_score`;
      if (typeof factors[factorKey] === 'number') return factors[factorKey];
    }

    // 4. Fallback: calculate proportion from active events if score object missing
    if (events && events.length > 0) {
      const matching = events.filter((e) => (e.category || '').toUpperCase() === catUpper);
      if (matching.length > 0) {
        const sumSev = matching.reduce((acc, ev) => acc + (Number(ev.severity) || 0.5), 0);
        return Number(((sumSev * (riskData.risk_index || 10)) / events.length).toFixed(1));
      }
    }

    return 0;
  };

  const conflictScore = getDomainScore('Conflict');
  const securityScore = getDomainScore('Security');
  const economyScore = getDomainScore('Economy');
  const diplomacyScore = getDomainScore('Diplomacy');

  const totalPoints = conflictScore + securityScore + economyScore + diplomacyScore;
  const compositeScore = typeof riskData?.risk_index === 'number' ? riskData.risk_index : totalPoints;

  const domainBreakdown = useMemo(() => [
    {
      name: 'Conflict',
      weight: 'w=1.00',
      score: Number(conflictScore.toFixed(1)),
      fill: '#EF4444',
      bg: 'bg-rose-950/30',
      border: 'border-rose-800/40',
      text: 'text-rose-400',
      icon: Swords,
      sharePct: totalPoints > 0 ? Math.round((conflictScore / totalPoints) * 100) : 0,
      description: 'Kinetic skirmishes, military posture & border tensions',
    },
    {
      name: 'Security',
      weight: 'w=0.80',
      score: Number(securityScore.toFixed(1)),
      fill: '#F59E0B',
      bg: 'bg-amber-950/30',
      border: 'border-amber-800/40',
      text: 'text-amber-400',
      icon: Shield,
      sharePct: totalPoints > 0 ? Math.round((securityScore / totalPoints) * 100) : 0,
      description: 'Law enforcement, counter-terrorism & civil stability',
    },
    {
      name: 'Economy',
      weight: 'w=0.55',
      score: Number(economyScore.toFixed(1)),
      fill: '#38BDF8',
      bg: 'bg-sky-950/30',
      border: 'border-sky-800/40',
      text: 'text-sky-400',
      icon: TrendingUp,
      sharePct: totalPoints > 0 ? Math.round((economyScore / totalPoints) * 100) : 0,
      description: 'Trade embargos, energy supplies & shipping chokepoints',
    },
    {
      name: 'Diplomacy',
      weight: 'w=0.35',
      score: Number(diplomacyScore.toFixed(1)),
      fill: '#818CF8',
      bg: 'bg-indigo-950/30',
      border: 'border-indigo-800/40',
      text: 'text-indigo-400',
      icon: Compass,
      sharePct: totalPoints > 0 ? Math.round((diplomacyScore / totalPoints) * 100) : 0,
      description: 'Bilateral negotiations, international summits & treaties',
    },
  ], [conflictScore, securityScore, economyScore, diplomacyScore, totalPoints]);

  // Identify dominant risk vector
  const dominantDomain = useMemo(() => {
    return domainBreakdown.reduce((max, cur) => (cur.score > max.score ? cur : max), domainBreakdown[0]);
  }, [domainBreakdown]);

  const getTierBadge = (tier) => {
    switch (tier?.toUpperCase()) {
      case 'CRITICAL':
      case 'SEVERE':
        return 'bg-rose-950/80 text-rose-300 border-rose-700/80 shadow-rose-950/50';
      case 'MODERATE':
        return 'bg-amber-950/80 text-amber-300 border-amber-700/80 shadow-amber-950/50';
      default:
        return 'bg-emerald-950/70 text-emerald-300 border-emerald-700/60 shadow-emerald-950/50';
    }
  };

  // Filtered events
  const filteredEvents = useMemo(() => {
    return events.filter((ev) => {
      const evCat = (ev.category || '').toUpperCase();
      const matchesCategory = selectedCategory === 'ALL' || evCat === selectedCategory;
      const q = searchQuery.toLowerCase().trim();
      const matchesSearch =
        !q ||
        (ev.article_title || ev.summary || '').toLowerCase().includes(q) ||
        (ev.source_name || '').toLowerCase().includes(q);
      return matchesCategory && matchesSearch;
    });
  }, [events, selectedCategory, searchQuery]);

  const categoryCounts = useMemo(() => {
    const counts = { ALL: events.length, CONFLICT: 0, SECURITY: 0, ECONOMY: 0, DIPLOMACY: 0 };
    events.forEach((ev) => {
      const cat = (ev.category || '').toUpperCase();
      if (counts[cat] !== undefined) counts[cat] += 1;
    });
    return counts;
  }, [events]);

  const maxDomainScore = Math.max(...domainBreakdown.map((d) => d.score), 1);

  const handleExportJSON = () => {
    const payload = {
      country_iso: iso,
      country_name: riskData?.country_name || iso,
      exported_at: new Date().toISOString(),
      risk_index: compositeScore,
      risk_tier: riskData?.risk_tier || 'Low',
      event_count: riskData?.event_count || events.length,
      category_breakdown: {
        Conflict: conflictScore,
        Security: securityScore,
        Economy: economyScore,
        Diplomacy: diplomacyScore,
      },
      executive_briefing: summaryData?.bullet_points || [],
      evidence_links: summaryData?.evidence_links || [],
      forecast: forecastData,
      recent_events: events,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `GeoSentinel_${iso}_Report_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/85 backdrop-blur-md overflow-y-auto font-sans animate-fadeIn">
      <div className="bg-[#0B121E] w-full max-w-5xl rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800/90 bg-[#070D17]">
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-sky-500/20 to-blue-600/10 border border-sky-500/30 flex items-center justify-center text-sky-300 font-mono font-extrabold text-base shadow-inner">
              {iso}
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h2 className="text-lg font-bold text-slate-100 tracking-tight">
                  {riskData?.country_name || iso}
                </h2>
                <span
                  className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-bold border shadow-sm ${getTierBadge(
                    riskData?.risk_tier || 'Low'
                  )}`}
                >
                  {riskData?.risk_tier || 'LOW'} RISK
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Lat: {riskData?.latitude ? riskData.latitude.toFixed(2) : '--'} &bull; Lon:{' '}
                {riskData?.longitude ? riskData.longitude.toFixed(2) : '--'} &bull; 30-Day Multi-Source Monitoring Window
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 transition-colors font-mono disabled:opacity-40"
              title="Print / Save as PDF"
            >
              <Printer className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Print</span>
            </button>
            <button
              onClick={handleExportJSON}
              disabled={loading}
              className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-sky-600 hover:bg-sky-500 text-white shadow-md hover:shadow-sky-600/30 transition-all font-mono disabled:opacity-40"
              title="Export country risk data and evidence as JSON"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export JSON</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 transition-colors"
              title="Close modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-5">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-28 text-sky-400 font-mono text-xs gap-3">
              <div className="w-8 h-8 border-2 border-sky-400/30 border-t-sky-400 rounded-full animate-spin" />
              <span className="tracking-wide">Synthesizing Country Telemetry &amp; Evidence...</span>
            </div>
          ) : (
            <>
              {/* TOP ROW: Strategic KPI Matrix & Executive Briefing */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Composite Threat Score Card */}
                <div className="bg-[#10192A] p-5 rounded-xl border border-slate-800/90 flex flex-col justify-between shadow-sm">
                  <div>
                    <div className="flex items-center justify-between text-[11px] uppercase font-mono tracking-wider text-slate-400 mb-1">
                      <span>Composite Threat Index</span>
                      <span className="text-[10px] text-slate-400">Scale: 0 - 100</span>
                    </div>

                    <div className="flex items-baseline gap-2 my-2 font-mono">
                      <span className="text-5xl font-extrabold text-slate-100 tracking-tight">
                        {compositeScore.toFixed(1)}
                      </span>
                      <span className="text-xs text-slate-400 font-sans">/ 100</span>
                    </div>

                    {/* Threat Progress Meter */}
                    <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800 mt-2">
                      <div
                        className="h-full transition-all duration-700 rounded-full"
                        style={{
                          width: `${Math.min(100, Math.max(4, compositeScore))}%`,
                          backgroundColor:
                            compositeScore > 60
                              ? '#EF4444'
                              : compositeScore >= 30
                              ? '#F59E0B'
                              : '#10B981',
                        }}
                      />
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono">
                    <div className="flex items-center gap-1.5 text-slate-300">
                      <Activity className="w-3.5 h-3.5 text-sky-400" />
                      <span>{riskData?.event_count || events.length} Active Events</span>
                    </div>
                    <span className="text-slate-400">7-Day Half-Life Decay</span>
                  </div>
                </div>

                {/* Executive Strategic Intelligence Briefing */}
                <div className="lg:col-span-2 bg-[#10192A] p-5 rounded-xl border border-slate-800/90 flex flex-col justify-between shadow-sm">
                  <div>
                    <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-sky-400" />
                        <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-200">
                          Executive Strategic Intelligence Briefing
                        </h3>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#070D17] text-sky-400 border border-slate-800">
                        Synthesized Telemetry
                      </span>
                    </div>

                    <div className="space-y-2 mt-1">
                      {(summaryData?.bullet_points && summaryData.bullet_points.length > 0
                        ? summaryData.bullet_points
                        : [
                            `Key Development: Verified multi-source surveillance active across ${
                              riskData?.country_name || iso
                            } sovereign territory.`,
                            dominantDomain.score > 0
                              ? `Strategic Significance: Primary threat vector concentrated in ${dominantDomain.name} domain with ${dominantDomain.score} severity points (${dominantDomain.sharePct}% share).`
                              : 'Strategic Significance: Regional indicator trends demonstrate nominal baseline stability.',
                            'Operational Implication: Continued real-time telemetry ingestion and asset defense monitoring recommended.',
                          ]
                      ).map((bullet, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2.5 text-xs text-slate-200 leading-relaxed bg-[#070D17]/70 p-2.5 rounded-lg border border-slate-800/70 font-sans"
                        >
                          <span className="text-sky-400 font-bold mt-0.5">&bull;</span>
                          <span>{bullet}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {summaryData?.evidence_links && summaryData.evidence_links.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-slate-800 flex items-center justify-between gap-2 text-[11px] text-slate-400 font-mono">
                      <div className="flex items-center gap-1.5 truncate">
                        <span className="text-sky-400 font-semibold">Primary Citation:</span>
                        <a
                          href={summaryData.evidence_links[0].url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-slate-300 hover:text-sky-300 truncate underline flex items-center gap-1 font-sans"
                        >
                          {summaryData.evidence_links[0].title}
                          <ExternalLink className="w-3 h-3 shrink-0" />
                        </a>
                      </div>
                      <span className="text-[10px] text-slate-400 shrink-0">
                        {summaryData.evidence_links[0].source || 'Verified OSINT'}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* CORE FIX: DOMAIN SEVERITY POINTS & THREAT VECTORS CENTER */}
              <div className="bg-[#10192A] p-5 rounded-xl border border-slate-800/90 shadow-sm space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-sky-400" />
                    <div>
                      <h3 className="text-xs font-bold uppercase font-mono tracking-wider text-slate-200">
                        Domain Severity Points &amp; Threat Vectors
                      </h3>
                      <p className="text-[11px] text-slate-400">
                        Weighted category points synthesized from active geopolitical events
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-[#070D17] text-slate-300 border border-slate-800">
                      Dominant Vector: <strong className="text-sky-300 font-bold">{dominantDomain.name}</strong> ({dominantDomain.score} pts)
                    </span>
                    <button
                      onClick={() => setShowAuditTelemetry(!showAuditTelemetry)}
                      className="flex items-center gap-1 text-[11px] font-mono text-slate-400 hover:text-sky-300 transition-colors ml-1 px-2 py-1 rounded bg-[#070D17] border border-slate-800"
                    >
                      <span>{showAuditTelemetry ? 'Hide Calibration' : 'Calibration Info'}</span>
                      {showAuditTelemetry ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* 4 Interactive Domain Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {domainBreakdown.map((d) => {
                    const Icon = d.icon;
                    return (
                      <div
                        key={d.name}
                        className={`${d.bg} border ${d.border} p-3.5 rounded-xl flex flex-col justify-between hover:border-slate-700 transition-all`}
                      >
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className={`p-1.5 rounded-lg bg-black/40 ${d.text}`}>
                                <Icon className="w-4 h-4" />
                              </span>
                              <span className="text-xs font-bold font-mono text-slate-100 uppercase">{d.name}</span>
                            </div>
                            <span className="text-[10px] font-mono text-slate-400 bg-[#070D17] px-1.5 py-0.5 rounded border border-slate-800">
                              {d.weight}
                            </span>
                          </div>

                          <div className="my-2">
                            <div className={`text-2xl font-extrabold font-mono ${d.text} tracking-tight`}>
                              +{d.score.toFixed(1)} <span className="text-xs font-normal text-slate-400">pts</span>
                            </div>
                            <div className="text-[11px] text-slate-300 font-mono mt-0.5">
                              {d.sharePct}% of total threat
                            </div>
                          </div>
                        </div>

                        <div>
                          {/* Mini Progress Bar */}
                          <div className="w-full bg-slate-900/90 h-2 rounded-full overflow-hidden mt-1 border border-slate-800/80">
                            <div
                              className="h-full rounded-full transition-all duration-700"
                              style={{ width: `${Math.min(100, Math.max(d.score > 0 ? 6 : 0, (d.score / maxDomainScore) * 100))}%`, backgroundColor: d.fill }}
                            />
                          </div>
                          <p className="text-[10px] text-slate-400 mt-2 line-clamp-1">{d.description}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Optional Calibration Info Drawer */}
                {showAuditTelemetry && (
                  <div className="bg-[#070D17] p-3.5 rounded-lg border border-slate-800 font-mono text-[11px] text-slate-300 space-y-2 animate-fadeIn">
                    <div className="flex items-center gap-1.5 text-sky-400 font-bold text-xs">
                      <Info className="w-3.5 h-3.5" />
                      <span>Mathematical Scoring Formulation &amp; Telemetry Calibration</span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[10px] text-slate-400 pt-1 border-t border-slate-800/80">
                      <div>Weight Scalar (&alpha;): <span className="text-slate-100 font-bold">4.25</span></div>
                      <div>Half-Life Decay (&lambda;): <span className="text-slate-100 font-bold">ln(2)/7 &approx; 0.0990</span></div>
                      <div>Freshness Retention: <span className="text-slate-100 font-bold">{riskData?.explanation?.temporal_retention_pct || 92}%</span></div>
                      <div>Avg Polarity Magnitude: <span className="text-slate-100 font-bold">{(riskData?.explanation?.sentiment_magnitude || 0.55).toFixed(2)}</span></div>
                    </div>
                  </div>
                )}
              </div>

              {/* MIDDLE ROW: Trajectory Forecast Chart & Domain Severity Points Visualizer */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* 7-Day Forecasting vs Historical Trend Line Chart */}
                <div className="bg-[#10192A] p-5 rounded-xl border border-slate-800/90 flex flex-col h-[300px] shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-1.5 bg-[#070D17] p-1 rounded-lg border border-slate-800">
                      <button
                        onClick={() => setTrajectoryMode('forecast')}
                        className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-mono font-bold transition-all ${
                          trajectoryMode === 'forecast'
                            ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30 shadow-sm'
                            : 'text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        <TrendingUp className="w-3.5 h-3.5 text-purple-400" />
                        <span>7d Forward Forecast</span>
                      </button>
                      <button
                        onClick={() => setTrajectoryMode('history')}
                        className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-mono font-bold transition-all ${
                          trajectoryMode === 'history'
                            ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30 shadow-sm'
                            : 'text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        <Calendar className="w-3.5 h-3.5 text-sky-400" />
                        <span>Historical ({historyRange}d)</span>
                      </button>
                    </div>

                    {trajectoryMode === 'history' ? (
                      <div className="flex items-center gap-1 text-[11px] font-mono">
                        {[7, 14, 30].map((d) => (
                          <button
                            key={d}
                            onClick={() => setHistoryRange(d)}
                            className={`px-2 py-0.5 rounded transition-colors ${
                              historyRange === d
                                ? 'bg-sky-500/20 text-sky-300 font-bold border border-sky-500/30'
                                : 'text-slate-400 hover:text-slate-200'
                            }`}
                          >
                            {d}d
                          </button>
                        ))}
                      </div>
                    ) : (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#070D17] text-purple-300 border border-purple-900/40">
                        {forecastData[0]?.model_used === 'naive_persistence'
                          ? 'Persistence Baseline'
                          : 'Holt-Winters (95% CI)'}
                      </span>
                    )}
                  </div>

                  <div className="flex-1 w-full mt-2">
                    {trajectoryMode === 'forecast' ? (
                      forecastData.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400 font-mono text-xs">
                          <TrendingUp className="w-7 h-7 text-slate-600 mb-2" />
                          <span>No projection available for {iso}.</span>
                          <span className="text-[10px] text-slate-400 mt-1">
                            Awaiting minimum telemetry observations for statistical extrapolation.
                          </span>
                        </div>
                      ) : (
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={forecastData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.08)" vertical={false} />
                            <XAxis
                              dataKey="timestamp"
                              stroke="#476999"
                              fontSize={10}
                              tickLine={false}
                              tickFormatter={(val) => {
                                const d = new Date(val);
                                return `${d.getMonth() + 1}/${d.getDate()}`;
                              }}
                            />
                            <YAxis stroke="#476999" domain={[0, 100]} fontSize={10} tickLine={false} />
                            <Tooltip
                              contentStyle={{
                                background: '#070D17',
                                borderColor: 'rgba(148, 163, 184, 0.2)',
                                fontSize: '11px',
                                color: '#F1F5F9',
                                borderRadius: '8px',
                              }}
                              labelFormatter={(l) => `Forecast: ${new Date(l).toLocaleDateString()}`}
                              formatter={(val, name) => {
                                const num = Number(val).toFixed(1);
                                if (name === 'Upper 95% CI') return [`${num} / 100`, 'Upper Bound (95% CI)'];
                                if (name === 'Lower 95% CI') return [`${num} / 100`, 'Lower Bound (95% CI)'];
                                return [`${num} / 100`, 'Projected Risk'];
                              }}
                            />
                            <ReferenceLine
                              y={75}
                              stroke="#EF4444"
                              strokeDasharray="3 3"
                              label={{
                                value: 'Alert Threshold (75)',
                                fill: '#EF4444',
                                fontSize: 10,
                                position: 'insideTopLeft',
                              }}
                            />
                            <Line
                              type="monotone"
                              dataKey="confidence_upper"
                              stroke="#A855F7"
                              strokeWidth={1}
                              strokeDasharray="3 3"
                              dot={false}
                              name="Upper 95% CI"
                            />
                            <Line
                              type="monotone"
                              dataKey="forecast_risk"
                              stroke="#C084FC"
                              strokeWidth={2.5}
                              dot={{ fill: '#C084FC', r: 3 }}
                              name="Projected Risk"
                            />
                            <Line
                              type="monotone"
                              dataKey="confidence_lower"
                              stroke="#A855F7"
                              strokeWidth={1}
                              strokeDasharray="3 3"
                              dot={false}
                              name="Lower 95% CI"
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      )
                    ) : (
                      historyData.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400 font-mono text-xs">
                          <Clock className="w-7 h-7 text-slate-600 mb-2" />
                          <span>No historical baseline recorded in {historyRange}d window.</span>
                          <span className="text-[10px] text-slate-400 mt-1">
                            Observed time-series points are logged after verified ingestion cycles.
                          </span>
                        </div>
                      ) : (
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={historyData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.08)" vertical={false} />
                            <XAxis
                              dataKey="timestamp"
                              stroke="#476999"
                              fontSize={10}
                              tickLine={false}
                              tickFormatter={(val) =>
                                new Date(val).toLocaleDateString(undefined, { month: 'numeric', day: 'numeric' })
                              }
                            />
                            <YAxis stroke="#476999" domain={[0, 100]} fontSize={10} tickLine={false} />
                            <Tooltip
                              contentStyle={{
                                background: '#070D17',
                                borderColor: 'rgba(148, 163, 184, 0.2)',
                                fontSize: '11px',
                                color: '#F1F5F9',
                                borderRadius: '8px',
                              }}
                              labelFormatter={(l) => new Date(l).toLocaleString()}
                              formatter={(val) => [`${Number(val).toFixed(1)} / 100`, 'Historical Risk']}
                            />
                            <ReferenceLine
                              y={75}
                              stroke="#EF4444"
                              strokeDasharray="3 3"
                              label={{
                                value: 'Alert Threshold (75)',
                                fill: '#EF4444',
                                fontSize: 10,
                                position: 'insideTopLeft',
                              }}
                            />
                            <Line
                              type="monotone"
                              dataKey="risk_score"
                              stroke="#38BDF8"
                              strokeWidth={2.5}
                              dot={false}
                              name="Historical Risk"
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      )
                    )}
                  </div>
                </div>

                {/* Domain Severity Points Bar Chart */}
                <div className="bg-[#10192A] p-5 rounded-xl border border-slate-800/90 flex flex-col h-[300px] shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-sky-400" />
                      <h4 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-200">
                        Domain Severity Points Comparison
                      </h4>
                    </div>
                    <span className="text-[11px] font-mono text-slate-400">
                      Total: <strong className="text-slate-200">+{totalPoints.toFixed(1)} pts</strong>
                    </span>
                  </div>

                  <div className="flex-1 w-full mt-2">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={domainBreakdown} layout="vertical" margin={{ left: 10, right: 30, top: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.08)" horizontal={false} />
                        <XAxis type="number" stroke="#476999" fontSize={10} tickLine={false} domain={[0, Math.max(10, Math.ceil(maxDomainScore * 1.25))]} />
                        <YAxis dataKey="name" type="category" stroke="#94A3B8" fontSize={11} tickLine={false} width={80} />
                        <Tooltip
                          content={({ active, payload }) => {
                            if (!active || !payload || !payload.length) return null;
                            const item = payload[0].payload;
                            return (
                              <div className="bg-[#070D17] border border-slate-700 p-2.5 rounded-lg shadow-xl font-mono text-xs">
                                <div className="font-bold text-slate-100 flex items-center gap-1.5 mb-1">
                                  <span className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: item.fill }}></span>
                                  <span>{item.name} Domain</span>
                                  <span className="text-[10px] text-slate-400 font-normal">({item.weight})</span>
                                </div>
                                <div className="text-slate-200">
                                  Severity Points: <strong style={{ color: item.fill }}>+{item.score.toFixed(1)} pts</strong>
                                </div>
                                <div className="text-[10px] text-slate-400 mt-0.5">
                                  Impact Contribution: <strong>{item.sharePct}%</strong> of total risk
                                </div>
                              </div>
                            );
                          }}
                        />
                        <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                          {domainBreakdown.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* BOTTOM: Verified Evidence Feed & Search Wire */}
              <div className="bg-[#10192A] p-5 rounded-xl border border-slate-800/90 shadow-sm space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-sky-400" />
                    <div>
                      <h4 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-200">
                        Verified Evidence Trail: Events &amp; Articles
                      </h4>
                      <p className="text-[11px] text-slate-400">
                        Showing {filteredEvents.length} of {events.length} multi-source intelligence records
                      </p>
                    </div>
                  </div>

                  {/* Search Input */}
                  <div className="relative w-full sm:w-64">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Filter articles &amp; sources..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-[#070D17] border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors font-sans"
                    />
                  </div>
                </div>

                {/* Category Filter Pills */}
                <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs font-mono">
                  {['ALL', 'CONFLICT', 'SECURITY', 'ECONOMY', 'DIPLOMACY'].map((cat) => {
                    const count = categoryCounts[cat] || 0;
                    const isActive = selectedCategory === cat;
                    return (
                      <button
                        key={cat}
                        onClick={() => setSelectedCategory(cat)}
                        className={`px-3 py-1 rounded-lg border transition-all flex items-center gap-1.5 whitespace-nowrap ${
                          isActive
                            ? 'bg-sky-600/20 text-sky-300 border-sky-500/50 font-bold shadow-sm'
                            : 'bg-[#070D17] text-slate-400 border-slate-800 hover:text-slate-200 hover:border-slate-700'
                        }`}
                      >
                        <span>{cat}</span>
                        <span className={`px-1.5 py-0.2 rounded text-[10px] ${isActive ? 'bg-sky-500/30 text-sky-200' : 'bg-slate-800 text-slate-400'}`}>
                          {count}
                        </span>
                      </button>
                    );
                  })}
                </div>

                {/* Events Feed List */}
                <div className="space-y-2.5 max-h-[360px] overflow-y-auto pr-1">
                  {filteredEvents.length === 0 ? (
                    <div className="text-xs text-slate-400 py-10 text-center font-mono bg-[#070D17] rounded-xl border border-slate-800/80">
                      {searchQuery
                        ? 'No records match your filter criteria.'
                        : 'No active events recorded for this sovereign theater.'}
                    </div>
                  ) : (
                    filteredEvents.map((ev) => {
                      const sev = Number(ev.severity || 0);
                      const catUpper = (ev.category || 'SECURITY').toUpperCase();
                      const domainMeta = domainBreakdown.find((d) => d.name.toUpperCase() === catUpper) || domainBreakdown[1];

                      return (
                        <div
                          key={ev.event_id}
                          className="p-3.5 rounded-xl bg-[#070D17] border border-slate-800/90 hover:border-slate-700 hover:bg-[#070D17]/90 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shadow-sm"
                        >
                          <div className="space-y-1.5 flex-1 min-w-0">
                            <div className="flex flex-wrap items-center gap-2 font-mono text-[10px]">
                              <span className={`px-2 py-0.5 rounded font-bold border ${domainMeta.bg} ${domainMeta.text} ${domainMeta.border}`}>
                                {catUpper}
                              </span>
                              <span
                                className={`px-1.5 py-0.5 rounded font-bold ${
                                  sev >= 0.7
                                    ? 'bg-rose-950 text-rose-300 border border-rose-800/60'
                                    : sev >= 0.4
                                    ? 'bg-amber-950 text-amber-300 border border-amber-800/60'
                                    : 'bg-emerald-950 text-emerald-300 border border-emerald-800/60'
                                }`}
                              >
                                Sev: {sev.toFixed(2)}
                              </span>
                              <span className="text-slate-400">
                                {new Date(ev.timestamp).toLocaleDateString(undefined, {
                                  year: 'numeric',
                                  month: 'short',
                                  day: 'numeric',
                                })}
                              </span>
                              <span className="text-slate-600">&bull;</span>
                              <span className="text-slate-300 font-semibold">{ev.source_name || 'OSINT News Wire'}</span>
                            </div>

                            <div className="font-semibold text-slate-100 font-sans text-sm leading-snug">
                              {ev.article_title || ev.summary}
                            </div>
                          </div>

                          {ev.source_url && (
                            <a
                              href={ev.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-950/60 hover:bg-sky-900/80 text-sky-400 hover:text-sky-300 text-xs font-mono font-medium border border-sky-800/40 shrink-0 transition-colors"
                            >
                              <span>Verify Citation</span>
                              <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                          )}
                        </div>
                      );
                    })
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
