import React from 'react';
import { Lock, ShieldCheck } from 'lucide-react';

interface FooterBarProps {
  sessionId?: string;
}

export const FooterBar: React.FC<FooterBarProps> = ({ sessionId }) => {
  return (
    <footer className="h-8 bg-[#060a12] border-t border-slate-800/80 px-4 flex items-center justify-between text-[10px] text-slate-400 font-mono select-none shrink-0">
      <div className="flex items-center space-x-1.5">
        <Lock className="w-3 h-3 text-cyan-400" />
        <span>End-to-End Encryption <strong className="text-slate-300">AES-256</strong></span>
      </div>

      <div className="flex items-center space-x-1">
        <span>Session ID:</span>
        <span className="text-cyan-300 font-bold">{sessionId || 'DS-2025-0519-114233'}</span>
      </div>

      <div className="flex items-center space-x-1.5 text-slate-400">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span>All actions are audit logged and tamper-evident</span>
      </div>
    </footer>
  );
};
