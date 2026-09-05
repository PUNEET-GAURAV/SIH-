import React, { useState } from 'react';
import {
  ShieldCheck, LayoutGrid, Fingerprint, UserCheck, Sparkles,
  CheckCircle2, AlertTriangle, Activity, CheckSquare, Layers
} from 'lucide-react';
import { ScreeningAssessmentData, DemoScenario } from '../types';
import { OverviewTab } from './EvidenceTabs/OverviewTab';
import { OcrTab } from './EvidenceTabs/OcrTab';
import { MrzTab } from './EvidenceTabs/MrzTab';
import { StructureTab } from './EvidenceTabs/StructureTab';
import { ForensicsTab } from './EvidenceTabs/ForensicsTab';
import { FaceTab } from './EvidenceTabs/FaceTab';
import { AuditTab } from './EvidenceTabs/AuditTab';

interface AnalysisCenterColProps {
  assessment?: ScreeningAssessmentData;
  activeTab: string;
  onTabChange: (tab: string) => void;
  sessionData: any;
  scenario: DemoScenario;
  auditTrail: any[];
  onVerifyAudit: () => Promise<any>;
}

export const AnalysisCenterCol: React.FC<AnalysisCenterColProps> = ({
  assessment,
  activeTab,
  onTabChange,
  sessionData,
  scenario,
  auditTrail,
  onVerifyAudit,
}) => {
  const doc = sessionData?.documents?.[0];

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'ocr', label: 'OCR & Data' },
    { id: 'mrz', label: 'MRZ / Barcode' },
    { id: 'structure', label: 'Structure' },
    { id: 'forensics', label: 'Forensics' },
    { id: 'face', label: 'Face & PAD' },
    { id: 'cross', label: 'Cross Checks' },
    { id: 'audit', label: `Audit Log (${auditTrail.length})` },
  ];

  return (
    <div className="flex flex-col space-y-4 h-full overflow-y-auto select-none pr-1">
      {/* Evidence Tabs Header Bar */}
      <div className="h-12 bg-[#090e1a]/95 border border-slate-800/80 rounded-2xl flex items-center justify-between px-3 shrink-0 shadow-lg">
        <div className="flex items-center space-x-1 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition cursor-pointer ${
                activeTab === tab.id
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm shadow-cyan-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <button className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-blue-600/30 to-cyan-600/30 hover:from-blue-600/40 hover:to-cyan-600/40 text-cyan-300 border border-cyan-500/40 text-xs font-semibold shadow-sm cursor-pointer">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Analysis Pipeline</span>
        </button>
      </div>

      {/* If Overview tab is active, show the rich 4-Section Dashboard layout from the reference image */}
      {activeTab === 'overview' ? (
        <div className="space-y-4">
          {/* SECTION 1: 4 DIMENSION CARDS ROW */}
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
            {/* Card 1: Document Consistency */}
            <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-3.5 space-y-2.5 shadow-xl hover:border-slate-700 transition">
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-xl bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-mono">
                  EXCELLENT
                </span>
              </div>
              <div>
                <span className="text-[11px] font-bold text-slate-300 block">Document Consistency</span>
                <div className="flex items-baseline space-x-1 mt-0.5">
                  <span className="text-xl font-extrabold text-white font-mono">98</span>
                  <span className="text-xs text-slate-500 font-mono">/100</span>
                </div>
              </div>
              <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                <div className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full w-[98%]" />
              </div>
              <span className="text-[10px] text-slate-400 block truncate">All key fields consistent</span>
            </div>

            {/* Card 2: Structural Conformity */}
            <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-3.5 space-y-2.5 shadow-xl hover:border-slate-700 transition">
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                  <LayoutGrid className="w-4 h-4" />
                </div>
                <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-mono">
                  EXCELLENT
                </span>
              </div>
              <div>
                <span className="text-[11px] font-bold text-slate-300 block">Structural Conformity</span>
                <div className="flex items-baseline space-x-1 mt-0.5">
                  <span className="text-xl font-extrabold text-white font-mono">96</span>
                  <span className="text-xs text-slate-500 font-mono">/100</span>
                </div>
              </div>
              <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                <div className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full w-[96%]" />
              </div>
              <span className="text-[10px] text-slate-400 block truncate">Template & layout verified</span>
            </div>

            {/* Card 3: Forensic Integrity */}
            <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-3.5 space-y-2.5 shadow-xl hover:border-slate-700 transition">
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  <Fingerprint className="w-4 h-4" />
                </div>
                <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono">
                  GOOD
                </span>
              </div>
              <div>
                <span className="text-[11px] font-bold text-slate-300 block">Forensic Integrity</span>
                <div className="flex items-baseline space-x-1 mt-0.5">
                  <span className="text-xl font-extrabold text-white font-mono">93</span>
                  <span className="text-xs text-slate-500 font-mono">/100</span>
                </div>
              </div>
              <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                <div className="bg-gradient-to-r from-amber-500 to-emerald-400 h-full w-[93%]" />
              </div>
              <span className="text-[10px] text-slate-400 block truncate">Minor artifacts detected</span>
            </div>

            {/* Card 4: Identity & PAD */}
            <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-3.5 space-y-2.5 shadow-xl hover:border-slate-700 transition">
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  <UserCheck className="w-4 h-4" />
                </div>
                <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40 font-mono">
                  GOOD
                </span>
              </div>
              <div>
                <span className="text-[11px] font-bold text-slate-300 block">Identity & PAD</span>
                <div className="flex items-baseline space-x-1 mt-0.5">
                  <span className="text-xl font-extrabold text-white font-mono">89</span>
                  <span className="text-xs text-slate-500 font-mono">/100</span>
                </div>
              </div>
              <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                <div className="bg-gradient-to-r from-purple-500 to-cyan-400 h-full w-[89%]" />
              </div>
              <span className="text-[10px] text-slate-400 block truncate">Live face match strong</span>
            </div>
          </div>

          {/* SECTION 2: RISK SCORE GAUGE & BREAKDOWN CHART ROW */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
            {/* Left Gauge Widget */}
            <div className="md:col-span-4 bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-4 flex flex-col justify-between items-center text-center shadow-xl relative overflow-hidden">
              <div className="w-full flex justify-between items-center text-xs font-bold text-slate-300 pb-2 border-b border-slate-800/60">
                <span>Risk Score (Fusion Engine)</span>
              </div>

              {/* Semi-circular Arc Gauge Visual */}
              <div className="relative my-3 flex items-center justify-center">
                <svg className="w-36 h-20" viewBox="0 0 100 50">
                  <path
                    d="M 10 50 A 40 40 0 0 1 90 50"
                    fill="none"
                    stroke="#1e293b"
                    strokeWidth="10"
                    strokeLinecap="round"
                  />
                  <path
                    d="M 10 50 A 40 40 0 0 1 90 50"
                    fill="none"
                    stroke="url(#emeraldGradient)"
                    strokeWidth="10"
                    strokeLinecap="round"
                    strokeDasharray="126"
                    strokeDashoffset="100"
                  />
                  <defs>
                    <linearGradient id="emeraldGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#10b981" />
                      <stop offset="100%" stopColor="#06b6d4" />
                    </linearGradient>
                  </defs>
                </svg>

                <div className="absolute top-7 flex flex-col items-center">
                  <span className="text-3xl font-black font-mono text-white">18</span>
                  <span className="text-[10px] text-slate-500 font-mono">/100</span>
                </div>
              </div>

              <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold animate-pulse shadow-md shadow-emerald-500/10">
                LOW RISK
              </div>
            </div>

            {/* Right Trend Chart & Breakdown */}
            <div className="md:col-span-8 bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-4 flex flex-col justify-between shadow-xl">
              <div className="flex justify-between items-center text-xs font-bold text-slate-300 pb-2 border-b border-slate-800/60">
                <span>Risk Breakdown</span>
                <span className="text-[10px] text-slate-500 font-mono">Lower score is better</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-2">
                {/* SVG Score Trend Graph */}
                <div className="flex flex-col justify-between">
                  <span className="text-[10px] font-bold text-slate-400 mb-1">Score Trend</span>
                  <svg className="w-full h-20" viewBox="0 0 200 60">
                    <path
                      d="M 0 40 Q 30 50, 60 30 T 120 20 T 180 40 L 200 35"
                      fill="none"
                      stroke="#06b6d4"
                      strokeWidth="2.5"
                    />
                    <circle cx="60" cy="30" r="3" fill="#10b981" />
                    <circle cx="120" cy="20" r="3" fill="#06b6d4" />
                    <circle cx="180" cy="40" r="3" fill="#3b82f6" />
                  </svg>
                  <div className="flex justify-between text-[9px] text-slate-500 font-mono pt-1">
                    <span>10:40</span>
                    <span>10:50</span>
                    <span>11:00</span>
                    <span>11:10</span>
                    <span>11:20</span>
                    <span>11:30</span>
                    <span>11:40</span>
                  </div>
                </div>

                {/* Breakdown Metrics Table */}
                <div className="space-y-1.5 text-[11px] font-mono justify-center flex flex-col">
                  <div className="flex justify-between items-center">
                    <span className="flex items-center space-x-1.5 text-slate-400">
                      <span className="w-2 h-2 rounded-full bg-blue-400" />
                      <span>Rule-Based Checks</span>
                    </span>
                    <span className="text-slate-300 font-bold">0</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="flex items-center space-x-1.5 text-slate-400">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      <span>Structure & Template</span>
                    </span>
                    <span className="text-emerald-400 font-bold">-2</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="flex items-center space-x-1.5 text-slate-400">
                      <span className="w-2 h-2 rounded-full bg-amber-400" />
                      <span>Forensics</span>
                    </span>
                    <span className="text-amber-400 font-bold">12</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="flex items-center space-x-1.5 text-slate-400">
                      <span className="w-2 h-2 rounded-full bg-purple-400" />
                      <span>Face & PAD</span>
                    </span>
                    <span className="text-purple-400 font-bold">8</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="flex items-center space-x-1.5 text-slate-400">
                      <span className="w-2 h-2 rounded-full bg-cyan-400" />
                      <span>Cross-Validation</span>
                    </span>
                    <span className="text-slate-300 font-bold">0</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* SECTION 3: KEY FINDINGS CHIPS ROW */}
          <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-3.5 space-y-2.5 shadow-xl">
            <span className="text-xs font-bold text-slate-200 tracking-wider uppercase block">Key Findings</span>
            <div className="flex flex-wrap gap-2">
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>MRZ / Data Validation: All checks passed</span>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Template Match: Strong alignment</span>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                <span>Forensic Signals: Minor recompression</span>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Face Match: Similarity 0.87</span>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Duplicate Check: No matches found</span>
              </div>
            </div>
          </div>

          {/* SECTION 4: EVIDENCE HEATMAP (FORENSICS) */}
          <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-4 space-y-3 shadow-xl">
            <span className="text-xs font-bold text-slate-200 tracking-wider uppercase block">Evidence Heatmap (Forensics)</span>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
              {/* Heatmap Image Box */}
              <div className="md:col-span-6 relative rounded-xl overflow-hidden border border-slate-800 bg-slate-950 min-h-[160px] flex items-center justify-center">
                <img
                  src={doc?.file_path || 'https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=800&q=80'}
                  alt="Heatmap Preview"
                  className="max-h-[160px] w-auto object-contain brightness-90"
                />
                <div className="absolute inset-0 bg-gradient-to-tr from-purple-600/40 via-yellow-500/30 to-rose-600/50 mix-blend-color-dodge pointer-events-none" />
                <div className="absolute bottom-2 right-2 w-12 h-12 rounded-full bg-rose-500/60 blur-md pointer-events-none" />
              </div>

              {/* Heatmap Layer Checklist & Percentages */}
              <div className="md:col-span-6 space-y-2.5">
                <span className="text-[11px] font-bold text-slate-300 block">Heatmap Layers</span>

                <div className="space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center space-x-2 text-slate-300 cursor-pointer">
                      <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0" />
                      <span>Recompression</span>
                    </label>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                        <div className="bg-purple-500 h-full w-[83%]" />
                      </div>
                      <span className="font-mono text-[11px] font-bold text-purple-400">83%</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <label className="flex items-center space-x-2 text-slate-300 cursor-pointer">
                      <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0" />
                      <span>Copy-Move</span>
                    </label>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                        <div className="bg-cyan-400 h-full w-[12%]" />
                      </div>
                      <span className="font-mono text-[11px] font-bold text-cyan-400">12%</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <label className="flex items-center space-x-2 text-slate-300 cursor-pointer">
                      <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0" />
                      <span>Noise Residual</span>
                    </label>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                        <div className="bg-blue-400 h-full w-[18%]" />
                      </div>
                      <span className="font-mono text-[11px] font-bold text-blue-400">18%</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <label className="flex items-center space-x-2 text-slate-300 cursor-pointer">
                      <input type="checkbox" defaultChecked className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0" />
                      <span>Font Anomaly</span>
                    </label>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                        <div className="bg-amber-400 h-full w-[9%]" />
                      </div>
                      <span className="font-mono text-[11px] font-bold text-amber-400">9%</span>
                    </div>
                  </div>
                </div>

                {/* Color Legend Bar */}
                <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                  <span>Low</span>
                  <div className="flex-1 mx-3 h-1.5 rounded-full bg-gradient-to-r from-blue-500 via-yellow-400 to-rose-500" />
                  <span>High</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* If other tab is selected, render individual tab body */
        <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-5 shadow-xl min-h-[500px]">
          {activeTab === 'ocr' && <OcrTab fields={doc?.ocr_fields} />}
          {activeTab === 'mrz' && <MrzTab mrzData={doc?.mrz_result} />}
          {activeTab === 'structure' && (
            <StructureTab
              documentType={doc?.document_type}
              classificationConfidence={doc?.classification_confidence}
              templateResult={doc?.template_result}
            />
          )}
          {activeTab === 'forensics' && <ForensicsTab forensicResults={doc?.forensic_results} />}
          {activeTab === 'face' && <FaceTab faceData={sessionData?.face_verification} />}
          {activeTab === 'cross' && <OverviewTab assessment={assessment} />}
          {activeTab === 'audit' && (
            <AuditTab
              sessionId={sessionData?.id || ''}
              auditTrail={auditTrail}
              onVerifyAudit={onVerifyAudit}
            />
          )}
        </div>
      )}
    </div>
  );
};
