import React, { useState, useEffect } from 'react';
import {
  X,
  Printer,
  Download,
  Shield,
  Sparkles,
  ExternalLink,
  Activity,
  Info,
} from 'lucide-react';
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
      .catch((err) => console.error('Error generating dossier:', err))
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/85 backdrop-blur-md overflow-y-auto font-sans animate-fadeIn">
      <div className="bg-[#0D1422] w-full max-w-4xl rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Modal Action Bar */}
        <div className="flex items-center justify-between px-6 py-3.5 border-b border-slate-800 bg-[#080D17]">
          <div className="flex items-center gap-2 text-sky-400 font-mono text-xs font-bold uppercase tracking-wider">
            <Shield className="w-4 h-4" />
            <span>Strategic Intelligence Briefing Dossier</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-850 hover:bg-slate-800 text-slate-200 border border-slate-750 transition-colors disabled:opacity-40"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print / PDF</span>
            </button>
            <button
              onClick={handleDownloadJSON}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-sky-600 hover:bg-sky-500 text-white transition-colors disabled:opacity-40"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export JSON</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-850 hover:bg-slate-800 border border-slate-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Dossier Document Content */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-[#0A0F1D] text-slate-200 print:bg-white print:text-black">
          {loading ? (
            <div className="py-24 text-center text-sky-400 font-mono text-xs animate-pulse">
              Compiling Executive Dossier &amp; Primary Citations...
            </div>
          ) : (
            <div className="space-y-6 max-w-3xl mx-auto font-sans">
              {/* Document Header */}
              <div className="border-b-2 border-slate-800 pb-4">
                <div className="text-[10px] font-mono tracking-widest text-sky-400 uppercase font-bold mb-1">
                  {dossier.classification || 'PROPRIETARY EXECUTIVE INTELLIGENCE'}
                </div>
                <h1 className="text-xl font-extrabold text-white print:text-black tracking-tight">
                  COUNTRY INTELLIGENCE DOSSIER: {dossier.country_name} ({dossier.country_iso})
                </h1>
                <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-400 mt-2">
                  <span>Generated: {new Date(dossier.generated_at).toUTCString()}</span>
                  <span>Report ID: {dossier.report_id?.slice(0, 8)}</span>
                  <span>Platform: GeoSentinel Enterprise v2.4</span>
                </div>
              </div>

              {/* Research Disclaimer */}
              <div className="p-3.5 rounded-lg bg-[#0D1422] border border-amber-800/40 text-xs text-amber-200/90 leading-relaxed flex items-start gap-2.5">
                <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span>{dossier.disclaimer}</span>
              </div>

              {/* KPI Summary Block */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-4 rounded-xl bg-[#111C2D] border border-slate-800 text-center font-mono">
                  <span className="text-[10px] uppercase text-slate-400">Current Risk Index</span>
                  <div className="text-3xl font-extrabold text-slate-100 print:text-black mt-1">
                    {dossier.current_risk?.toFixed(1)} <span className="text-xs text-slate-400">/ 100</span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-[#111C2D] border border-slate-800 text-center font-mono">
                  <span className="text-[10px] uppercase text-slate-400">Risk Tier</span>
                  <div className="text-lg font-bold text-sky-400 mt-1">
                    {dossier.risk_tier}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-[#111C2D] border border-slate-800 text-center font-mono">
                  <span className="text-[10px] uppercase text-slate-400">Trend Trajectory</span>
                  <div className="text-lg font-bold text-amber-400 mt-1">
                    {dossier.risk_trend}
                  </div>
                </div>
              </div>

              {/* Executive Summary Section */}
              <div className="space-y-2.5">
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-sky-400 border-b border-slate-800 pb-1">
                  1. Executive Briefing (BART Abstractive Summarization)
                </h3>
                <div className="space-y-2 text-xs leading-relaxed">
                  {(dossier.executive_briefing || []).map((point, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-[#111C2D] border border-slate-800">
                      <strong className="text-sky-400 mr-2">&bull;</strong>
                      {point}
                    </div>
                  ))}
                </div>
              </div>

              {/* Primary Citations */}
              {dossier.recent_events && (
                <div className="space-y-2.5">
                  <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-sky-400 border-b border-slate-800 pb-1">
                    2. Primary Source Evidence Trail ({dossier.recent_events.length} Events)
                  </h3>
                  <div className="space-y-2">
                    {dossier.recent_events.map((ev, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-[#111C2D] border border-slate-800 flex items-center justify-between gap-3 text-xs">
                        <div className="space-y-0.5">
                          <div className="font-mono text-[10px] text-slate-400">{ev.category} &bull; {ev.source}</div>
                          <div className="font-semibold text-slate-200">{ev.title}</div>
                        </div>
                        {ev.url && (
                          <a href={ev.url} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline flex items-center gap-1 font-mono text-xs shrink-0">
                            <span>Link</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
