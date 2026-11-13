import React from 'react';
import {
  Shield,
  LayoutDashboard,
  TrendingUp,
  Newspaper,
  BellRing,
  Building2,
  Compass,
  BookOpen,
  Activity,
  Bot,
  ChevronLeft,
  ChevronRight,
  Radio,
  ExternalLink,
} from 'lucide-react';

export default function Sidebar({
  currentView,
  onSelectView,
  isCollapsed,
  onToggleCollapse,
  alertsCount = 0,
  assetsCount = 0,
  wsConnected = false,
  onOpenCopilot,
}) {
  const navSections = [
    {
      title: 'INTELLIGENCE',
      items: [
        { id: 'dashboard', label: 'Tactical Map', icon: LayoutDashboard, badge: null },
        { id: 'analytics', label: 'Risk Analytics', icon: TrendingUp, badge: null },
        { id: 'news', label: 'OSINT News Wire', icon: Newspaper, badge: null },
        { id: 'alerts', label: 'Live Alerts', icon: BellRing, badge: alertsCount > 0 ? alertsCount : null, badgeColor: 'bg-rose-500 text-white' },
      ],
    },
    {
      title: 'OPERATIONS & DEFENSE',
      items: [
        { id: 'assets', label: 'Corporate Assets', icon: Building2, badge: assetsCount, badgeColor: 'bg-sky-500/20 text-sky-400 border border-sky-500/30' },
        { id: 'simulation', label: 'What-If Sandbox', icon: Compass, badge: null },
        { id: 'playbooks', label: 'Action Playbooks', icon: BookOpen, badge: null },
      ],
    },
    {
      title: 'SYSTEM & SUPPORT',
      items: [
        { id: 'health', label: 'System Health', icon: Activity, badge: null },
      ],
    },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 z-30 h-screen bg-[#0A101D] border-r border-slate-800/80 flex flex-col transition-all duration-300 ease-in-out ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="h-14 px-3 flex items-center justify-between border-b border-slate-800/80">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-500/20 to-indigo-600/30 border border-sky-500/40 flex items-center justify-center text-sky-400 shrink-0 shadow-sm shadow-sky-950/50">
              <Shield className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="font-mono font-bold text-xs tracking-wider text-slate-100 flex items-center gap-1.5">
                <span>GEOSENTINEL</span>
                <span className="text-[9px] px-1 py-0.2 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                  AI
                </span>
              </span>
              <span className="text-[10px] text-slate-400 truncate">Global Threat Intelligence</span>
            </div>
          </div>
        )}

        {isCollapsed && (
          <div className="w-full flex items-center justify-center">
            <div className="w-8 h-8 rounded-lg bg-sky-500/20 border border-sky-500/40 flex items-center justify-center text-sky-400">
              <Shield className="w-4 h-4" />
            </div>
          </div>
        )}

        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-100 hover:bg-slate-800/60 transition-colors"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-5">
        {navSections.map((section, idx) => (
          <div key={idx} className="space-y-1">
            {!isCollapsed && (
              <div className="px-2.5 py-1 text-[10px] font-mono font-semibold tracking-wider text-slate-400 uppercase">
                {section.title}
              </div>
            )}
            {section.items.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectView(item.id)}
                  title={isCollapsed ? item.label : undefined}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-all group ${
                    isActive
                      ? 'bg-sky-500/15 text-sky-300 border border-sky-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850 border border-transparent'
                  } ${isCollapsed ? 'justify-center px-0' : ''}`}
                >
                  <Icon
                    className={`w-4 h-4 shrink-0 transition-colors ${
                      isActive ? 'text-sky-400' : 'text-slate-400 group-hover:text-slate-200'
                    }`}
                  />
                  {!isCollapsed && (
                    <span className="flex-1 text-left truncate">{item.label}</span>
                  )}
                  {!isCollapsed && item.badge !== null && item.badge !== undefined && (
                    <span
                      className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold ${
                        item.badgeColor || 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                  {isCollapsed && item.badge !== null && item.badge !== undefined && (
                    <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-[#0A101D]" />
                  )}
                </button>
              );
            })}
          </div>
        ))}

        {/* AI Copilot Quick Launcher Button */}
        <div className="pt-2">
          <button
            onClick={onOpenCopilot}
            className={`w-full flex items-center gap-2.5 p-2 rounded-lg bg-gradient-to-r from-sky-600/20 to-indigo-600/20 hover:from-sky-600/30 hover:to-indigo-600/30 border border-sky-500/30 text-sky-200 text-xs font-mono transition-all shadow-sm ${
              isCollapsed ? 'justify-center p-2.5' : ''
            }`}
            title="Launch Ask GeoSentinel AI Copilot"
          >
            <Bot className="w-4 h-4 text-sky-400 shrink-0" />
            {!isCollapsed && (
              <div className="flex-1 text-left">
                <div className="font-semibold text-white">Ask Copilot</div>
                <div className="text-[10px] text-sky-300/70">RAG Intelligence</div>
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Telemetry Status Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/60">
        <div className={`flex items-center gap-2 ${isCollapsed ? 'justify-center' : ''}`}>
          <div
            className={`w-2 h-2 rounded-full ${
              wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'
            }`}
          />
          {!isCollapsed && (
            <div className="flex-1 text-[11px] font-mono text-slate-400 flex items-center justify-between">
              <span>{wsConnected ? 'SYSTEM SECURE' : 'STREAM OFFLINE'}</span>
              <span className="text-[10px] text-slate-400 font-sans">v2.4</span>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}

