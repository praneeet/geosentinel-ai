import React, { useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import { Shield, Eye, Flame, AlertCircle } from 'lucide-react';

export default function WorldRiskMap({ countries = [], onSelectCountry, selectedIso }) {
  const [filterTier, setFilterTier] = useState('ALL');

  const filteredCountries = countries.filter((c) => {
    if (filterTier === 'ALL') return true;
    return c.risk_tier.toUpperCase() === filterTier.toUpperCase();
  });

  const getMarkerColor = (risk) => {
    if (risk > 75) return '#dc2626'; // Alert Red
    if (risk > 60) return '#ef4444'; // Severe Crimson
    if (risk >= 30) return '#f59e0b'; // Moderate Amber
    return '#10b981'; // Low Emerald
  };

  const getMarkerRadius = (risk, count) => {
    return Math.max(8, Math.min(26, 8 + Math.sqrt(risk) * 1.8 + Math.log1p(count) * 2));
  };

  return (
    <div className="glass-panel rounded-xl border border-sentinel-700/60 p-4 shadow-xl flex flex-col h-[560px]">
      {/* Map Control Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-semibold tracking-wider text-slate-200 uppercase font-mono">
            Global Geopolitical Risk Choropleth Map
          </h2>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-1.5 bg-sentinel-950/80 p-1 rounded-lg border border-sentinel-700/50 text-xs">
          <span className="text-slate-400 px-2 font-mono text-[11px]">Filter:</span>
          {['ALL', 'SEVERE', 'MODERATE', 'LOW'].map((tier) => (
            <button
              key={tier}
              onClick={() => setFilterTier(tier)}
              className={`px-2 py-0.5 rounded font-medium transition-colors text-[11px] ${
                filterTier === tier
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* Leaflet Map Canvas */}
      <div className="flex-1 w-full rounded-lg overflow-hidden border border-sentinel-700/50 relative">
        <MapContainer
          center={[25.0, 30.0]}
          zoom={2.2}
          minZoom={1.5}
          maxZoom={7}
          style={{ height: '100%', width: '100%' }}
          className="z-10"
        >
          {/* CartoDB Dark Matter Basemap */}
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {filteredCountries.map((c) => {
            const color = getMarkerColor(c.risk_index);
            const radius = getMarkerRadius(c.risk_index, c.event_count);
            const isSelected = selectedIso === c.country_iso;
            const isCritical = c.risk_index > 75;

            return (
              <CircleMarker
                key={c.country_iso}
                center={[c.lat, c.lon]}
                radius={radius}
                pathOptions={{
                  fillColor: color,
                  fillOpacity: isSelected ? 0.95 : 0.75,
                  color: isSelected ? '#38bdf8' : isCritical ? '#f87171' : color,
                  weight: isSelected ? 3 : isCritical ? 2.5 : 1.5,
                }}
                eventHandlers={{
                  click: () => onSelectCountry(c.country_iso),
                }}
              >
                <Tooltip direction="top" offset={[0, -10]} opacity={0.95}>
                  <div className="text-xs p-1 font-sans">
                    <div className="font-bold text-white flex items-center gap-1.5">
                      <span>{c.country_name}</span>
                      <span className="font-mono text-[10px] text-cyan-400">({c.country_iso})</span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="font-mono font-bold text-sm" style={{ color }}>
                        {c.risk_index.toFixed(1)} / 100
                      </span>
                      <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-slate-800 text-slate-300">
                        {c.risk_tier}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      {c.event_count} active events
                    </div>
                  </div>
                </Tooltip>

                <Popup>
                  <div className="p-2 text-slate-200">
                    <h3 className="font-bold text-sm flex items-center justify-between border-b border-sentinel-700 pb-1 mb-2">
                      <span>{c.country_name}</span>
                      <span className="text-xs font-mono text-cyan-400">{c.country_iso}</span>
                    </h3>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-slate-400">Risk Score:</span>
                      <span className="font-mono font-bold text-base" style={{ color }}>
                        {c.risk_index.toFixed(1)} <span className="text-xs text-slate-400">/ 100</span>
                      </span>
                    </div>
                    <div className="flex items-center justify-between mb-3 text-xs">
                      <span className="text-slate-400">Tier Status:</span>
                      <span className="font-semibold" style={{ color }}>
                        {c.risk_tier}
                      </span>
                    </div>
                    <button
                      onClick={() => onSelectCountry(c.country_iso)}
                      className="w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs transition-colors shadow"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Inspect Dossier &amp; Evidence</span>
                    </button>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* Tactical Map Legend */}
        <div className="absolute bottom-3 right-3 z-20 glass-panel p-2.5 rounded-lg border border-sentinel-700/80 shadow-2xl text-xs flex flex-col gap-1.5 font-mono pointer-events-auto">
          <div className="text-[10px] uppercase text-slate-400 tracking-wider font-bold mb-0.5">
            Risk Tier Scale
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10b981]"></span>
            <span className="text-slate-300">Low (R &lt; 30)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]"></span>
            <span className="text-slate-300">Moderate (30 &le; R &le; 60)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444]"></span>
            <span className="text-slate-300">Severe (R &gt; 60)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#dc2626] ring-2 ring-red-500/50"></span>
            <span className="text-red-400 font-bold">Critical Alert (R &gt; 75)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
