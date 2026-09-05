import React from 'react';
import {
  LayoutGrid, Search, History, Eye, FileSpreadsheet, BarChart3,
  FileCheck2, Settings, ShieldCheck, Cpu, Lock, User
} from 'lucide-react';

interface SidebarProps {
  activeNav: string;
  onSelectNav: (nav: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeNav, onSelectNav }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutGrid },
    { id: 'investigations', label: 'Investigations', icon: Search },
    { id: 'history', label: 'History', icon: History },
    { id: 'watchlist', label: 'Watchlist', icon: Eye },
    { id: 'templates', label: 'Templates', icon: FileSpreadsheet },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'audit', label: 'Audit Log', icon: FileCheck2 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-56 bg-[#060a12] border-r border-slate-800/80 flex flex-col justify-between h-full shrink-0 select-none">
      {/* Navigation Links */}
      <div className="p-3 space-y-1">
        <div className="px-3 py-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
          Workbench Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeNav === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectNav(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500/20 to-blue-600/20 text-cyan-300 border border-cyan-500/40 shadow-lg shadow-cyan-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* System Status & Officer Card */}
      <div className="p-3 space-y-3 border-t border-slate-800/80 bg-slate-950/60">
        {/* System Status Widget */}
        <div className="p-3.5 rounded-xl bg-[#0a1120] border border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-300">System Status</span>
            <div className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[10px] font-medium text-emerald-400">Operational</span>
            </div>
          </div>

          {/* Animated Radar Visual */}
          <div className="py-2 flex items-center justify-center">
            <div className="relative w-16 h-16 rounded-full border border-cyan-500/30 bg-cyan-950/20 flex items-center justify-center shadow-inner">
              <div className="absolute inset-0 rounded-full border border-cyan-400/20 animate-ping" />
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-600/30 to-blue-600/30 flex items-center justify-center border border-cyan-400/40">
                <ShieldCheck className="w-5 h-5 text-cyan-300" />
              </div>
            </div>
          </div>

          <div className="space-y-1 text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-800/60">
            <div className="flex justify-between">
              <span>Model Version</span>
              <span className="text-cyan-300">v1.4.2</span>
            </div>
            <div className="flex justify-between">
              <span>DB Sync</span>
              <span className="text-slate-300">Offline</span>
            </div>
            <div className="flex justify-between">
              <span>Last Sync</span>
              <span className="text-slate-500">—</span>
            </div>
          </div>
        </div>

        {/* Officer Badge */}
        <div className="flex items-center space-x-2.5 p-2 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="relative">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-slate-700 to-slate-600 flex items-center justify-center text-white border border-slate-600">
              <User className="w-4 h-4" />
            </div>
            <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-500 border-2 border-slate-950" />
          </div>
          <div className="overflow-hidden">
            <span className="text-[10px] text-slate-400 font-medium block uppercase tracking-wider">Officer</span>
            <span className="text-xs font-bold text-slate-200 truncate block">Inspector Admin</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
