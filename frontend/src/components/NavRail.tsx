import React from 'react';
import {
  ScanLine, FolderOpen, Network, Database, FileText, Sliders, ShieldCheck
} from 'lucide-react';

interface NavRailProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
}

export const NavRail: React.FC<NavRailProps> = ({ activeTab, onSelectTab }) => {
  const navItems = [
    { id: 'verify', label: 'Verify', icon: ScanLine },
    { id: 'cases', label: 'Cases', icon: FolderOpen },
    { id: 'graph', label: 'Graph', icon: Network },
    { id: 'library', label: 'Library', icon: Database },
    { id: 'audit', label: 'Audit', icon: FileText },
  ];

  return (
    <>
      {/* DESKTOP NAV RAIL (72px Left Sidebar) */}
      <aside className="hidden md:flex fixed left-0 top-0 h-full w-[72px] bg-white border-r border-slate-200 z-50 flex-col justify-between items-center py-5 shadow-[0_1px_3px_rgba(0,0,0,0.02)] select-none">
        <div className="flex flex-col items-center w-full">
          {/* Shield Logo Icon with Jumio Green Spark */}
          <a className="relative w-11 h-11 rounded-xl bg-slate-950 flex items-center justify-center mb-8 shadow-sm hover:opacity-95 transition-all group" href="#">
            <ShieldCheck className="w-6 h-6 text-white" />
            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-[#00d084] rounded-full border-2 border-white" />
          </a>

          {/* Primary Nav Items */}
          <nav className="flex flex-col items-center gap-1.5 w-full px-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`flex flex-col items-center justify-center w-full py-2.5 rounded-xl transition-all cursor-pointer transform active:scale-95 ${
                    isActive
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                  title={item.label}
                >
                  <Icon className="w-5 h-5" />
                  <span className={`text-[10px] tracking-tight mt-0.5 ${isActive ? 'font-semibold' : 'font-medium'}`}>
                    {item.label}
                  </span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom Profile & Settings */}
        <div className="flex flex-col items-center gap-4 w-full px-2">
          <button
            className="flex items-center justify-center w-10 h-10 rounded-xl text-slate-500 hover:bg-slate-100 hover:text-slate-900 transition-all cursor-pointer"
            title="System Settings"
          >
            <Sliders className="w-5 h-5" />
          </button>

          <div
            className="w-9 h-9 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-semibold text-slate-700 text-xs cursor-pointer hover:ring-2 hover:ring-slate-300 transition-all"
            title="Agent Profile: Senior Adjudicator STN-09"
          >
            ST
          </div>
        </div>
      </aside>

      {/* MOBILE BOTTOM NAVIGATION BAR (PhonePe / Paytm / Lenskart Style) */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-white/95 backdrop-blur-lg border-t border-slate-200 z-50 flex items-center justify-around px-2 shadow-[0_-4px_20px_rgba(0,0,0,0.05)] select-none">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all cursor-pointer transform active:scale-90 ${
                isActive
                  ? 'text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-slate-700'
              }`}
            >
              <div className={`p-1 rounded-full transition-all ${isActive ? 'bg-[#00d084]/20 text-[#00d084]' : ''}`}>
                <Icon className="w-5 h-5" />
              </div>
              <span className={`text-[10px] tracking-tight mt-0.5 ${isActive ? 'font-bold text-slate-950' : 'font-medium'}`}>
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>
    </>
  );
};
