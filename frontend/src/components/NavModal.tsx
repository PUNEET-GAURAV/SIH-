import React from 'react';
import { X, FolderOpen, Network, Database, FileText, Sliders, ShieldCheck, CheckCircle2, Clock, Cpu, FileCheck2 } from 'lucide-react';

interface NavModalProps {
  activeTab: string | null;
  onClose: () => void;
}

export const NavModal: React.FC<NavModalProps> = ({ activeTab, onClose }) => {
  if (!activeTab || activeTab === 'verify') return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
      <div className="bg-white border border-slate-200 rounded-3xl shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col max-h-[85vh] transition-all">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/80">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-slate-950 text-white flex items-center justify-center shadow-sm">
              {activeTab === 'cases' && <FolderOpen className="w-5 h-5 text-[#00d084]" />}
              {activeTab === 'graph' && <Network className="w-5 h-5 text-[#00d084]" />}
              {activeTab === 'library' && <Database className="w-5 h-5 text-[#00d084]" />}
              {activeTab === 'audit' && <FileText className="w-5 h-5 text-[#00d084]" />}
              {activeTab === 'settings' && <Sliders className="w-5 h-5 text-[#00d084]" />}
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-950 capitalize">
                {activeTab === 'cases' && 'Adjudication Case Queue'}
                {activeTab === 'graph' && 'Identity Risk Network Graph'}
                {activeTab === 'library' && 'Passport & ID Specimen Repository'}
                {activeTab === 'audit' && 'Cryptographic Audit Trail'}
                {activeTab === 'settings' && 'System Configuration & Rule Engine'}
              </h3>
              <p className="text-xs text-slate-500 font-medium">DocShield Enterprise Security • STN-09 Active Session</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Content Body */}
        <div className="p-6 overflow-y-auto space-y-4 text-xs">
          {activeTab === 'cases' && (
            <div className="space-y-3">
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-2xl flex items-center justify-between text-amber-900">
                <span className="font-semibold">3 High Priority Cases Awaiting Senior Adjudication</span>
                <span className="px-2 py-0.5 rounded-full bg-amber-200 text-[10px] font-bold">Action Required</span>
              </div>
              <div className="divide-y divide-slate-100 border border-slate-200 rounded-2xl overflow-hidden bg-white">
                {[
                  { id: 'SCN-9941', type: 'Passport TD3', risk: 'High Concern', date: '2 mins ago', status: 'Pending Review' },
                  { id: 'SCN-9940', type: 'ID Card TD1', risk: 'Low Concern', date: '14 mins ago', status: 'Auto-Cleared' },
                  { id: 'SCN-9939', type: 'Passport TD3', risk: 'Medium Concern', date: '32 mins ago', status: 'Secondary Check' },
                ].map((item) => (
                  <div key={item.id} className="p-3 flex items-center justify-between hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-3">
                      <FileCheck2 className="w-5 h-5 text-slate-400" />
                      <div>
                        <div className="font-bold text-slate-900">{item.id} — {item.type}</div>
                        <div className="text-[10px] text-slate-400">{item.date} • Officer STN-09</div>
                      </div>
                    </div>
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                      item.risk === 'High Concern' ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'
                    }`}>
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'graph' && (
            <div className="space-y-4">
              <div className="p-4 bg-slate-950 text-white rounded-2xl flex flex-col gap-2">
                <span className="text-[10px] font-bold uppercase text-[#00d084]">Graph Telemetry</span>
                <div className="text-sm font-bold">Multi-Document Specimen Correlation</div>
                <p className="text-slate-300 text-xs leading-relaxed">
                  No cross-case copy-move cluster matches found for specimen PA8849201 across global watchlist repositories.
                </p>
              </div>
              <div className="h-44 bg-slate-50 border border-slate-200 rounded-2xl flex items-center justify-center text-slate-400 font-mono">
                [ Interactive Node Topology Graph: 0 Suspicious Clusters Connected ]
              </div>
            </div>
          )}

          {activeTab === 'library' && (
            <div className="grid grid-cols-2 gap-3">
              {[
                { country: 'Arcasia Passport', code: 'ARC-P3', templates: '14 Security Patterns' },
                { country: 'Estonia e-ID', code: 'EST-TD1', templates: '22 Security Patterns' },
                { country: 'Germany Reisepass', code: 'DEU-P2', templates: '30 Security Patterns' },
                { country: 'Singapore Passport', code: 'SGP-P3', templates: '18 Security Patterns' },
              ].map((lib) => (
                <div key={lib.code} className="p-3.5 border border-slate-200 rounded-2xl hover:border-slate-400 transition-colors bg-white">
                  <div className="font-bold text-slate-900">{lib.country}</div>
                  <div className="text-[11px] font-mono text-slate-500">{lib.code}</div>
                  <div className="text-[10px] text-emerald-600 font-semibold mt-2">{lib.templates}</div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'audit' && (
            <div className="space-y-3 font-mono">
              <div className="p-3 bg-slate-900 text-slate-200 rounded-2xl text-[11px] space-y-1">
                <div>[04/SEP/2026:16:20:01] IMMUTABLE HASH LOG INITIALIZED</div>
                <div>[04/SEP/2026:16:22:15] SESSION SCN-9941 INSPECTION COMPLETED</div>
                <div>[04/SEP/2026:16:23:40] CRYPTOGRAPHIC SIGNATURE: SHA256-e9b41a8820...</div>
              </div>
              <div className="flex items-center gap-2 text-slate-500 text-xs">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>Tamper-Proof Ledger Signed by Local Security Module</span>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 border border-slate-200 rounded-2xl">
                <div>
                  <div className="font-bold text-slate-900">MOCK_MODE Execution</div>
                  <div className="text-slate-500 text-[11px]">Enforce strict deterministic offline inspection</div>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px]">ACTIVE (Deterministic)</span>
              </div>
              <div className="flex items-center justify-between p-3 border border-slate-200 rounded-2xl">
                <div>
                  <div className="font-bold text-slate-900">Air-Gapped Optical Calibration</div>
                  <div className="text-slate-500 text-[11px]">600 DPI High-Res Local Ingestion</div>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-bold text-[10px]">ENABLED</span>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-950 text-white text-xs font-semibold rounded-xl hover:bg-slate-800 transition-colors cursor-pointer"
          >
            Close Window
          </button>
        </div>
      </div>
    </div>
  );
};
