import React, { useState, useRef, useEffect } from 'react';
import {
  Search,
  BellRing,
  RefreshCw,
  Radio,
  ChevronRight,
  X,
  Globe,
} from 'lucide-react';

export default function TopNav({
  currentView,
  wsConnected,
  isIngesting,
  onTriggerIngest,
  alerts = [],
  countries = [],
  onSelectCountry,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isAlertsOpen, setIsAlertsOpen] = useState(false);
  const alertsRef = useRef(null);
  const searchRef = useRef(null);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (alertsRef.current && !alertsRef.current.contains(event.target)) {
        setIsAlertsOpen(false);
      }
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsSearchOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter countries for quick jump
  const filteredCountries = searchQuery.trim()
    ? countries
        .filter(
          (c) =>
            c.country_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            c.country_iso?.toLowerCase().includes(searchQuery.toLowerCase())
        )
        .slice(0, 6)
    : [];

  const getBreadcrumb = () => {
    switch (currentView) {
      case 'dashboard':
        return 'World Risk Map & Overview';
      case 'analytics':
        return 'Risk Analytics & Forecasting';
      case 'news':
        return 'OSINT News Wire';
      case 'alerts':
        return 'Threat Alerts Log';
      default:
        return 'Dashboard';
    }
  };

  return (
    <header className="sticky top-0 z-20 h-14 bg-[#080D17]/95 backdrop-blur-md border-b border-slate-800/80 px-4 flex items-center justify-between gap-4">
      {/* Breadcrumbs */}
      <div className="flex items-center gap-2 text-xs font-mono">
        <span className="text-slate-400 font-bold hidden sm:inline">GEOSENTINEL</span>
        <ChevronRight className="w-3 h-3 text-slate-400 hidden sm:inline" />
        <span className="text-slate-200 font-semibold">{getBreadcrumb()}</span>
      </div>

      {/* Global Quick Search Bar */}
      <div className="relative flex-1 max-w-md hidden md:block" ref={searchRef}>
        <div className="relative flex items-center">
          <Search className="absolute left-3 w-3.5 h-3.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setIsSearchOpen(true);
            }}
            onFocus={() => setIsSearchOpen(true)}
            placeholder="Search countries or ISO codes..."
            className="w-full pl-9 pr-10 py-1.5 bg-[#0D1422] border border-slate-800 focus:border-sky-500/50 rounded-lg text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-500/30 transition-all font-sans"
          />
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('');
                setIsSearchOpen(false);
              }}
              className="absolute right-2.5 text-slate-400 hover:text-white"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Search Results Dropdown */}
        {isSearchOpen && searchQuery.trim() && (
          <div className="absolute left-0 right-0 top-full mt-1.5 bg-[#0D1422] border border-slate-700/80 rounded-xl shadow-2xl p-2 z-50 animate-fadeIn text-xs">
            <div className="px-2 py-1 text-[10px] font-mono text-slate-400 uppercase tracking-wider flex items-center justify-between border-b border-slate-800 pb-1 mb-1">
              <span>Countries</span>
              <button onClick={() => setIsSearchOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-3 h-3" />
              </button>
            </div>

            {filteredCountries.length === 0 ? (
              <div className="p-3 text-center text-slate-400 text-xs font-mono">
                No matching country found.
              </div>
            ) : (
              <div className="space-y-0.5">
                {filteredCountries.map((c) => (
                  <button
                    key={c.country_iso}
                    onClick={() => {
                      onSelectCountry(c.country_iso);
                      setIsSearchOpen(false);
                      setSearchQuery('');
                    }}
                    className="w-full flex items-center justify-between p-2 rounded-lg hover:bg-slate-800 text-slate-200 transition-colors text-left"
                  >
                    <div className="flex items-center gap-2">
                      <Globe className="w-3.5 h-3.5 text-sky-400" />
                      <span className="font-semibold">{c.country_name || c.country_iso}</span>
                      <span className="text-[10px] font-mono text-slate-400">({c.country_iso})</span>
                    </div>
                    <span
                      className={`px-1.5 py-0.2 rounded text-[10px] font-mono font-bold ${
                        c.risk_index > 60
                          ? 'bg-rose-500/20 text-rose-300'
                          : c.risk_index >= 30
                          ? 'bg-amber-500/20 text-amber-300'
                          : 'bg-emerald-500/20 text-emerald-300'
                      }`}
                    >
                      R: {c.risk_index.toFixed(1)}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right Action Tools */}
      <div className="flex items-center gap-2.5">
        {/* Real-time Ingestion Trigger Button */}
        <button
          onClick={onTriggerIngest}
          disabled={isIngesting}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all font-mono shadow-sm ${
            isIngesting
              ? 'bg-slate-800 text-slate-400 border border-slate-700 cursor-not-allowed'
              : 'bg-slate-850 hover:bg-slate-800 text-slate-200 border border-slate-700 hover:border-slate-600 active:scale-95'
          }`}
          title="Fetch latest news articles & recalculate risk indices"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-sky-400 ${isIngesting ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">{isIngesting ? 'Ingesting...' : 'Ingest Feeds'}</span>
        </button>

        {/* Notification Center Dropdown */}
        <div className="relative" ref={alertsRef}>
          <button
            onClick={() => setIsAlertsOpen(!isAlertsOpen)}
            className="relative p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-850 border border-slate-800 transition-colors"
            title="Notification Center"
          >
            <BellRing className="w-4 h-4" />
            {alerts.length > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-[#080D17]" />
            )}
          </button>

          {isAlertsOpen && (
            <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-[#0D1422] border border-slate-700/80 rounded-xl shadow-2xl p-3 z-50 animate-fadeIn text-xs">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
                <div className="font-mono font-bold text-slate-200 flex items-center gap-1.5">
                  <BellRing className="w-3.5 h-3.5 text-rose-400" />
                  <span>Critical Alerts ({alerts.length})</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">R &gt; 75 Threshold</span>
              </div>

              {alerts.length === 0 ? (
                <div className="py-6 text-center text-slate-400 font-mono text-xs">
                  No active critical alerts. Operating in baseline zone.
                </div>
              ) : (
                <div className="max-h-80 overflow-y-auto space-y-2 pr-1">
                  {alerts.slice(0, 6).map((a, i) => (
                    <button
                      key={a.alert_id || i}
                      onClick={() => {
                        setIsAlertsOpen(false);
                        onSelectCountry(a.country_iso || a.country);
                      }}
                      className="w-full text-left p-2.5 rounded-lg bg-slate-900 border border-rose-500/20 hover:border-rose-500/40 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-rose-950 text-rose-400 border border-rose-800/50">
                          {a.country_iso || a.country}
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono">
                          {new Date(a.sent_at || a.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-300">
                        Risk Score peaked at{' '}
                        <strong className="text-rose-400 font-mono">
                          {Number(a.risk_score).toFixed(1)} / 100
                        </strong>.
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Telemetry Stream Badge */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono border ${
            wsConnected
              ? 'bg-emerald-950/40 border-emerald-800/40 text-emerald-400'
              : 'bg-rose-950/40 border-rose-800/40 text-rose-400'
          }`}
          title={wsConnected ? 'WebSocket Live Feed Connected' : 'WebSocket Disconnected'}
        >
          <Radio className={`w-3 h-3 ${wsConnected ? 'animate-pulse' : ''}`} />
          <span className="text-[10px] font-bold hidden lg:inline">{wsConnected ? 'LIVE FEED' : 'OFFLINE'}</span>
        </div>
      </div>
    </header>
  );
}
