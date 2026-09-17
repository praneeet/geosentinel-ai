import React from 'react';
import { Shield, Radio, Activity, RefreshCw, AlertTriangle, FileText, Server } from 'lucide-react';

export default function Header({
  wsConnected,
  isIngesting,
  onTriggerIngest,
  onOpenHealth,
  criticalAlertCount = 0,
  activeView,
  setActiveView,
}) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-sentinel-700/70 bg-[#070b12]/90 backdrop-blur-md px-4 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Brand & Team Info */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-600/30 border border-cyan-500/40 text-cyan-400 shadow-lg shadow-cyan-950/40">
            <Shield className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-wider text-white bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-cyan-400">
                GEOSENTINEL AI
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-mono tracking-widest bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 rounded">
                v1.0.0
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wider bg-amber-950/70 text-amber-300 border border-amber-700/60 rounded-full animate-pulse">
                DEMO DATA
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              AKGEC Dept of IT &bull; CSIT Group 32 &bull; SDG 16 &amp; SDG 9
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1 bg-sentinel-900/80 p-1 rounded-lg border border-sentinel-700/50">
          <button
            onClick={() => setActiveView('dashboard')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeView === 'dashboard'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-sentinel-800/40'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveView('news')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeView === 'news'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-sentinel-800/40'
            }`}
          >
            News Wire
          </button>
          <button
            onClick={() => setActiveView('alerts')}
            className={`relative px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeView === 'alerts'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-sentinel-800/40'
            }`}
          >
            Alerts
            {criticalAlertCount > 0 && (
              <span className="ml-1.5 px-1.5 py-0.2 bg-red-500 text-white rounded-full text-[10px] font-bold">
                {criticalAlertCount}
              </span>
            )}
          </button>
        </div>

        {/* Live Status & Actions */}
        <div className="flex items-center gap-2">
          {/* WebSocket Status */}
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono border ${
              wsConnected
                ? 'bg-emerald-950/60 border-emerald-800/50 text-emerald-400'
                : 'bg-rose-950/60 border-rose-800/50 text-rose-400'
            }`}
            title={wsConnected ? 'WebSocket live alert telemetry connected' : 'WebSocket disconnected'}
          >
            <Radio className={`w-3.5 h-3.5 ${wsConnected ? 'animate-pulse' : ''}`} />
            <span className="text-[11px]">{wsConnected ? 'LIVE FEED' : 'OFFLINE'}</span>
          </div>

          {/* Trigger Ingest Button */}
          <button
            onClick={onTriggerIngest}
            disabled={isIngesting}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md bg-sentinel-800 hover:bg-sentinel-700 text-slate-200 border border-sentinel-600 transition-colors disabled:opacity-50"
            title="Poll news feeds and recalculate country risk"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isIngesting ? 'animate-spin text-cyan-400' : ''}`} />
            <span>{isIngesting ? 'Ingesting...' : 'Ingest News'}</span>
          </button>

          {/* System Health Probe */}
          <button
            onClick={onOpenHealth}
            className="p-1.5 text-slate-400 hover:text-cyan-300 bg-sentinel-900 hover:bg-sentinel-800 rounded-md border border-sentinel-700 transition-colors"
            title="Observability & System Diagnostics"
          >
            <Server className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
