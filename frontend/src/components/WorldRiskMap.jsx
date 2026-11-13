import React, { useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Circle, Polyline, Popup, Tooltip } from 'react-leaflet';
import { Shield, Eye, Flame, AlertCircle, Navigation, Building2, Layers, Anchor } from 'lucide-react';
import { STRATEGIC_CHOKEPOINTS } from '../data/chokepoints';

export default function WorldRiskMap({
  countries = [],
  assets = [],
  onSelectCountry,
  onSelectAsset,
  selectedIso,
}) {
  const [filterTier, setFilterTier] = useState('ALL');
  const [showAssets, setShowAssets] = useState(true);
  const [showChokepoints, setShowChokepoints] = useState(true);
  const [basemap, setBasemap] = useState('dark');

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
    <div className="bg-[#111C2D] rounded-xl border border-slate-800/80 p-4 shadow-sm flex flex-col h-[600px]">
      {/* Map Control Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-sky-400" />
          <h2 className="text-sm font-semibold tracking-wider text-slate-100 uppercase font-mono">
            Global Geopolitical Risk &amp; Corporate Asset Map
          </h2>
        </div>

        {/* Filter & Layer Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAssets(!showAssets)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-mono transition-all ${
              showAssets
                ? 'bg-sky-500/15 text-sky-300 border-sky-500/40 shadow-sm'
                : 'bg-[#0D1422] text-slate-400 border-slate-800 hover:text-slate-200'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Corporate Assets {showAssets ? 'ON' : 'OFF'}</span>
          </button>

          <button
            onClick={() => setShowChokepoints(!showChokepoints)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-mono transition-all ${
              showChokepoints
                ? 'bg-amber-500/15 text-amber-300 border-amber-500/40 shadow-sm'
                : 'bg-[#0D1422] text-slate-400 border-slate-800 hover:text-slate-200'
            }`}
          >
            <Anchor className="w-3.5 h-3.5" />
            <span>Maritime Chokepoints {showChokepoints ? 'ON' : 'OFF'}</span>
          </button>

          {/* Basemap Selector */}
          <div className="flex items-center gap-1 bg-[#0D1422] p-1 rounded-lg border border-slate-800 text-xs">
            <Layers className="w-3.5 h-3.5 text-sky-400 ml-1 mr-0.5" />
            <button
              onClick={() => setBasemap('dark')}
              className={`px-2 py-0.5 rounded font-mono text-[11px] transition-colors ${
                basemap === 'dark'
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Dark
            </button>
            <button
              onClick={() => setBasemap('satellite')}
              className={`px-2 py-0.5 rounded font-mono text-[11px] transition-colors ${
                basemap === 'satellite'
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Satellite
            </button>
            <button
              onClick={() => setBasemap('osm')}
              className={`px-2 py-0.5 rounded font-mono text-[11px] transition-colors ${
                basemap === 'osm'
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
                className={`px-2 py-0.5 rounded font-medium transition-colors text-[11px] ${
                  filterTier === tier
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
          {/* Esri World Dark Gray Canvas (Default: Crisp, high-tech GTOC dark map, completely free with NO API key needed) */}
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

          {/* Tactical High-Resolution Satellite Imagery */}
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

          {/* Corporate Pinned Assets & Geofence Buffers Layer */}
          {showAssets && (
            <>
              {assets.map((asset) => {
                const threatColor =
                  asset.threat_level === 'CRITICAL'
                    ? '#f43f5e'
                    : asset.threat_level === 'HIGH'
                    ? '#f59e0b'
                    : asset.threat_level === 'ELEVATED'
                    ? '#eab308'
                    : '#38bdf8';

                return (
                  <React.Fragment key={asset.asset_id}>
                    {/* Geofence circular buffer boundary */}
                    <Circle
                      center={[asset.latitude, asset.longitude]}
                      radius={asset.buffer_radius_km * 1000}
                      pathOptions={{
                        color: threatColor,
                        weight: 1.5,
                        dashArray: '6, 8',
                        fillColor: threatColor,
                        fillOpacity: 0.06,
                      }}
                    />

                    {/* Asset facility beacon */}
                    <CircleMarker
                      center={[asset.latitude, asset.longitude]}
                      radius={8}
                      pathOptions={{
                        color: '#ffffff',
                        weight: 2,
                        fillColor: threatColor,
                        fillOpacity: 0.95,
                      }}
                    >
                      <Tooltip direction="top" offset={[0, -10]} opacity={0.95}>
                        <div className="font-mono text-xs">
                          <strong className="text-white block">{asset.name}</strong>
                          <span className="text-[10px] text-slate-300">
                            [{asset.asset_type}] &bull; Threat: {asset.threat_level} ({asset.threat_score})
                          </span>
                        </div>
                      </Tooltip>

                      <Popup>
                        <div className="p-2 text-slate-200 max-w-xs font-sans">
                          <div className="flex items-center gap-1.5 text-cyan-400 font-bold text-sm border-b border-sentinel-700 pb-1 mb-2 font-mono">
                            <Building2 className="w-4 h-4 text-cyan-400" />
                            <span>{asset.name}</span>
                          </div>
                          <div className="text-xs text-slate-400 mb-1">
                            <span className="font-semibold text-slate-200 font-mono">Type:</span> {asset.asset_type}
                          </div>
                          <div className="text-xs text-slate-400 mb-1">
                            <span className="font-semibold text-slate-200 font-mono">Territory:</span> {asset.country_name} ({asset.country_iso})
                          </div>
                          <div className="text-xs text-slate-400 mb-1">
                            <span className="font-semibold text-slate-200 font-mono">Geofence Radius:</span> {asset.buffer_radius_km} km
                          </div>
                          <div className="text-xs text-slate-400 mb-2 font-mono">
                            <span className="font-semibold text-slate-200">Threat Score:</span>{' '}
                            <strong style={{ color: threatColor }}>{asset.threat_score.toFixed(1)} / 100 ({asset.threat_level})</strong>
                          </div>
                          <div className="p-2 rounded bg-sentinel-950 border border-sentinel-750 text-[11px] text-slate-300 mb-3 leading-relaxed">
                            <strong className="text-cyan-400 block text-[10px] font-mono mb-0.5">DIRECTIVE:</strong>
                            {asset.prescriptive_directive}
                          </div>
                          <button
                            onClick={() => onSelectAsset && onSelectAsset(asset)}
                            className="w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono font-bold text-xs transition-colors shadow"
                          >
                            <span>Inspect Asset Threat Profile</span>
                          </button>
                        </div>
                      </Popup>
                    </CircleMarker>
                  </React.Fragment>
                );
              })}
            </>
          )}

          {/* Strategic Maritime Chokepoints & Supply Chain Corridors */}
          {showChokepoints &&
            STRATEGIC_CHOKEPOINTS.map((cp) => (
              <React.Fragment key={cp.id}>
                {cp.corridor && (
                  <Polyline
                    positions={cp.corridor}
                    pathOptions={{
                      color: '#f59e0b',
                      weight: 2,
                      dashArray: '5, 8',
                      opacity: 0.8,
                    }}
                  />
                )}
                <CircleMarker
                  center={[cp.lat, cp.lon]}
                  radius={7}
                  pathOptions={{
                    color: '#ffffff',
                    weight: 1.5,
                    fillColor: '#d97706',
                    fillOpacity: 0.95,
                  }}
                >
                  <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
                    <div className="font-mono text-xs">
                      <strong className="text-amber-300 block">{cp.name}</strong>
                      <span className="text-[10px] text-slate-300">
                        {cp.tradeShare} &bull; Vulnerability: {cp.vulnerabilityLevel}
                      </span>
                    </div>
                  </Tooltip>
                  <Popup>
                    <div className="p-2 text-slate-200 max-w-xs font-sans">
                      <div className="flex items-center gap-1.5 text-amber-400 font-bold text-sm border-b border-slate-700 pb-1 mb-2 font-mono">
                        <Anchor className="w-4 h-4 text-amber-400" />
                        <span>{cp.name}</span>
                      </div>
                      <div className="text-xs text-slate-400 mb-1">
                        <span className="font-semibold text-slate-200 font-mono">Transit Share:</span> {cp.tradeShare}
                      </div>
                      <div className="text-xs text-slate-400 mb-1">
                        <span className="font-semibold text-slate-200 font-mono">Vulnerability:</span>{' '}
                        <strong className="text-amber-400 font-mono">{cp.vulnerabilityLevel}</strong>
                      </div>
                      <p className="text-[11px] text-slate-300 mt-2 mb-2 leading-relaxed">
                        {cp.description}
                      </p>
                    </div>
                  </Popup>
                </CircleMarker>
              </React.Fragment>
            ))}

          {/* Country Risk Markers */}
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
        <div className="absolute bottom-3 right-3 z-20 bg-[#0D1422]/95 backdrop-blur-md p-3 rounded-xl border border-slate-800 shadow-xl text-xs flex flex-col gap-1.5 font-mono pointer-events-auto">
          <div className="text-[10px] uppercase text-slate-400 tracking-wider font-bold mb-0.5">
            Tactical Map Legend
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
          <div className="flex items-center gap-2 border-t border-slate-800 pt-1.5 mt-0.5">
            <Building2 className="w-3.5 h-3.5 text-sky-400" />
            <span className="text-sky-300">Corporate Geofence Buffer</span>
          </div>
          <div className="flex items-center gap-2">
            <Anchor className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-amber-300">Maritime Chokepoint &amp; Corridor</span>
          </div>
        </div>
      </div>
    </div>
  );
}
