import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Send,
  Eye,
  CheckCircle2,
  XCircle,
  MessageSquare,
  RefreshCw,
} from 'lucide-react';
import { api } from '../api/client';

export default function AlertsView({
  alerts = [],
  onInspectCountry,
  onTriggerIngest,
  isIngesting,
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [webhookStatus, setWebhookStatus] = useState({
    webhooks_enabled: false,
    discord_configured: false,
    telegram_configured: false,
  });

  useEffect(() => {
    api.getWebhookStatus()
      .then((data) => {
        if (data) setWebhookStatus(data);
      })
      .catch((err) => console.error('Error fetching webhook status:', err));
  }, []);

  const discordActive = webhookStatus.webhooks_enabled && webhookStatus.discord_configured;
  const telegramActive = webhookStatus.webhooks_enabled && webhookStatus.telegram_configured;
  const anyWebhookActive = discordActive || telegramActive;

  const filteredAlerts = alerts.filter((a) => {
    const cName = (a.country_iso || a.country || '').toLowerCase();
    return !searchTerm || cName.includes(searchTerm.toLowerCase());
  });

  return (
    <div className="space-y-6">
      {/* Alerts Operations Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#111C2D] p-5 rounded-xl border border-slate-800/80 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ShieldAlert className="w-5 h-5 text-rose-500" />
            <h2 className="text-base font-bold font-mono text-slate-100 uppercase tracking-wider">
              Critical Risk Threshold Alerts Log (R &gt; 75)
            </h2>
          </div>
          <p className="text-xs text-slate-400 font-sans">
            Real-time WebSocket alerts with optional Discord and Telegram webhook notifications
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0D1422] border border-slate-800 text-xs font-mono text-slate-300">
            <span
              className={`w-2 h-2 rounded-full ${
                anyWebhookActive ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'
              }`}
            ></span>
            <span>{anyWebhookActive ? 'Webhooks Active' : 'Webhooks Disabled'}</span>
          </div>

          <button
            onClick={onTriggerIngest}
            disabled={isIngesting}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-500/15 hover:bg-sky-500/25 border border-sky-500/30 text-sky-300 text-xs font-mono font-semibold transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-sky-400 ${isIngesting ? 'animate-spin' : ''}`} />
            <span>{isIngesting ? 'Running Feed...' : 'Run Ingestion'}</span>
          </button>
        </div>
      </div>

      {/* Integration Status Cards (Real Runtime Config) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Discord Card */}
        <div className="bg-[#111C2D] p-4 rounded-xl border border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <div className="font-mono font-bold text-xs text-slate-100">Discord Webhook</div>
              <div className="text-[11px] text-slate-400">
                {discordActive
                  ? 'Configured via DISCORD_WEBHOOK_URL'
                  : 'Set DISCORD_WEBHOOK_URL & WEBHOOKS_ENABLED=true in .env'}
              </div>
            </div>
          </div>
          {discordActive ? (
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 shrink-0">
              <CheckCircle2 className="w-3 h-3" />
              <span>CONFIGURED</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-900 text-slate-400 border border-slate-700 shrink-0">
              <XCircle className="w-3 h-3" />
              <span>NOT CONFIGURED</span>
            </div>
          )}
        </div>

        {/* Telegram Card */}
        <div className="bg-[#111C2D] p-4 rounded-xl border border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
              <Send className="w-5 h-5" />
            </div>
            <div>
              <div className="font-mono font-bold text-xs text-slate-100">Telegram Bot Channel</div>
              <div className="text-[11px] text-slate-400">
                {telegramActive
                  ? 'Configured via TELEGRAM_BOT_TOKEN & TELEGRAM_CHAT_ID'
                  : 'Set TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID & WEBHOOKS_ENABLED=true in .env'}
              </div>
            </div>
          </div>
          {telegramActive ? (
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 shrink-0">
              <CheckCircle2 className="w-3 h-3" />
              <span>CONFIGURED</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-900 text-slate-400 border border-slate-700 shrink-0">
              <XCircle className="w-3 h-3" />
              <span>NOT CONFIGURED</span>
            </div>
          )}
        </div>
      </div>

      {/* Alerts Feed */}
      <div className="bg-[#111C2D] rounded-xl border border-slate-800/80 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
            Broadcast History ({filteredAlerts.length} Critical Dispatches)
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter alerts by country..."
            className="px-3 py-1 bg-[#0D1422] border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-400 font-mono w-52 focus:outline-none focus:ring-1 focus:ring-sky-500/40"
          />
        </div>

        {filteredAlerts.length === 0 ? (
          <div className="py-20 text-center text-slate-400 font-mono text-xs">
            No critical risk alerts recorded. Systems operating within normal bounds.
          </div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {filteredAlerts.map((item, idx) => (
              <div
                key={item.alert_id || idx}
                className="p-4 hover:bg-[#131F31] transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-950 text-rose-400 border border-rose-800/60">
                      CRITICAL THRESHOLD
                    </span>
                    <span className="font-bold text-sm text-slate-100">
                      {item.country_iso || item.country}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      &bull; {new Date(item.sent_at || item.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300">
                    Sovereign risk calculation exceeded critical threshold with composite value of{' '}
                    <strong className="text-rose-400 font-mono">
                      {Number(item.risk_score).toFixed(1)} / 100
                    </strong>.
                  </p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => onInspectCountry(item.country_iso || item.country)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0D1422] hover:bg-slate-800 text-sky-400 border border-slate-750 hover:border-sky-500/40 text-xs font-mono font-semibold transition-colors"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Inspect Country</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
