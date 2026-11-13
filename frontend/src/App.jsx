import React, { useState, useEffect, useMemo } from 'react';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
import KPICards from './components/KPICards';
import WorldRiskMap from './components/WorldRiskMap';
import RiskAnalyticsView from './components/RiskAnalyticsView';
import NewsExplorer from './components/NewsExplorer';
import AlertsView from './components/AlertsView';
import AssetWatchlistPanel from './components/AssetWatchlistPanel';
import ScenarioSimulatorModal from './components/ScenarioSimulatorModal';
import TacticalPlaybookModal from './components/TacticalPlaybookModal';
import SystemHealthModal from './components/SystemHealthModal';
import CountryDetailsModal from './components/CountryDetailsModal';
import DossierExportModal from './components/DossierExportModal';
import AiAnalystDrawer from './components/AiAnalystDrawer';
import AlertBanner from './components/AlertBanner';
import { useWebSocketAlerts } from './hooks/useWebSocketAlerts';
import { api } from './api/client';
import { CheckCircle2, Bot } from 'lucide-react';

export default function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [countries, setCountries] = useState([]);
  const [assets, setAssets] = useState([]);
  const [alertsHistory, setAlertsHistory] = useState([]);
  const [selectedIso, setSelectedIso] = useState(null);
  const [dossierIso, setDossierIso] = useState(null);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [activeLiveAlert, setActiveLiveAlert] = useState(null);
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestNotification, setIngestNotification] = useState(null);
  const [activePlaybookId, setActivePlaybookId] = useState(null);

  // Auto-authenticate as Admin on boot so user never encounters permission friction
  useEffect(() => {
    api.login('admin', 'admin123').catch((e) => console.warn('Admin auto-auth note:', e));
  }, []);

  // WebSocket Live Alert listener
  const { isConnected: wsConnected } = useWebSocketAlerts((newAlert) => {
    setActiveLiveAlert(newAlert);
    setAlertsHistory((prev) => [newAlert, ...prev]);
    loadDashboardData();
  });

  const loadDashboardData = () => {
    api.getRiskMap()
      .then((data) => setCountries(data || []))
      .catch((err) => console.error('Error loading map risk data:', err));

    api.getAssets()
      .then((data) => setAssets(data || []))
      .catch((err) => console.error('Error loading corporate assets:', err));

    api.getAlerts(30)
      .then((data) => setAlertsHistory(data.alerts || []))
      .catch((err) => console.error('Error loading alerts:', err));
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleTriggerIngest = async () => {
    setIsIngesting(true);
    try {
      const res = await api.runIngestion();
      loadDashboardData();
      setIngestNotification(
        `Ingested ${res.raw_articles_fetched} articles (${res.unique_articles_saved} unique, ${res.exact_duplicates + res.near_duplicates} deduped). Recalculated risk across ${res.affected_countries_count} regions.`
      );
      setTimeout(() => setIngestNotification(null), 6000);
    } catch (e) {
      console.error('Ingestion failed:', e);
    } finally {
      setIsIngesting(false);
    }
  };

  // Aggregated KPI Metrics
  const totalEvents = useMemo(
    () => countries.reduce((acc, c) => acc + (c.event_count || 0), 0),
    [countries]
  );
  const severeCountries = useMemo(
    () => countries.filter((c) => c.risk_index > 60).length,
    [countries]
  );
  const criticalAssetsCount = useMemo(
    () => assets.filter((a) => a.threat_level === 'CRITICAL').length,
    [assets]
  );
  const avgRisk = useMemo(() => {
    if (countries.length === 0) return 0;
    const sum = countries.reduce((acc, c) => acc + (c.risk_index || 0), 0);
    return sum / countries.length;
  }, [countries]);

  return (
    <div className="min-h-screen bg-[#080D17] text-slate-100 flex flex-col font-sans selection:bg-sky-500/30 selection:text-sky-200">
      {/* Real-time Alert Toast Banner */}
      <AlertBanner
        alert={activeLiveAlert}
        onDismiss={() => setActiveLiveAlert(null)}
        onInspect={(iso) => {
          setActiveLiveAlert(null);
          setSelectedIso(iso);
        }}
      />

      {/* Collapsible Left Navigation Sidebar */}
      <Sidebar
        currentView={currentView}
        onSelectView={setCurrentView}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        alertsCount={alertsHistory.length}
        assetsCount={assets.length}
        wsConnected={wsConnected}
        onOpenCopilot={() => setIsCopilotOpen(true)}
      />

      {/* Main Content Area (Offset by Sidebar Width) */}
      <div
        className={`flex-1 flex flex-col transition-all duration-300 ease-in-out ${
          isSidebarCollapsed ? 'ml-16' : 'ml-64'
        }`}
      >
        {/* Top Navigation & Global Search Header */}
        <TopNav
          currentView={currentView}
          wsConnected={wsConnected}
          isIngesting={isIngesting}
          onTriggerIngest={handleTriggerIngest}
          onOpenCopilot={() => setIsCopilotOpen(true)}
          alerts={alertsHistory}
          countries={countries}
          assets={assets}
          onSelectCountry={(iso) => setSelectedIso(iso)}
          onSelectAsset={(asset) => {
            if (asset?.country_iso) setSelectedIso(asset.country_iso);
          }}
        />

        {/* Live Ingestion Toast Notification */}
        {ingestNotification && (
          <div className="bg-sky-950/80 border-b border-sky-800 text-sky-200 text-xs px-4 py-2 flex items-center justify-center gap-2 animate-fadeIn font-mono">
            <CheckCircle2 className="w-4 h-4 text-sky-400 shrink-0" />
            <span>{ingestNotification}</span>
          </div>
        )}

        {/* Dynamic View Viewport */}
        <main className="flex-1 p-4 md:p-6 space-y-6 max-w-[1600px] w-full mx-auto">
          {/* VIEW: Tactical Map & Overview */}
          {currentView === 'dashboard' && (
            <div className="space-y-5 animate-fadeIn">
              {/* Executive KPI Metrics Ribbon */}
              <KPICards
                countriesCount={countries.length}
                eventsCount={totalEvents}
                severeCount={severeCountries}
                alertCount={alertsHistory.length}
                assetsCount={assets.length}
                criticalAssetsCount={criticalAssetsCount}
                avgRisk={avgRisk}
                onOpenAssets={() => setCurrentView('assets')}
              />

              {/* Interactive World Risk Map */}
              <WorldRiskMap
                countries={countries}
                assets={assets}
                selectedIso={selectedIso}
                onSelectCountry={(iso) => setSelectedIso(iso)}
                onSelectAsset={(asset) => {
                  if (asset?.country_iso) setSelectedIso(asset.country_iso);
                }}
              />
            </div>
          )}

          {/* VIEW: Risk Analytics & Forecasting */}
          {currentView === 'analytics' && (
            <div className="animate-fadeIn">
              <RiskAnalyticsView
                countries={countries}
                onSelectCountry={(iso) => setSelectedIso(iso)}
              />
            </div>
          )}

          {/* VIEW: OSINT News Wire Feed */}
          {currentView === 'news' && (
            <div className="space-y-4 animate-fadeIn">
              <div className="bg-[#111C2D] p-5 rounded-xl border border-slate-800/80 shadow-sm flex items-center justify-between">
                <div>
                  <h2 className="text-base font-bold font-mono text-slate-100 uppercase tracking-wider">
                    Real-Time Open-Source Intelligence (OSINT) News Wire
                  </h2>
                  <p className="text-xs text-slate-400 font-sans">
                    Ingested from global news portals (BBC World News, Al Jazeera, UN News, Deutsche Welle, NewsAPI)
                  </p>
                </div>
              </div>
              <NewsExplorer />
            </div>
          )}

          {/* VIEW: Live Alerts & Webhook Logs */}
          {currentView === 'alerts' && (
            <div className="animate-fadeIn">
              <AlertsView
                alerts={alertsHistory}
                onInspectCountry={(iso) => setSelectedIso(iso)}
                onTriggerIngest={handleTriggerIngest}
                isIngesting={isIngesting}
              />
            </div>
          )}

          {/* VIEW: Corporate Asset Geofences Portfolio */}
          {currentView === 'assets' && (
            <div className="animate-fadeIn">
              <AssetWatchlistPanel
                assets={assets}
                isInline={true}
                onRefreshAssets={loadDashboardData}
                onSelectAsset={(asset) => {
                  if (asset?.country_iso) setSelectedIso(asset.country_iso);
                }}
                onOpenPlaybook={(asset) => {
                  setCurrentView('playbooks');
                }}
              />
            </div>
          )}

          {/* VIEW: What-If Scenario Simulation Sandbox */}
          {currentView === 'simulation' && (
            <div className="animate-fadeIn">
              <ScenarioSimulatorModal
                isInline={true}
                countries={countries}
              />
            </div>
          )}

          {/* VIEW: Action Mitigation Playbooks */}
          {currentView === 'playbooks' && (
            <div className="animate-fadeIn">
              <TacticalPlaybookModal
                isInline={true}
                initialPlaybookId={activePlaybookId}
              />
            </div>
          )}

          {/* VIEW: System Diagnostics & Health */}
          {currentView === 'health' && (
            <div className="animate-fadeIn">
              <SystemHealthModal
                isInline={true}
                wsConnected={wsConnected}
              />
            </div>
          )}
        </main>

        {/* Global Footer */}
        <footer className="border-t border-slate-800/80 bg-[#080D17] py-3.5 px-6 text-xs text-slate-400 font-mono mt-auto">
          <div className="max-w-[1600px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
            <span className="flex items-center gap-2 text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              GeoSentinel AI &bull; Enterprise Threat Operations Center (GTOC v2.4)
            </span>
            <span className="text-slate-500 text-[11px]">
              Mathematical Geopolitical Modeling &amp; Corporate Asset Geofencing Suite
            </span>
          </div>
        </footer>
      </div>

      {/* Floating Copilot Launcher Button */}
      {!isCopilotOpen && (
        <button
          onClick={() => setIsCopilotOpen(true)}
          className="fixed bottom-5 right-5 z-40 flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-gradient-to-r from-sky-600 to-indigo-600 text-white font-mono text-xs font-bold shadow-lg shadow-sky-950/60 hover:scale-105 transition-all border border-sky-400/30"
          title="Open GeoSentinel AI Intelligence Copilot"
        >
          <Bot className="w-4 h-4 text-sky-200" />
          <span>Ask Copilot</span>
        </button>
      )}

      {/* Sliding AI Copilot Drawer */}
      <AiAnalystDrawer
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
      />

      {/* Country Detail & Evidence Modal */}
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
    </div>
  );
}
