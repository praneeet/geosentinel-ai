import React from 'react';
import { AlertTriangle, X, ArrowRight, ShieldAlert } from 'lucide-react';

export default function AlertBanner({ alert, onDismiss, onInspect }) {
  if (!alert) return null;

  return (
    <div className="fixed top-16 right-4 z-50 max-w-md w-full animate-bounce-short">
      <div className="p-4 rounded-xl bg-gradient-to-r from-red-950 via-rose-950 to-sentinel-950 border-2 border-red-500/80 shadow-2xl shadow-red-950/80 text-white relative flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </span>
            <span className="font-mono font-bold text-xs uppercase tracking-widest text-red-400 flex items-center gap-1">
              <ShieldAlert className="w-4 h-4" />
              CRITICAL RISK ALERT TRIGGERED (R &gt; 75)
            </span>
          </div>

          <button
            onClick={onDismiss}
            className="text-slate-400 hover:text-white p-1 rounded hover:bg-white/10"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div>
          <div className="flex items-center justify-between">
            <h4 className="text-base font-extrabold text-white">
              {alert.country_name || alert.country}
            </h4>
            <span className="font-mono font-bold text-lg text-red-400">
              {Number(alert.risk_score).toFixed(1)} <span className="text-xs text-slate-300">/ 100</span>
            </span>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            Country composite risk has breached the severe escalation threshold. Continuous 7-day half-life decay applied.
          </p>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-red-800/40 text-xs mt-1">
          <span className="font-mono text-[10px] text-slate-400">
            {new Date(alert.timestamp).toLocaleTimeString()}
          </span>
          <button
            onClick={() => onInspect(alert.country)}
            className="flex items-center gap-1 px-3 py-1 rounded bg-red-600 hover:bg-red-500 font-bold text-white transition-colors text-xs"
          >
            <span>Inspect Evidence</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
