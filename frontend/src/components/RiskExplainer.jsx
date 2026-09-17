import React from 'react';
import { HelpCircle, Clock, HeartHandshake, ShieldAlert, TrendingUp, ExternalLink, ArrowRight } from 'lucide-react';

export default function RiskExplainer({ explanation, countryName, riskIndex, riskTier }) {
  if (!explanation) return null;

  const cats = explanation.category_breakdown || {};
  const retention = explanation.temporal_retention_pct || 100;
  const sentimentMag = explanation.sentiment_magnitude || 0;

  return (
    <div className="glass-panel p-4 rounded-xl border border-sentinel-700/60 shadow-lg flex flex-col gap-3">
      <div className="flex items-center justify-between border-b border-sentinel-700/60 pb-2">
        <div className="flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold uppercase font-mono tracking-wider text-slate-200">
            Explainable Risk Scoring Decomposition (Eq. 1)
          </h3>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-sentinel-800 text-slate-300">
          R = {riskIndex.toFixed(1)} / 100 &bull; {riskTier}
        </span>
      </div>

      {/* Formula Audit Box */}
      <div className="bg-sentinel-950/80 p-3 rounded-lg border border-sentinel-700/60 font-mono text-[11px] text-slate-300">
        <div className="text-cyan-400 mb-1 font-bold">
          R_c(t) = min(100, (&alpha; / N) &Sigma; [w_i &times; |S_a,i| &times; c_s,i &times; e^(-&lambda;(t - t_i))])
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px] text-slate-400 mt-2 border-t border-sentinel-800 pt-2">
          <div>&alpha; (Scalar): <span className="text-white font-semibold">4.25</span></div>
          <div>&lambda; (Half-Life): <span className="text-white font-semibold">ln(2)/7 &approx; 0.0990</span></div>
          <div>Freshness Retention: <span className="text-white font-semibold">{retention}%</span></div>
          <div>Avg Polarity |S|: <span className="text-white font-semibold">{sentimentMag.toFixed(2)}</span></div>
        </div>
      </div>

      {/* Domain Contributions Breakdown */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div className="bg-rose-950/30 border border-rose-800/40 p-2.5 rounded-lg">
          <div className="text-[10px] text-rose-300/80 font-mono uppercase">Conflict (w=1.00)</div>
          <div className="text-lg font-bold font-mono text-rose-400">
            +{Number(cats.Conflict || 0).toFixed(1)} <span className="text-xs font-normal text-rose-300/60">pts</span>
          </div>
        </div>

        <div className="bg-amber-950/30 border border-amber-800/40 p-2.5 rounded-lg">
          <div className="text-[10px] text-amber-300/80 font-mono uppercase">Security (w=0.80)</div>
          <div className="text-lg font-bold font-mono text-amber-400">
            +{Number(cats.Security || 0).toFixed(1)} <span className="text-xs font-normal text-amber-300/60">pts</span>
          </div>
        </div>

        <div className="bg-blue-950/30 border border-blue-800/40 p-2.5 rounded-lg">
          <div className="text-[10px] text-blue-300/80 font-mono uppercase">Economy (w=0.55)</div>
          <div className="text-lg font-bold font-mono text-blue-400">
            +{Number(cats.Economy || 0).toFixed(1)} <span className="text-xs font-normal text-blue-300/60">pts</span>
          </div>
        </div>

        <div className="bg-emerald-950/30 border border-emerald-800/40 p-2.5 rounded-lg">
          <div className="text-[10px] text-emerald-300/80 font-mono uppercase">Diplomacy (w=0.35)</div>
          <div className="text-lg font-bold font-mono text-emerald-400">
            +{Number(cats.Diplomacy || 0).toFixed(1)} <span className="text-xs font-normal text-emerald-300/60">pts</span>
          </div>
        </div>
      </div>

      {/* Narrative Synthesis */}
      <div className="space-y-1.5 text-xs text-slate-300 leading-relaxed bg-sentinel-900/50 p-2.5 rounded-lg border border-sentinel-800/50">
        {(explanation.narrative || []).map((line, idx) => (
          <p key={idx} className="flex items-start gap-1.5">
            <span className="text-cyan-400 font-bold">&bull;</span>
            <span>{line}</span>
          </p>
        ))}
      </div>
    </div>
  );
}
