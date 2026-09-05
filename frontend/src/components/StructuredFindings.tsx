import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, ArrowRight, Check, ChevronRight, Layers } from 'lucide-react';
import { DemoScenario, ScreeningAssessmentData } from '../types';

interface StructuredFindingsProps {
  scenario: DemoScenario;
  assessment?: ScreeningAssessmentData;
}

export const StructuredFindings: React.FC<StructuredFindingsProps> = ({
  scenario,
  assessment,
}) => {
  const [activeFilter, setActiveFilter] = useState<'all' | 'flagged' | 'passed'>('all');
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  const isAltered = scenario === 'altered_dob' || assessment?.concern_level === 'high_concern';

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-4 sm:p-6 flex flex-col gap-4 sm:gap-5 select-none transition-all">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm sm:text-base font-bold text-slate-950 tracking-tight">Structured Verification Findings</span>
          <span className="text-[11px] sm:text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
            4 Engine Modules
          </span>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-full border border-slate-200 text-xs">
          <button
            onClick={() => setActiveFilter('all')}
            className={`px-3 py-1 rounded-full text-[11px] font-semibold transition-all cursor-pointer ${
              activeFilter === 'all' ? 'bg-white text-slate-950 shadow-xs' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            All (4)
          </button>
          <button
            onClick={() => setActiveFilter('flagged')}
            className={`px-3 py-1 rounded-full text-[11px] font-semibold transition-all cursor-pointer ${
              activeFilter === 'flagged' ? 'bg-white text-rose-700 shadow-xs' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Flagged ({isAltered ? 2 : 0})
          </button>
          <button
            onClick={() => setActiveFilter('passed')}
            className={`px-3 py-1 rounded-full text-[11px] font-semibold transition-all cursor-pointer ${
              activeFilter === 'passed' ? 'bg-white text-emerald-700 shadow-xs' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Passed ({isAltered ? 2 : 4})
          </button>
        </div>
      </div>

      {/* 4 Jumio Case Study Style Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Module 01: Document Consistency */}
        <div
          className={`bg-white border rounded-xl p-4 flex flex-col justify-between gap-3 shadow-xs transition-all ${
            isAltered ? 'border-rose-200' : 'border-slate-200'
          }`}
        >
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Module 01</span>
              {isAltered ? (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 text-xs font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                  Discrepancy Found
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#00d084]" />
                  Pass Consistency
                </span>
              )}
            </div>
            <h4 className="text-sm font-bold text-slate-950 mb-1">Document Consistency</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              {isAltered
                ? 'Checksum mathematically matches internal algorithm, but VIZ/MRZ expiry year mismatch is confirmed: VIZ displays 2029 while MRZ reads 2026.'
                : 'All MRZ check digits, expiration logic, and visual zone dates are fully consistent and validated.'}
            </p>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[11px] font-mono text-slate-400">Weight: 42%</span>
            <button className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-900 hover:text-[#00d084] group cursor-pointer">
              <span>Inspect Inconsistency</span>
              <span className="w-5 h-5 rounded-full bg-slate-100 group-hover:bg-slate-900 group-hover:text-white flex items-center justify-center transition-colors">
                <ArrowRight className="w-3 h-3" />
              </span>
            </button>
          </div>
        </div>

        {/* Module 02: Forensic Integrity */}
        <div
          className={`bg-white border rounded-xl p-4 flex flex-col justify-between gap-3 shadow-xs transition-all ${
            isAltered ? 'border-rose-200' : 'border-slate-200'
          }`}
        >
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Module 02</span>
              {isAltered ? (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 text-xs font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                  Elevated Concern
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#00d084]" />
                  Uniform Background
                </span>
              )}
            </div>
            <h4 className="text-sm font-bold text-slate-950 mb-1">Forensic Integrity</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              {isAltered
                ? 'Localized DCT recompression signature detected around the expiry glyphs. Pixel gradient analysis suggests digital typeface overwrite.'
                : 'No SIFT copy-move feature clusters or localized neural patch manipulation signatures detected.'}
            </p>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[11px] font-mono text-slate-400">Weight: 38%</span>
            <button className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-900 hover:text-[#00d084] group cursor-pointer">
              <span>View Forensic Lens</span>
              <span className="w-5 h-5 rounded-full bg-slate-100 group-hover:bg-slate-900 group-hover:text-white flex items-center justify-center transition-colors">
                <ArrowRight className="w-3 h-3" />
              </span>
            </button>
          </div>
        </div>

        {/* Module 03: Structural Conformity */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col justify-between gap-3 shadow-xs">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Module 03</span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-[#00d084]" />
                Pass Conformity
              </span>
            </div>
            <h4 className="text-sm font-bold text-slate-950 mb-1">Structural Conformity</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              National template geometry, guilloche line fidelity, and microfont baselines remain within acceptable variance limits (±0.02mm).
            </p>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[11px] font-mono text-slate-400">Variance: 0.018mm</span>
            <span className="text-xs font-medium text-slate-400 flex items-center gap-1">
              <Check className="w-4 h-4 text-emerald-500" /> Verified
            </span>
          </div>
        </div>

        {/* Module 04: Biometric & Identity Consistency */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col justify-between gap-3 shadow-xs">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Module 04</span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-[#00d084]" />
                Match Confirmed
              </span>
            </div>
            <h4 className="text-sm font-bold text-slate-950 mb-1">Biometric / Identity Consistency</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Facial portrait biometric similarity scores 98.2% cosine match against reference citizen repository. Zero presentation attack indicators detected.
            </p>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[11px] font-mono text-slate-400">Cosine: 0.892</span>
            <span className="text-xs font-medium text-slate-400 flex items-center gap-1">
              <Check className="w-4 h-4 text-emerald-500" /> 1:1 Match
            </span>
          </div>
        </div>
      </div>

      {/* Actionable Key Findings Checklist */}
      <div className="pt-2 flex flex-col gap-2">
        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Actionable Key Findings</span>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
          <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4.5 h-4.5 text-[#00d084]" />
              <span className="font-medium text-slate-800">MRZ checksum mathematical validity</span>
            </div>
            <span className="font-mono text-slate-500 text-[11px]">Passed</span>
          </div>

          <div
            className={`flex items-center justify-between p-2.5 rounded-lg ${
              isAltered ? 'bg-rose-50/70 border border-rose-200' : 'bg-slate-50 border border-slate-200'
            }`}
          >
            <div className="flex items-center gap-2">
              {isAltered ? (
                <AlertTriangle className="w-4.5 h-4.5 text-rose-600" />
              ) : (
                <CheckCircle2 className="w-4.5 h-4.5 text-[#00d084]" />
              )}
              <span className={`font-semibold ${isAltered ? 'text-rose-950' : 'text-slate-800'}`}>
                {isAltered ? 'VIZ / MRZ expiry date conflict (2029 vs 2026)' : 'VIZ / MRZ date cross-check'}
              </span>
            </div>
            {isAltered ? (
              <span className="text-rose-700 font-bold text-[11px]">Inspect →</span>
            ) : (
              <span className="font-mono text-slate-500 text-[11px]">Passed</span>
            )}
          </div>

          <div
            className={`flex items-center justify-between p-2.5 rounded-lg ${
              isAltered ? 'bg-rose-50/70 border border-rose-200' : 'bg-slate-50 border border-slate-200'
            }`}
          >
            <div className="flex items-center gap-2">
              {isAltered ? (
                <AlertTriangle className="w-4.5 h-4.5 text-rose-600" />
              ) : (
                <CheckCircle2 className="w-4.5 h-4.5 text-[#00d084]" />
              )}
              <span className={`font-semibold ${isAltered ? 'text-rose-950' : 'text-slate-800'}`}>
                {isAltered ? 'Localized compression anomaly in Region B2' : 'Substrate compression analysis'}
              </span>
            </div>
            {isAltered ? (
              <span className="text-rose-700 font-bold text-[11px]">Inspect →</span>
            ) : (
              <span className="font-mono text-slate-500 text-[11px]">Passed</span>
            )}
          </div>

          <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4.5 h-4.5 text-[#00d084]" />
              <span className="font-medium text-slate-800">1:1 Biometric Face Match (0.892 similarity)</span>
            </div>
            <span className="font-mono text-slate-500 text-[11px]">Passed</span>
          </div>
        </div>
      </div>
    </div>
  );
};
