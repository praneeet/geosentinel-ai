import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import KPICards from './components/KPICards';
import WorldRiskMap from './components/WorldRiskMap';
import CountryDetailsModal from './components/CountryDetailsModal';
import TrendCharts from './components/TrendCharts';
import NewsExplorer from './components/NewsExplorer';
import AlertBanner from './components/AlertBanner';
import DossierExportModal from './components/DossierExportModal';
import SystemHealthModal from './components/SystemHealthModal';
import { useWebSocketAlerts } from './hooks/useWebSocketAlerts';
import { api } from './api/client';
import { BellRing, ShieldAlert, CheckCircle } from 'lucide-react';

export default function App() {
  const [countries, setCountries] = useState([]);
  const [selectedIso, setSelectedIso] = useState(null);
  const [dossierIso, setDossierIso] = useState(null);
  const [isHealthOpen, setIsHealthOpen] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [activeView, setActiveView] = useState('dashboard'); // 'dashboard', 'news', 'alerts'
  const [alertsHistory, setAlertsHistory] = useState([]);
  const [activeLiveAlert, setActiveLiveAlert] = useState(null);
  const [ingestNotification, setIngestNotification] = useState(null);

  // WebSocket Live Alert listener
  const { isConnected: wsConnected } = useWebSocketAlerts((newAlert) => {
    setActiveLiveAlert(newAlert);
    setAlertsHistory((prev) => [newAlert, ...prev]);
    // Refresh map data to reflect new risk scores
    loadDashboardData();
  });

  const loadDashboardData = () => {
    api.getRiskMap()
      .then((data) => setCountries(data || []))
      .catch((err) => console.error("Error loading map risk data:", err));

    api.getAlerts(20)
      .then((data) => setAlertsHistory(data.alerts || []))
      .catch((err) => console.error("Error loading alerts:", err));
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleTriggerIngest = async () => {
    setIsIngesting(true);
    try {
      const res = await api.runIngestion();
      loadDashboardData();
      setIngestNotification(`Ingested ${res.raw_articles_fetched} articles (${res.unique_articles_saved} unique, ${res.exact_duplicates + res.near_duplicates} deduped). Recalculated risk across ${res.affected_countries_count} regions.`);
      setTimeout(() => setIngestNotification(null), 6000);
    } catch (e) {
      console.error("Ingestion failed:", e);
    } finally {
      setIsIngesting(false);
    }
  };

  // Compute KPI figures
  const totalEvents = countries.reduce((acc, c) => acc + (c.event_count || 0), 0);
  const severeCountries = countries.filter((c) => c.risk_index > 60).length;

  return (
    <div className="min-h-screen bg-[#06090e] text-slate-100 flex flex-col selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Real-time Alert Toast Banner */}
      <AlertBanner
        alert={activeLiveAlert}
        onDismiss={() => setActiveLiveAlert(null)}
        onInspect={(iso) => {
          setActiveLiveAlert(null);
          setSelectedIso(iso);
        }}
      />

      {/* Global Header */}
      <Header
        wsConnected={wsConnected}
        isIngesting={isIngesting}
        onTriggerIngest={handleTriggerIngest}
        onOpenHealth={() => setIsHealthOpen(true)}
        criticalAlertCount={alertsHistory.length}
        activeView={activeView}
        setActiveView={setActiveView}
      />

      {/* Ingestion Flash Notification */}
      {ingestNotification && (
        <div className="bg-cyan-950/80 border-b border-cyan-800 text-cyan-200 text-xs px-4 py-2 flex items-center justify-center gap-2 animate-fadeIn">
          <CheckCircle className="w-4 h-4 text-cyan-400" />
          <span>{ingestNotification}</span>
        </div>
      )}

      {/* Main Analytical View Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-6">
        {/* KPI Telemetry Banner */}
        <KPICards
          countriesCount={countries.length}
          eventsCount={totalEvents}
          severeCount={severeCountries}
          alertCount={alertsHistory.length}
          dupRate={0.0}
        />

        {/* Dynamic View Content */}
        {activeView === 'dashboard' && (
          <div className="space-y-6">
            {/* World Risk Map */}
            <WorldRiskMap
              countries={countries}
              selectedIso={selectedIso}
              onSelectCountry={(iso) => setSelectedIso(iso)}
            />

            {/* Longitudinal Trend Charts */}
            <TrendCharts />
          </div>
        )}

        {activeView === 'news' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold tracking-wider text-slate-200 uppercase font-mono">
                Real-Time Open-Source Intelligence (OSINT) News Wire
              </h2>
            </div>
            <NewsExplorer />
          </div>
        )}

        {activeView === 'alerts' && (
          <div className="glass-panel p-6 rounded-xl border border-sentinel-700/60 shadow-lg space-y-4">
            <div className="flex items-center justify-between border-b border-sentinel-700 pb-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-red-500" />
                <h2 className="text-sm font-bold uppercase font-mono tracking-wider text-white">
                  Critical Risk Threshold Alerts Log (R &gt; 75)
                </h2>
              </div>
              <span className="text-xs font-mono text-slate-400">
                Total Broadcasts: {alertsHistory.length}
              </span>
            </div>

            {alertsHistory.length === 0 ? (
              <div className="py-16 text-center text-slate-400 font-mono text-xs">
                No critical alerts recorded. System operating within normal risk thresholds.
              </div>
            ) : (
              <div className="space-y-3">
                {alertsHistory.map((item, idx) => (
                  <div
                    key={item.alert_id || idx}
                    className="p-4 rounded-lg bg-sentinel-950/80 border border-red-800/40 hover:border-red-600/70 transition-colors flex items-center justify-between gap-4"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-red-950 text-red-400 border border-red-800">
                          CRITICAL ALERT
                        </span>
                        <span className="font-bold text-sm text-white">
                          {item.country_iso || item.country}
                        </span>
                        <span className="text-xs text-slate-400 font-mono">
                          {new Date(item.sent_at || item.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300">
                        Country Risk Score exceeded threshold with composite value of{' '}
                        <strong className="text-red-400 font-mono">
                          {Number(item.risk_score).toFixed(1)} / 100
                        </strong>.
                      </p>
                    </div>

                    <button
                      onClick={() => setSelectedIso(item.country_iso || item.country)}
                      className="px-3 py-1.5 rounded text-xs font-semibold bg-sentinel-900 hover:bg-sentinel-800 text-cyan-400 border border-sentinel-700 transition-colors flex-shrink-0"
                    >
                      Inspect Country
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Country Detail Modal */}
      {selectedIso && (
        <CountryDetailsModal
          iso={selectedIso}
          onClose={() => setSelectedIso(null)}
          onOpenDossier={(iso) => {
            setSelectedIso(null);
            setDossierIso(iso);
          }}
        />
      )}

      {/* Strategic Intelligence Dossier Modal */}
      {dossierIso && (
        <DossierExportModal
          iso={dossierIso}
          onClose={() => setDossierIso(null)}
        />
      )}

      {/* System Health & Diagnostics Modal */}
      {isHealthOpen && (
        <SystemHealthModal
          onClose={() => setIsHealthOpen(false)}
          wsConnected={wsConnected}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-sentinel-800/60 bg-[#05080c] py-4 px-6 text-center text-xs text-slate-400 font-mono">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>GeoSentinel AI &bull; B.Tech Final Year Capstone Project 2026</span>
          <span>Ajay Kumar Garg Engineering College, Ghaziabad &bull; IT Dept</span>
        </div>
      </footer>
    </div>
  );
}
