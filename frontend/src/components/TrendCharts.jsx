import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend, Cell } from 'recharts';
import { TrendingUp, BarChart3, Activity, PieChart as PieIcon } from 'lucide-react';
import { api } from '../api/client';

export default function TrendCharts() {
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [windowDays, setWindowDays] = useState(30);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    api.getTrends(windowDays)
      .then((data) => {
        if (isMounted) setTrends(data);
      })
      .catch((err) => console.error("Error loading trends:", err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [windowDays]);

  if (loading || !trends) {
    return (
      <div className="glass-panel p-8 rounded-xl text-center text-cyan-400 font-mono text-xs animate-pulse">
        Calculating Global Trend Trajectories...
      </div>
    );
  }

  const categoryData = Object.entries(trends.category_distribution || {}).map(([cat, count]) => {
    const colors = {
      CONFLICT: '#ef4444',
      SECURITY: '#f59e0b',
      ECONOMY: '#3b82f6',
      DIPLOMACY: '#10b981',
    };
    return { name: cat, count, fill: colors[cat] || '#8b5cf6' };
  });

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-semibold tracking-wider text-slate-200 uppercase font-mono">
            Global Longitudinal Analysis &amp; Velocity
          </h2>
        </div>

        <div className="flex items-center gap-1 text-xs font-mono">
          {[14, 30, 60].map((d) => (
            <button
              key={d}
              onClick={() => setWindowDays(d)}
              className={`px-3 py-1 rounded transition-colors ${
                windowDays === d
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Daily Event Ingestion Velocity */}
        <div className="glass-panel p-4 rounded-xl border border-sentinel-700/60 shadow-lg flex flex-col h-[300px]">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-bold font-mono uppercase text-slate-200 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              Daily Event Ingestion Volume
            </h3>
            <span className="text-[10px] font-mono text-slate-400">Events / Day</span>
          </div>

          <div className="flex-1 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends.timeline || []}>
                <defs>
                  <linearGradient id="eventGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#162234" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#0e1724', borderColor: '#1e3048', fontSize: '11px' }} />
                <Area type="monotone" dataKey="events" stroke="#38bdf8" fillOpacity={1} fill="url(#eventGradient)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Global Domain Distribution */}
        <div className="glass-panel p-4 rounded-xl border border-sentinel-700/60 shadow-lg flex flex-col h-[300px]">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-bold font-mono uppercase text-slate-200 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-amber-400" />
              Domain Event Aggregation
            </h3>
            <span className="text-[10px] font-mono text-slate-400">DistilBERT 4-Class</span>
          </div>

          <div className="flex-1 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#162234" />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#0e1724', borderColor: '#1e3048', fontSize: '11px' }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
