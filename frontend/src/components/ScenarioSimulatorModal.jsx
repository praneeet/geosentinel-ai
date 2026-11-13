import React, { useState, useEffect } from 'react';
import {
  X,
  Play,
  RotateCcw,
  AlertTriangle,
  ShieldAlert,
  TrendingUp,
  Compass,
  Cpu,
  Zap,
  Activity,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { api } from '../api/client';

export default function ScenarioSimulatorModal({
  isOpen,
  onClose,
  countries = [],
  isInline = false,
}) {
  if (!isOpen && !isInline) return null;

  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [selectedIso, setSelectedIso] = useState('YEM');
  const [scenarioTitle, setScenarioTitle] = useState('Red Sea Missile Strike Interdiction');
  const [category, setCategory] = useState('CONFLICT');
  const [incidentCount, setIncidentCount] = useState(4);
  const [sentiment, setSentiment] = useState(-0.9);
  const [credibility, setCredibility] = useState(0.95);
  const [spilloverInput, setSpilloverInput] = useState('SAU, EGY, ISR');
  const [isSimulating, setIsSimulating] = useState(false);
  const [simResult, setSimResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getSimulationTemplates()
      .then((data) => {
        setTemplates(data || []);
        if (data && data.length > 0) {
          applyTemplate(data[0]);
        }
      })
      .catch((err) => console.error('Error loading simulation templates:', err));
  }, []);

  const applyTemplate = (tpl) => {
    setSelectedTemplate(tpl.id);
    setSelectedIso(tpl.country_iso);
    setScenarioTitle(tpl.title);
    setCategory(tpl.category);
    setIncidentCount(tpl.injected_incidents_count);
    setSentiment(tpl.sentiment);
    setCredibility(tpl.credibility);
    setSpilloverInput((tpl.spillover_countries || []).join(', '));
  };

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    setError(null);
    try {
      const spillovers = spilloverInput.split(',').map((s) => s.trim().toUpperCase()).filter(Boolean);
      const res = await api.runSimulation({
        country_iso: selectedIso,
        scenario_title: scenarioTitle,
        category: category,
        sentiment: parseFloat(sentiment),
        credibility: parseFloat(credibility),
        injected_incidents_count: parseInt(incidentCount, 10),
        spillover_countries: spillovers,
      });
      setSimResult(res);
    } catch (err) {
      setError(err.message || 'Simulation execution failed');
    } finally {
      setIsSimulating(false);
    }
  };

  const chartData =
    simResult?.projected_trajectory?.map((pt, idx) => ({
      day: `Day +${idx + 1}`,
      projected: pt.forecast_risk,
      upper: pt.upper_bound,
      lower: pt.lower_bound,
    })) || [];

  const contentBlock = (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#111C2D] p-5 rounded-xl border border-slate-800/80 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold font-mono text-slate-100 uppercase tracking-wider">
                What-If Scenario Simulation Sandbox
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-950 text-purple-300 border border-purple-700/50">
                STRESS TEST
              </span>
            </div>
            <p className="text-xs text-slate-400 font-sans">
              Inject synthetic kinetic, cyber, or economic shocks and model risk propagation across sovereign theaters.
            </p>
          </div>
        </div>

        {!isInline && onClose && (
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-850 border border-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Preset Scenarios */}
      <div className="space-y-2">
        <div className="text-xs font-mono font-semibold uppercase text-slate-400">
          Preset Tactical Scenarios:
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
          {templates.map((tpl) => (
            <button
              key={tpl.id}
              onClick={() => applyTemplate(tpl)}
              className={`p-3 rounded-xl border text-left transition-all text-xs flex flex-col justify-between ${
                selectedTemplate === tpl.id
                  ? 'bg-purple-500/20 border-purple-500/50 text-purple-200 shadow-sm'
                  : 'bg-[#111C2D] border-slate-800 text-slate-300 hover:border-slate-700'
              }`}
            >
              <div className="font-bold mb-1 truncate">{tpl.title}</div>
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>{tpl.country_iso}</span>
                <span className="text-sky-400">{tpl.category}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Configuration Parameters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-5 rounded-xl bg-[#111C2D] border border-slate-800/80">
        <div>
          <label className="block text-[10px] font-mono text-slate-400 uppercase mb-1">
            Target Country Theater
          </label>
          <select
            value={selectedIso}
            onChange={(e) => setSelectedIso(e.target.value)}
            className="w-full bg-[#0D1422] border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono focus:border-purple-400 focus:outline-none"
          >
            {countries.map((c) => (
              <option key={c.country_iso} value={c.country_iso}>
                {c.country_name} ({c.country_iso}) - Current: {c.risk_index.toFixed(1)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[10px] font-mono text-slate-400 uppercase mb-1">
            Category
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full bg-[#0D1422] border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono focus:border-purple-400 focus:outline-none"
          >
            <option value="CONFLICT">CONFLICT (Weight: 1.0)</option>
            <option value="SECURITY">SECURITY (Weight: 0.8)</option>
            <option value="ECONOMY">ECONOMY (Weight: 0.6)</option>
            <option value="DIPLOMACY">DIPLOMACY (Weight: 0.4)</option>
          </select>
        </div>

        <div>
          <label className="block text-[10px] font-mono text-slate-400 uppercase mb-1">
            Incident Velocity: {incidentCount}
          </label>
          <input
            type="range"
            min="1"
            max="12"
            value={incidentCount}
            onChange={(e) => setIncidentCount(e.target.value)}
            className="w-full accent-purple-400 h-1.5 bg-slate-800 rounded-lg"
          />
        </div>
      </div>

      {/* Action Button */}
      <div className="flex items-center justify-between">
        <button
          onClick={handleRunSimulation}
          disabled={isSimulating}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-mono text-xs font-bold shadow-md transition-colors disabled:opacity-50"
        >
          <Play className="w-4 h-4" />
          <span>{isSimulating ? 'Executing Simulation Model...' : 'Execute What-If Model'}</span>
        </button>

        {error && <span className="text-xs text-rose-400 font-mono">{error}</span>}
      </div>

      {/* Simulation Result Output */}
      {simResult && (
        <div className="p-5 rounded-xl bg-[#111C2D] border border-purple-500/40 space-y-4 animate-fadeIn">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-mono font-bold text-slate-100 text-sm">
              <Zap className="w-4 h-4 text-purple-400" />
              <span>Projected Impact: {simResult.target_country}</span>
            </div>
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="text-slate-400">Baseline: {simResult.baseline_risk?.toFixed(1)}</span>
              <span>&rarr;</span>
              <span className="text-rose-400 font-bold">Surge: {simResult.projected_risk?.toFixed(1)}</span>
              <span className="text-rose-400 font-bold">
                (+{simResult.delta_risk?.toFixed(1)} / +{simResult.delta_percentage?.toFixed(1)}%)
              </span>
            </div>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.08)" vertical={false} />
                <XAxis dataKey="day" stroke="#476999" fontSize={10} tickLine={false} />
                <YAxis stroke="#476999" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0D1422',
                    borderColor: 'rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    fontSize: '11px',
                    color: '#F1F5F9',
                  }}
                />
                <Line type="monotone" dataKey="projected" name="Projected Risk" stroke="#A855F7" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );

  if (isInline) {
    return contentBlock;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/85 backdrop-blur-md overflow-y-auto font-sans">
      <div className="bg-[#0D1422] w-full max-w-4xl rounded-2xl border border-slate-800 shadow-2xl p-6 overflow-hidden flex flex-col max-h-[90vh]">
        {contentBlock}
      </div>
    </div>
  );
}
