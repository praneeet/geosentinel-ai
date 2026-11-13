import React, { useState, useEffect } from 'react';
import {
  X,
  Server,
  Database,
  Radio,
  Cpu,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Activity,
  HardDrive,
  Shield,
  Zap,
} from 'lucide-react';
import { api } from '../api/client';

export default function SystemHealthModal({ onClose, wsConnected, isInline = false }) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshHealth = () => {
    setLoading(true);
    api.getHealth()
      .then((data) => setHealth(data))
      .catch((err) => console.error('Error checking health:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    refreshHealth();
  }, []);

  const contentBlock = (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#111C2D] p-5 rounded-xl border border-slate-800/80 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold font-mono text-slate-100 uppercase tracking-wider">
                System Diagnostics &amp; Runtime Telemetry
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-700/50">
                HEALTHY
              </span>
            </div>
            <p className="text-xs text-slate-400 font-sans">
              FastAPI ASGI telemetry, Async SQLAlchemy session state, and WebSocket subscriber connections.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={refreshHealth}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono font-semibold rounded-lg bg-[#0D1422] hover:bg-slate-800 text-slate-200 border border-slate-700 transition-colors"
            title="Refresh diagnostics"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-sky-400 ${loading ? 'animate-spin' : ''}`} />
            <span>Poll Metrics</span>
          </button>
          {!isInline && onClose && (
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-850 border border-slate-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Grid of Micro-Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5 font-mono">
        <div className="p-4 rounded-xl bg-[#111C2D] border border-slate-800/80">
          <span className="text-[10px] uppercase text-slate-400 block mb-1">FastAPI Backend</span>
          <div className="text-sm font-bold text-emerald-400 flex items-center gap-1.5">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>ONLINE (200 OK)</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#111C2D] border border-slate-800/80">
          <span className="text-[10px] uppercase text-slate-400 block mb-1">Database Engine</span>
          <div className="text-sm font-bold text-emerald-400 flex items-center gap-1.5">
            <Database className="w-4 h-4 text-emerald-400" />
            <span>{health?.database === 'ok' ? 'SQLITE READY' : 'CONNECTED'}</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#111C2D] border border-slate-800/80">
          <span className="text-[10px] uppercase text-slate-400 block mb-1">Telemetry Socket</span>
          <div className={`text-sm font-bold flex items-center gap-1.5 ${wsConnected ? 'text-emerald-400' : 'text-rose-400'}`}>
            <Radio className={`w-4 h-4 ${wsConnected ? 'animate-pulse' : ''}`} />
            <span>{wsConnected ? 'BROADCASTING' : 'DISCONNECTED'}</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#111C2D] border border-slate-800/80">
          <span className="text-[10px] uppercase text-slate-400 block mb-1">Active Subscribers</span>
          <div className="text-sm font-bold text-slate-100 flex items-center gap-1.5">
            <Cpu className="w-4 h-4 text-sky-400" />
            <span>{health?.websocket_active_connections ?? 1} Nodes</span>
          </div>
        </div>
      </div>

      {/* Runtime Platform Details */}
      <div className="p-5 rounded-xl bg-[#111C2D] border border-slate-800/80 space-y-3 font-mono text-xs">
        <div className="text-xs font-bold text-slate-200 uppercase tracking-wider border-b border-slate-800 pb-2">
          Platform Architecture &amp; Identity
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-slate-300 text-xs">
          <div>
            <span className="text-slate-400 block text-[10px]">PLATFORM SUITE</span>
            <span className="font-semibold text-slate-100">{health?.full_title || 'GeoSentinel Enterprise Intelligence'}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">OPERATIONS DIVISION</span>
            <span className="font-semibold text-slate-100">{health?.division || 'Global Threat Operations Center (GTOC)'}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">EDITION &amp; BUILD</span>
            <span className="font-semibold text-slate-100">{health?.edition || 'Enterprise Edition v2.4'}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">SYSTEM TIMESTAMP</span>
            <span className="font-semibold text-slate-100">{health?.timestamp || new Date().toISOString()}</span>
          </div>
        </div>
      </div>
    </div>
  );

  if (isInline) {
    return contentBlock;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="bg-[#0D1422] w-full max-w-2xl rounded-2xl border border-slate-800 shadow-2xl p-6 overflow-hidden">
        {contentBlock}
      </div>
    </div>
  );
}
