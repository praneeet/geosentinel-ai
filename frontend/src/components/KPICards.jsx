import React from 'react';
import { Globe, Zap, AlertTriangle, BellRing, Building2, TrendingUp } from 'lucide-react';

export default function KPICards({
  countriesCount = 0,
  eventsCount = 0,
  severeCount = 0,
  alertCount = 0,
  assetsCount = 0,
  criticalAssetsCount = 0,
  onOpenAssets,
  avgRisk = 42.4,
}) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
      {/* 1. Monitored Countries */}
      <div className="bg-[#111C2D] p-3.5 rounded-xl border border-slate-800/80 shadow-sm hover:border-slate-700 transition-colors">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[10px] uppercase font-mono font-semibold tracking-wider">Monitored States</span>
          <Globe className="w-3.5 h-3.5 text-sky-400" />
        </div>
        <div className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
          {countriesCount}
        </div>
        <div className="mt-1 flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>Global Coverage</span>
        </div>
      </div>

      {/* 2. Global Risk Index Composite */}
      <div className="bg-[#111C2D] p-3.5 rounded-xl border border-slate-800/80 shadow-sm hover:border-slate-700 transition-colors">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[10px] uppercase font-mono font-semibold tracking-wider">Mean Risk Index</span>
          <TrendingUp className="w-3.5 h-3.5 text-indigo-400" />
        </div>
        <div className="text-2xl font-bold font-mono text-indigo-300 tracking-tight">
          {Number(avgRisk).toFixed(1)} <span className="text-xs font-normal text-slate-400">/ 100</span>
        </div>
        <div className="mt-1 flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
          <span className="text-amber-400 font-semibold">Moderate</span>
          <span>(7-Day Decay)</span>
        </div>
      </div>

      {/* 3. Corporate Assets Geofenced */}
      <div
        onClick={onOpenAssets}
        className="bg-[#111C2D] p-3.5 rounded-xl border border-sky-500/30 hover:border-sky-500/60 shadow-sm cursor-pointer transition-all group bg-gradient-to-br from-sky-950/20 to-transparent"
      >
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[10px] uppercase font-mono font-semibold tracking-wider text-sky-300">
            Corporate Assets
          </span>
          <Building2 className="w-3.5 h-3.5 text-sky-400 group-hover:scale-110 transition-transform" />
        </div>
        <div className="text-2xl font-bold font-mono text-sky-300 tracking-tight">
          {assetsCount}
        </div>
        <div className="mt-1 text-[10px] font-mono">
          {criticalAssetsCount > 0 ? (
            <span className="text-rose-400 font-bold flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span>
              {criticalAssetsCount} In Conflict Buffer
            </span>
          ) : (
            <span className="text-emerald-400 font-medium">All Geofences Clear</span>
          )}
        </div>
      </div>

      {/* 4. Active Classified Events */}
      <div className="bg-[#111C2D] p-3.5 rounded-xl border border-slate-800/80 shadow-sm hover:border-slate-700 transition-colors">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[10px] uppercase font-mono font-semibold tracking-wider">Active Incidents</span>
          <Zap className="w-3.5 h-3.5 text-amber-400" />
        </div>
        <div className="text-2xl font-bold font-mono text-amber-400 tracking-tight">
          {eventsCount}
        </div>
        <div className="mt-1 flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
          <span>NLP Sentiment &amp; NER</span>
        </div>
      </div>

      {/* 5. Severe Risk Nations */}
      <div className="bg-[#111C2D] p-3.5 rounded-xl border border-slate-800/80 shadow-sm hover:border-slate-700 transition-colors">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[10px] uppercase font-mono font-semibold tracking-wider">Severe Theaters</span>
          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
        </div>
        <div className="text-2xl font-bold font-mono text-rose-400 tracking-tight">
          {severeCount}
        </div>
        <div className="mt-1 text-[10px] font-mono text-rose-400/80">
          <span>R &gt; 60 Crisis Level</span>
        </div>
      </div>

      {/* 6. Threshold Broadcast Alerts */}
      <div className="bg-[#111C2D] p-3.5 rounded-xl border border-slate-800/80 shadow-sm hover:border-slate-700 transition-colors">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[10px] uppercase font-mono font-semibold tracking-wider">Threshold Alerts</span>
          <BellRing className="w-3.5 h-3.5 text-rose-500" />
        </div>
        <div className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
          {alertCount}
        </div>
        <div className="mt-1 text-[10px] font-mono text-slate-400">
          <span>Discord &amp; Telegram Push</span>
        </div>
      </div>
    </div>
  );
}
