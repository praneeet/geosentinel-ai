import React, { useState } from 'react';
import {
  Shield,
  Building2,
  Anchor,
  Server,
  Warehouse,
  MapPin,
  AlertTriangle,
  Plus,
  Trash2,
  X,
  Compass,
  ExternalLink,
} from 'lucide-react';
import { api } from '../api/client';

export default function AssetWatchlistPanel({
  assets = [],
  onSelectAsset,
  onRefreshAssets,
  onOpenPlaybook,
  onClose,
  isInline = false,
}) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newAsset, setNewAsset] = useState({
    name: '',
    asset_type: 'FACILITY',
    country_iso: 'TWN',
    latitude: 25.033,
    longitude: 121.565,
    buffer_radius_km: 200,
    criticality: 'TIER_1_MISSION_CRITICAL',
    description: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const getAssetIcon = (type) => {
    switch (type.toUpperCase()) {
      case 'MARITIME_VESSEL':
        return <Anchor className="w-4 h-4 text-sky-400" />;
      case 'DATA_CENTER':
        return <Server className="w-4 h-4 text-indigo-400" />;
      case 'PORT':
        return <Compass className="w-4 h-4 text-amber-400" />;
      case 'SUPPLY_DEPOT':
        return <Warehouse className="w-4 h-4 text-emerald-400" />;
      default:
        return <Building2 className="w-4 h-4 text-sky-400" />;
    }
  };

  const getThreatBadge = (level) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-rose-950/70 text-rose-300 border-rose-800/80 animate-pulse';
      case 'HIGH':
        return 'bg-amber-950/70 text-amber-300 border-amber-800/80';
      case 'ELEVATED':
        return 'bg-yellow-950/60 text-yellow-300 border-yellow-800/60';
      default:
        return 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60';
    }
  };

  const handleCreateAsset = async (e) => {
    e.preventDefault();
    if (!newAsset.name || !newAsset.country_iso) return;
    setIsSubmitting(true);
    try {
      await api.createAsset({
        ...newAsset,
        latitude: parseFloat(newAsset.latitude),
        longitude: parseFloat(newAsset.longitude),
        buffer_radius_km: parseFloat(newAsset.buffer_radius_km),
      });
      setShowAddForm(false);
      setNewAsset({
        name: '',
        asset_type: 'FACILITY',
        country_iso: 'TWN',
        latitude: 25.033,
        longitude: 121.565,
        buffer_radius_km: 200,
        criticality: 'TIER_1_MISSION_CRITICAL',
        description: '',
      });
      if (onRefreshAssets) onRefreshAssets();
    } catch (err) {
      console.error('Failed to create corporate asset:', err);
      alert(err.message || 'Error creating asset');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteAsset = async (id, e) => {
    e.stopPropagation();
    if (!confirm('Remove this asset from active geofence monitoring?')) return;
    try {
      await api.deleteAsset(id);
      if (onRefreshAssets) onRefreshAssets();
    } catch (err) {
      console.error('Failed to delete asset:', err);
    }
  };

  const criticalCount = assets.filter((a) => a.threat_level === 'CRITICAL').length;
  const highCount = assets.filter((a) => a.threat_level === 'HIGH').length;

  const containerClasses = isInline
    ? 'bg-[#111C2D] rounded-xl border border-slate-800/80 shadow-sm overflow-hidden flex flex-col'
    : 'fixed inset-y-0 right-0 z-50 w-full max-w-lg bg-[#0D1422]/95 backdrop-blur-xl border-l border-slate-800/80 shadow-2xl flex flex-col animate-slideLeft font-sans';

  return (
    <div className={containerClasses}>
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-800 bg-[#0D1422] flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono">
              Corporate Geofence Portfolio
            </h2>
            <p className="text-[11px] text-slate-400 font-mono">
              Proximity Threat Monitoring &bull; {assets.length} Monitored Facilities
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-semibold bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 border border-sky-500/30 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Pin Facility</span>
          </button>
          {!isInline && onClose && (
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-850 border border-slate-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* KPI Sub-Bar */}
      <div className="grid grid-cols-3 gap-3 px-5 py-3 border-b border-slate-800/80 bg-[#080D17]/50 text-center font-mono">
        <div className="p-2.5 rounded-lg bg-[#111C2D] border border-slate-800/80">
          <div className="text-[10px] text-slate-400 uppercase">Monitored</div>
          <div className="text-lg font-bold text-slate-100">{assets.length}</div>
        </div>
        <div className="p-2.5 rounded-lg bg-[#111C2D] border border-slate-800/80">
          <div className="text-[10px] text-rose-400 uppercase">Critical Buffer</div>
          <div className="text-lg font-bold text-rose-400">{criticalCount}</div>
        </div>
        <div className="p-2.5 rounded-lg bg-[#111C2D] border border-slate-800/80">
          <div className="text-[10px] text-amber-400 uppercase">High Warning</div>
          <div className="text-lg font-bold text-amber-400">{highCount}</div>
        </div>
      </div>

      {/* Add Asset Form Overlay */}
      {showAddForm && (
        <form onSubmit={handleCreateAsset} className="p-5 border-b border-slate-800 bg-[#080D17] space-y-3.5 animate-fadeIn">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-sky-400 uppercase">
              Register New Corporate Facility
            </span>
            <button type="button" onClick={() => setShowAddForm(false)} className="text-slate-500 hover:text-slate-300">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="text-[10px] text-slate-400 font-mono block mb-1">Asset Name</label>
              <input
                type="text"
                required
                placeholder="e.g. TSMC Fab 18"
                value={newAsset.name}
                onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
                className="w-full px-2.5 py-1.5 rounded-lg bg-[#111C2D] border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 font-sans"
              />
            </div>
            <div>
              <label className="text-[10px] text-slate-400 font-mono block mb-1">Facility Type</label>
              <select
                value={newAsset.asset_type}
                onChange={(e) => setNewAsset({ ...newAsset, asset_type: e.target.value })}
                className="w-full px-2.5 py-1.5 rounded-lg bg-[#111C2D] border border-slate-700 text-slate-100 focus:outline-none focus:border-sky-500 font-mono"
              >
                <option value="FACILITY">Manufacturing Facility</option>
                <option value="DATA_CENTER">Data Center / Cloud</option>
                <option value="PORT">Maritime Terminal / Port</option>
                <option value="SUPPLY_DEPOT">Logistics Warehouse</option>
                <option value="MARITIME_VESSEL">Maritime Vessel / Tanker</option>
              </select>
            </div>
            <div>
              <label className="text-[10px] text-slate-400 font-mono block mb-1">Latitude</label>
              <input
                type="number"
                step="0.001"
                required
                value={newAsset.latitude}
                onChange={(e) => setNewAsset({ ...newAsset, latitude: e.target.value })}
                className="w-full px-2.5 py-1.5 rounded-lg bg-[#111C2D] border border-slate-700 text-slate-100 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-slate-400 font-mono block mb-1">Longitude</label>
              <input
                type="number"
                step="0.001"
                required
                value={newAsset.longitude}
                onChange={(e) => setNewAsset({ ...newAsset, longitude: e.target.value })}
                className="w-full px-2.5 py-1.5 rounded-lg bg-[#111C2D] border border-slate-700 text-slate-100 font-mono"
              />
            </div>
            <div>
              <label className="text-[10px] text-slate-400 font-mono block mb-1">Country ISO</label>
              <input
                type="text"
                required
                maxLength={3}
                placeholder="TWN"
                value={newAsset.country_iso}
                onChange={(e) => setNewAsset({ ...newAsset, country_iso: e.target.value.toUpperCase() })}
                className="w-full px-2.5 py-1.5 rounded-lg bg-[#111C2D] border border-slate-700 text-slate-100 font-mono uppercase"
              />
            </div>
            <div>
              <label className="text-[10px] text-slate-400 font-mono block mb-1">Geofence Radius (km)</label>
              <input
                type="number"
                min="10"
                max="1000"
                value={newAsset.buffer_radius_km}
                onChange={(e) => setNewAsset({ ...newAsset, buffer_radius_km: e.target.value })}
                className="w-full px-2.5 py-1.5 rounded-lg bg-[#111C2D] border border-slate-700 text-slate-100 font-mono"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-mono text-xs font-semibold shadow-md transition-colors disabled:opacity-50"
          >
            {isSubmitting ? 'Registering Facility...' : 'Confirm Geofence Activation'}
          </button>
        </form>
      )}

      {/* Asset Cards List */}
      <div className={`p-4 space-y-3 ${isInline ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 space-y-0' : 'flex-1 overflow-y-auto'}`}>
        {assets.length === 0 ? (
          <div className="text-center py-16 text-slate-400 font-mono text-xs col-span-full">
            No corporate assets currently registered. Click "+ Pin Facility" to begin geofence tracking.
          </div>
        ) : (
          assets.map((asset) => (
            <div
              key={asset.asset_id}
              onClick={() => onSelectAsset && onSelectAsset(asset)}
              className="p-4 rounded-xl bg-[#0D1422] border border-slate-800 hover:border-sky-500/40 hover:bg-[#111C2D] transition-all cursor-pointer group shadow-sm flex flex-col justify-between space-y-3"
            >
              {/* Top row */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-slate-850 border border-slate-800 text-sky-400">
                    {getAssetIcon(asset.asset_type)}
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-slate-100 group-hover:text-sky-300 transition-colors">
                      {asset.name}
                    </h3>
                    <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
                      <span>{asset.country_name || asset.country_iso}</span>
                      <span>&bull;</span>
                      <span>Buffer: {asset.buffer_radius_km} km</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-1.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getThreatBadge(asset.threat_level)}`}>
                    {asset.threat_level}
                  </span>
                  <button
                    onClick={(e) => handleDeleteAsset(asset.asset_id, e)}
                    className="p-1 text-slate-500 hover:text-rose-400 transition-colors opacity-0 group-hover:opacity-100"
                    title="Remove asset"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Threat Gauge */}
              <div className="space-y-1 font-mono">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-slate-400">Proximity Threat Index:</span>
                  <span className={`font-bold ${asset.threat_score > 60 ? 'text-rose-400' : asset.threat_score > 30 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {Number(asset.threat_score).toFixed(1)} / 100
                  </span>
                </div>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden border border-slate-800">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      asset.threat_score > 60 ? 'bg-rose-500' : asset.threat_score > 30 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, asset.threat_score)}%` }}
                  />
                </div>
              </div>

              {/* Directive snippet */}
              <div className="p-2.5 rounded-lg bg-slate-850/80 border border-slate-800 text-[11px] text-slate-300 leading-snug">
                <span className="text-sky-400 font-mono text-[10px] font-bold block mb-0.5">SOP DIRECTIVE:</span>
                {asset.prescriptive_directive || 'Active geofence monitoring ongoing; no evacuation trigger.'}
              </div>

              {/* Footer */}
              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs font-mono">
                <span className="text-[10px] text-slate-400">
                  Incidents in Range: <strong className={asset.active_breaches_count > 0 ? 'text-rose-400' : 'text-slate-400'}>{asset.active_breaches_count || 0}</strong>
                </span>

                {onOpenPlaybook && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onOpenPlaybook(asset);
                    }}
                    className="flex items-center gap-1 text-sky-400 hover:text-sky-300 text-[11px] font-bold"
                  >
                    <span>Playbook</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
