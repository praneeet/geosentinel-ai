import React from 'react';
import { Globe, Zap, AlertOctagon, BellRing, Filter, Clock } from 'lucide-react';

export default function KPICards({
  countriesCount = 0,
  eventsCount = 0,
  severeCount = 0,
  alertCount = 0,
  dupRate = 0.0,
}) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {/* Countries Monitored */}
      <div className="glass-panel p-3.5 rounded-xl border border-sentinel-700/60 shadow-lg">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs uppercase font-mono tracking-wider">Monitored</span>
          <Globe className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="text-2xl font-bold font-mono text-white tracking-tight">
          {countriesCount}
        </div>
        <span className="text-[11px] text-cyan-400/80 font-medium">Sovereign Nations</span>
      </div>

      {/* Events Processed */}
      <div className="glass-panel p-3.5 rounded-xl border border-sentinel-700/60 shadow-lg">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs uppercase font-mono tracking-wider">Active Events</span>
          <Zap className="w-4 h-4 text-amber-400" />
        </div>
        <div className="text-2xl font-bold font-mono text-white tracking-tight">
          {eventsCount}
        </div>
        <span className="text-[11px] text-amber-400/80 font-medium">NLP Classified Tuples</span>
      </div>

      {/* Severe Risk Nations */}
      <div className="glass-panel p-3.5 rounded-xl border border-sentinel-700/60 shadow-lg">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs uppercase font-mono tracking-wider">Severe Risk</span>
          <AlertOctagon className="w-4 h-4 text-rose-400" />
        </div>
        <div className="text-2xl font-bold font-mono text-rose-400 tracking-tight">
          {severeCount}
        </div>
        <span className="text-[11px] text-rose-400/80 font-medium">R &gt; 60 Threshold</span>
      </div>

      {/* Active Alerts */}
      <div className="glass-panel p-3.5 rounded-xl border border-sentinel-700/60 shadow-lg">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs uppercase font-mono tracking-wider">Critical Alerts</span>
          <BellRing className="w-4 h-4 text-red-500" />
        </div>
        <div className="text-2xl font-bold font-mono text-red-500 tracking-tight">
          {alertCount}
        </div>
        <span className="text-[11px] text-red-400/80 font-medium">R &gt; 75 Dispatched</span>
      </div>

      {/* Dedup Filter */}
      <div className="glass-panel p-3.5 rounded-xl border border-sentinel-700/60 shadow-lg">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs uppercase font-mono tracking-wider">Dedup Leakage</span>
          <Filter className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-2xl font-bold font-mono text-emerald-400 tracking-tight">
          {dupRate.toFixed(1)}%
        </div>
        <span className="text-[11px] text-emerald-400/80 font-medium">&lt; 1% Target Met</span>
      </div>

      {/* Temporal Half-Life */}
      <div className="glass-panel p-3.5 rounded-xl border border-sentinel-700/60 shadow-lg">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs uppercase font-mono tracking-wider">Half-Life Decay</span>
          <Clock className="w-4 h-4 text-purple-400" />
        </div>
        <div className="text-2xl font-bold font-mono text-purple-400 tracking-tight">
          7.0 d
        </div>
        <span className="text-[11px] text-purple-400/80 font-medium">&lambda; = ln(2)/7</span>
      </div>
    </div>
  );
}
