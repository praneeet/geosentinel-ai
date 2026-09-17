import React, { useState, useEffect } from 'react';
import { X, Printer, Download, Shield, Sparkles, ExternalLink, Activity, Info } from 'lucide-react';
import { api } from '../api/client';

export default function DossierExportModal({ iso, onClose }) {
  const [dossier, setDossier] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!iso) return;
    let isMounted = true;
    setLoading(true);

    api.generateReport(iso)
      .then((data) => {
        if (isMounted) setDossier(data);
      })
      .catch((err) => console.error("Error generating dossier:", err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [iso]);

  if (!iso) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadJSON = () => {
    if (!dossier) return;
    const blob = new Blob([JSON.stringify(dossier, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `GeoSentinel_${iso}_Intelligence_Dossier_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/85 backdrop-blur-md overflow-y-auto">
      <div className="glass-panel w-full max-w-4xl rounded-2xl border border-sentinel-700/80 shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Modal Action Bar */}
        <div className="flex items-center justify-between px-6 py-3.5 border-b border-sentinel-700 bg-sentinel-950/80">
          <div className="flex items-center gap-2 text-cyan-400 font-mono text-xs font-bold uppercase tracking-wider">
            <Shield className="w-4 h-4" />
            <span>Strategic Intelligence Briefing Dossier</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded bg-sentinel-800 hover:bg-sentinel-700 text-slate-200 border border-sentinel-600 transition-colors"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print / PDF</span>
            </button>
            <button
              onClick={handleDownloadJSON}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded bg-cyan-600 hover:bg-cyan-500 text-white transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export JSON</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded bg-sentinel-900 hover:bg-sentinel-800 border border-sentinel-700"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Dossier Document Content */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-[#0a0f18] text-slate-200 print:bg-white print:text-black">
          {loading ? (
            <div className="py-24 text-center text-cyan-400 font-mono text-sm animate-pulse">
              Compiling Executive Dossier &amp; Primary Citations...
            </div>
          ) : (
            <div className="space-y-6 max-w-3xl mx-auto">
              {/* Document Header */}
              <div className="border-b-2 border-sentinel-700 pb-4">
                <div className="text-[11px] font-mono tracking-widest text-cyan-400 uppercase font-bold mb-1">
                  {dossier.classification}
                </div>
                <h1 className="text-2xl font-extrabold text-white print:text-black tracking-tight">
                  COUNTRY INTELLIGENCE DOSSIER: {dossier.country_name} ({dossier.country_iso})
                </h1>
                <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-400 mt-2">
                  <span>Generated: {new Date(dossier.generated_at).toUTCString()}</span>
                  <span>Report ID: {dossier.report_id.slice(0, 8)}</span>
                  <span>Platform: GeoSentinel AI v1.0.0</span>
                </div>
              </div>

              {/* Research Disclaimer */}
              <div className="p-3 rounded-lg bg-sentinel-950 border border-amber-800/40 text-xs text-amber-200/90 leading-relaxed flex items-start gap-2">
                <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                <span>{dossier.disclaimer}</span>
              </div>

              {/* KPI Summary Block */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3.5 rounded-lg bg-sentinel-900/60 border border-sentinel-700 text-center">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Current Risk Index</span>
                  <div className="text-3xl font-extrabold font-mono text-white print:text-black mt-1">
                    {dossier.current_risk.toFixed(1)} <span className="text-xs text-slate-400">/ 100</span>
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-sentinel-900/60 border border-sentinel-700 text-center">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Risk Tier</span>
                  <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
                    {dossier.risk_tier}
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-sentinel-900/60 border border-sentinel-700 text-center">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Trend Trajectory</span>
                  <div className="text-xl font-bold font-mono text-amber-400 mt-1">
                    {dossier.risk_trend}
                  </div>
                </div>
              </div>

              {/* Executive Summary Section */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-cyan-400 border-b border-sentinel-800 pb-1">
                  1. Executive Briefing (BART Abstractive Summarization)
                </h3>
                <div className="space-y-2 text-xs leading-relaxed">
                  {dossier.executive_briefing.map((point, idx) => (
                    <div key={idx} className="p-2.5 rounded bg-sentinel-950/70 border border-sentinel-800">
                      <strong className="text-cyan-300 mr-1.5">&bull;</strong>
                      {point}
                    </div>
                  ))}
                </div>
              </div>

              {/* Domain Breakdown Section */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-cyan-400 border-b border-sentinel-800 pb-1">
                  2. Mathematical Contribution Breakdown (Eq. 1)
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                  {Object.entries(dossier.contributing_breakdown).map(([cat, score]) => (
                    <div key={cat} className="p-2.5 rounded bg-sentinel-950 border border-sentinel-800">
                      <div className="text-slate-400 text-[10px] uppercase">{cat}</div>
                      <div className="text-base font-bold text-white mt-0.5">+{Number(score).toFixed(1)} pts</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Experimental Forecasting Section */}
              {dossier.experimental_forecast && dossier.experimental_forecast.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-amber-400 border-b border-sentinel-800 pb-1 flex items-center justify-between">
                    <span>3. Experimental Trend-Based Forecast (Proof-of-Concept)</span>
                    <span className="text-[10px] text-slate-400">Non-deterministic</span>
                  </h3>
                  <div className="grid grid-cols-7 gap-1.5 text-center text-xs font-mono">
                    {dossier.experimental_forecast.map((pt, i) => (
                      <div key={i} className="p-2 rounded bg-sentinel-950 border border-sentinel-800">
                        <div className="text-[10px] text-slate-400">Day +{i + 1}</div>
                        <div className="text-sm font-bold text-amber-300">{pt.forecast_risk}</div>
                        <div className="text-[9px] text-slate-500">[{pt.lower_bound}-{pt.upper_bound}]</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recent Events & Citations Section */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-cyan-400 border-b border-sentinel-800 pb-1">
                  4. Chronological Event Evidence &amp; Source Citations
                </h3>
                <div className="space-y-2">
                  {dossier.recent_events.map((ev) => (
                    <div key={ev.event_id} className="p-2.5 rounded bg-sentinel-950 border border-sentinel-800 text-xs">
                      <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mb-1">
                        <span>[{ev.category}] &bull; {new Date(ev.timestamp).toLocaleDateString()}</span>
                        <span className="text-cyan-400">{ev.source_name}</span>
                      </div>
                      <p className="text-slate-200 font-medium mb-1">{ev.title}</p>
                      <a
                        href={ev.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] text-cyan-400 hover:underline flex items-center gap-1"
                      >
                        <span>{ev.source_url}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  ))}
                </div>
              </div>

              {/* Model & Version Attributions */}
              <div className="border-t border-sentinel-800 pt-4 text-[10px] font-mono text-slate-400 space-y-1">
                <div className="font-bold text-slate-300 mb-1">AI/ML System Architecture &amp; Models:</div>
                {Object.entries(dossier.model_versions).map(([k, v]) => (
                  <div key={k}>&bull; {k}: <span className="text-slate-200">{v}</span></div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
