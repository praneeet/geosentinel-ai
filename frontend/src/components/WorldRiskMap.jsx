import React, { useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import { Shield, Eye, Layers } from 'lucide-react';

export default function WorldRiskMap({
  countries = [],
  onSelectCountry,
  selectedIso,
}) {
  const [filterTier, setFilterTier] = useState('ALL');
  const [basemap, setBasemap] = useState('dark');

  const filteredCountries = countries.filter((c) => {
    if (filterTier === 'ALL') return true;
    return c.risk_tier.toUpperCase() === filterTier.toUpperCase();
  });

  const getMarkerColor = (risk, count) => {
    if (!count || count === 0) return '#64748b'; // Slate: Unmonitored / No Active Signals
    if (risk > 75) return '#dc2626'; // Alert Red
    if (risk > 60) return '#ef4444'; // Severe Crimson
    if (risk >= 30) return '#f59e0b'; // Moderate Amber
    return '#10b981'; // Low Emerald
  };

  const getMarkerRadius = (risk, count) => {
    if (!count || count === 0) return 6;
    return Math.max(8, Math.min(26, 8 + Math.sqrt(risk) * 1.8 + Math.log1p(count) * 2));
  };

  return (
    <div className="bg-[#111C2D] rounded-xl border border-slate-800/80 p-4 shadow-sm flex flex-col h-[600px]">
      {/* Map Control Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-sky-400" />
          <h2 className="text-sm font-semibold tracking-wider text-slate-100 uppercase font-mono">
            Global Geopolitical Risk Map
          </h2>
        </div>

        {/* Filter & Layer Controls */}
        <div className="flex items-center gap-2">
          {/* Basemap Selector */}
          <div className="flex items-center gap-1 bg-[#0D1422] p-1 rounded-lg border border-slate-800 text-xs">
            <Layers className="w-3.5 h-3.5 text-sky-400 ml-1 mr-0.5" />
            <button
              onClick={() => setBasemap('dark')}
              className={`px-2 py-0.5 rounded font-mono text-[11px] transition-colors ${basemap === 'dark'
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              Dark
            </button>
            <button
              onClick={() => setBasemap('satellite')}
              className={`px-2 py-0.5 rounded font-mono text-[11px] transition-colors ${basemap === 'satellite'
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              Satellite
            </button>
            <button
              onClick={() => setBasemap('osm')}
              className={`px-2 py-0.5 rounded font-mono text-[11px] transition-colors ${basemap === 'osm'
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              OSM
            </button>
          </div>

          <div className="flex items-center gap-1 bg-[#0D1422] p-1 rounded-lg border border-slate-800 text-xs">
            <span className="text-slate-400 px-2 font-mono text-[11px]">Filter:</span>
            {['ALL', 'SEVERE', 'MODERATE', 'LOW'].map((tier) => (
              <button
                key={tier}
                onClick={() => setFilterTier(tier)}
                className={`px-2 py-0.5 rounded font-medium transition-colors text-[11px] ${filterTier === tier
                    ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                  }`}
              >
                {tier}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Leaflet Map Canvas */}
      <div className="flex-1 w-full rounded-xl overflow-hidden border border-slate-800 relative">
        <MapContainer
          center={[23.0, 35.0]}
          zoom={2.3}
          minZoom={1.5}
          maxZoom={7}
          style={{ height: '100%', width: '100%' }}
          className="z-10"
        >
          {/* Esri World Dark Gray Canvas */}
          {basemap === 'dark' && (
            <>
              <TileLayer
                attribution='Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
                url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
                maxZoom={16}
              />
              <TileLayer
                attribution=''
                url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}"
                maxZoom={16}
              />
            </>
          )}

          {/* Satellite Imagery */}
          {basemap === 'satellite' && (
            <TileLayer
              attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              maxZoom={17}
            />
          )}

          {/* OpenStreetMap Standard Vector Basemap */}
          {basemap === 'osm' && (
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              maxZoom={18}
            />
          )}

          {/* Country Risk Markers */}
          {filteredCountries.map((c) => {
            const hasData = (c.event_count || 0) > 0;
            const color = getMarkerColor(c.risk_index, c.event_count);
            const radius = getMarkerRadius(c.risk_index, c.event_count);
            const isSelected = selectedIso === c.country_iso;
            const isCritical = c.risk_index > 75 && hasData;

            return (
              <CircleMarker
                key={c.country_iso}
                center={[c.lat, c.lon]}
                radius={radius}
                pathOptions={{
                  fillColor: color,
                  fillOpacity: isSelected ? 0.95 : hasData ? 0.75 : 0.40,
                  color: isSelected ? '#38bdf8' : isCritical ? '#f87171' : color,
                  weight: isSelected ? 3 : isCritical ? 2.5 : hasData ? 1.5 : 1,
                  dashArray: hasData ? null : '2, 4',
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
                    {hasData ? (
                      <>
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
                      </>
                    ) : (
                      <div className="text-[10px] text-slate-400 mt-1 italic">
                        No active OSINT signals recorded
                      </div>
                    )}
                  </div>
                </Tooltip>

                <Popup>
                  <div className="p-2 text-slate-200">
                    <h3 className="font-bold text-sm flex items-center justify-between border-b border-sentinel-700 pb-1 mb-2">
                      <span>{c.country_name}</span>
                      <span className="text-xs font-mono text-cyan-400">{c.country_iso}</span>
                    </h3>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-slate-400">Status / Risk:</span>
                      {hasData ? (
                        <span className="font-mono font-bold text-base" style={{ color }}>
                          {c.risk_index.toFixed(1)} <span className="text-xs text-slate-400">/ 100</span>
                        </span>
                      ) : (
                        <span className="font-mono text-xs text-slate-400">No Active Events</span>
                      )}
                    </div>
                    <div className="flex items-center justify-between mb-3 text-xs">
                      <span className="text-slate-400">Tier Status:</span>
                      <span className="font-semibold" style={{ color }}>
                        {hasData ? c.risk_tier : 'Unmonitored / Baseline'}
                      </span>
                    </div>
                    <button
                      onClick={() => onSelectCountry(c.country_iso)}
                      className="w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs transition-colors shadow"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Inspect Country Evidence</span>
                    </button>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* Map Legend */}
        <div className="absolute bottom-3 right-3 z-20 bg-[#0D1422]/95 backdrop-blur-md p-3 rounded-xl border border-slate-800 shadow-xl text-xs flex flex-col gap-1.5 font-mono pointer-events-auto">
          <div className="text-[10px] uppercase text-slate-400 tracking-wider font-bold mb-0.5">
            Risk Tier Legend
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#64748B] border border-dashed border-slate-500"></span>
            <span className="text-slate-400">No Active OSINT Signals</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#22C55E]"></span>
            <span className="text-slate-300">Low (R &lt; 30)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]"></span>
            <span className="text-slate-300">Moderate (30 &le; R &le; 60)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]"></span>
            <span className="text-slate-300">Severe (R &gt; 60)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#DC2626] ring-2 ring-rose-500/50"></span>
            <span className="text-rose-400 font-bold">Critical Alert (R &gt; 75)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
