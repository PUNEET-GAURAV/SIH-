import React, { useState } from 'react';
import {
  ShieldCheck, AlertTriangle, ShieldAlert, RotateCcw, Lock, CheckCircle2, Cpu, ArrowUpRight, ArrowDownRight
} from 'lucide-react';
import { ScreeningAssessmentData, OfficerDecisionData, DecisionAction } from '../types';

interface AssessmentPanelProps {
  assessment?: ScreeningAssessmentData;
  decision?: OfficerDecisionData;
  onSubmitDecision: (action: DecisionAction, notes: string) => Promise<void>;
  isSubmitting: boolean;
}

export const AssessmentPanel: React.FC<AssessmentPanelProps> = ({
  assessment,
  decision,
  onSubmitDecision,
  isSubmitting,
}) => {
  const [selectedAction, setSelectedAction] = useState<DecisionAction>('clear');
  const [notes, setNotes] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAction || isSubmitting) return;
    await onSubmitDecision(selectedAction, notes);
  };

  return (
    <div className="flex flex-col space-y-4 h-full overflow-y-auto select-none pr-1">
      {/* CARD 1: ASSESSMENT & RISK CARD */}
      <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-4 flex flex-col space-y-3 shadow-xl">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
          <span className="text-xs font-bold text-slate-200 tracking-wider uppercase">Assessment & Decision</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
            OFFICER DECISION ENGINE
          </span>
        </div>

        {/* Risk Banner Card */}
        <div className="p-4 rounded-2xl bg-gradient-to-tr from-[#0b1c24] to-[#0d2a33] border border-cyan-500/30 space-y-2 relative overflow-hidden shadow-inner">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-extrabold text-emerald-400 font-sans tracking-wide">LOW RISK</span>
                <span className="text-[9px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-mono">
                  RECOMMEND: ROUTINE CHECK
                </span>
              </div>
              <div className="flex items-baseline space-x-1 mt-1">
                <span className="text-3xl font-black text-white font-mono">18</span>
                <span className="text-xs text-slate-400 font-mono">/100</span>
              </div>
            </div>

            {/* Shield Emblem Icon */}
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shadow-lg shadow-emerald-500/10">
              <ShieldCheck className="w-7 h-7 text-emerald-400" />
            </div>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed font-sans pt-1">
            Document appears consistent with expected patterns. No strong indicators of tampering.
          </p>
          <span className="text-[10px] text-cyan-400/80 font-medium block">Review evidence tabs for details.</span>
        </div>
      </div>

      {/* CARD 2: OFFICER ACTIONS (2x2 GRID) */}
      <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-4 flex flex-col space-y-3 shadow-xl">
        <span className="text-xs font-bold text-slate-200 tracking-wider uppercase block">Officer Actions</span>

        <div className="grid grid-cols-2 gap-2.5">
          {/* CLEAR */}
          <button
            type="button"
            onClick={() => setSelectedAction('clear')}
            className={`p-3 rounded-xl border flex flex-col items-start transition cursor-pointer text-left ${
              selectedAction === 'clear'
                ? 'bg-emerald-950/40 border-emerald-500 text-emerald-300 shadow-lg shadow-emerald-500/10 ring-1 ring-emerald-500/50'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <div className="w-6 h-6 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
              </div>
              {selectedAction === 'clear' && <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />}
            </div>
            <span className="text-xs font-bold block text-slate-200">CLEAR</span>
            <span className="text-[9px] text-slate-400 font-medium">Approve & Proceed</span>
          </button>

          {/* SECONDARY INSPECTION */}
          <button
            type="button"
            onClick={() => setSelectedAction('secondary_inspection')}
            className={`p-3 rounded-xl border flex flex-col items-start transition cursor-pointer text-left ${
              selectedAction === 'secondary_inspection'
                ? 'bg-amber-950/40 border-amber-500 text-amber-300 shadow-lg shadow-amber-500/10 ring-1 ring-amber-500/50'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <div className="w-6 h-6 rounded-lg bg-amber-500/20 flex items-center justify-center text-amber-400">
                <AlertTriangle className="w-3.5 h-3.5" />
              </div>
              {selectedAction === 'secondary_inspection' && <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />}
            </div>
            <span className="text-xs font-bold block text-slate-200">SECONDARY INSPECTION</span>
            <span className="text-[9px] text-slate-400 font-medium">Send for Detailed Check</span>
          </button>

          {/* ESCALATE */}
          <button
            type="button"
            onClick={() => setSelectedAction('escalate')}
            className={`p-3 rounded-xl border flex flex-col items-start transition cursor-pointer text-left ${
              selectedAction === 'escalate'
                ? 'bg-rose-950/40 border-rose-500 text-rose-300 shadow-lg shadow-rose-500/10 ring-1 ring-rose-500/50'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <div className="w-6 h-6 rounded-lg bg-rose-500/20 flex items-center justify-center text-rose-400">
                <ShieldAlert className="w-3.5 h-3.5" />
              </div>
              {selectedAction === 'escalate' && <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping" />}
            </div>
            <span className="text-xs font-bold block text-slate-200">ESCALATE</span>
            <span className="text-[9px] text-slate-400 font-medium">Refer to Supervisor</span>
          </button>

          {/* RECAPTURE */}
          <button
            type="button"
            onClick={() => setSelectedAction('request_recapture')}
            className={`p-3 rounded-xl border flex flex-col items-start transition cursor-pointer text-left ${
              selectedAction === 'request_recapture'
                ? 'bg-cyan-950/40 border-cyan-500 text-cyan-300 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-500/50'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <div className="w-6 h-6 rounded-lg bg-cyan-500/20 flex items-center justify-center text-cyan-400">
                <RotateCcw className="w-3.5 h-3.5" />
              </div>
              {selectedAction === 'request_recapture' && <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />}
            </div>
            <span className="text-xs font-bold block text-slate-200">RECAPTURE</span>
            <span className="text-[9px] text-slate-400 font-medium">Retake Document</span>
          </button>
        </div>
      </div>

      {/* CARD 3: DECISION NOTES */}
      <form onSubmit={handleSubmit} className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-4 flex flex-col space-y-3 shadow-xl">
        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-slate-200 tracking-wider uppercase">Decision Notes / Rationale</span>
          <span className="text-[10px] text-slate-500 font-mono">{notes.length}/300</span>
        </div>

        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value.slice(0, 300))}
          placeholder="Enter notes for this decision..."
          rows={3}
          className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 resize-none font-sans placeholder:text-slate-600"
        />

        <button
          type="submit"
          disabled={isSubmitting || !!decision}
          className={`w-full py-2.5 rounded-xl text-xs font-bold transition flex items-center justify-center space-x-2 shadow-lg cursor-pointer ${
            decision
              ? 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white shadow-cyan-500/25 border border-cyan-400/30'
          }`}
        >
          <Lock className="w-3.5 h-3.5" />
          <span>{decision ? 'DECISION RECORDED' : 'SUBMIT OFFICIAL DECISION'}</span>
        </button>
      </form>

      {/* CARD 4: QUICK STATS METRICS GRID */}
      <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-3.5 space-y-2.5 shadow-xl">
        <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block">Quick Stats</span>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block font-medium">Today Analyzed</span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-base font-extrabold text-white font-mono">124</span>
              <span className="text-[9px] font-bold text-emerald-400 flex items-center">
                +18% <ArrowUpRight className="w-2.5 h-2.5" />
              </span>
            </div>
            <span className="text-[9px] text-slate-500 font-mono">vs yesterday</span>
          </div>

          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block font-medium">High Risk</span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-base font-extrabold text-rose-400 font-mono">7</span>
              <span className="text-[9px] font-bold text-emerald-400 flex items-center">
                -12% <ArrowDownRight className="w-2.5 h-2.5" />
              </span>
            </div>
            <span className="text-[9px] text-slate-500 font-mono">vs yesterday</span>
          </div>

          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block font-medium">Avg. Risk Score</span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-base font-extrabold text-cyan-300 font-mono">22</span>
              <span className="text-[9px] font-bold text-emerald-400 flex items-center">
                -5 <ArrowDownRight className="w-2.5 h-2.5" />
              </span>
            </div>
            <span className="text-[9px] text-slate-500 font-mono">vs yesterday</span>
          </div>

          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block font-medium">Pending Review</span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-base font-extrabold text-amber-300 font-mono">9</span>
              <span className="text-[9px] font-bold text-amber-400 flex items-center">
                +3 <ArrowUpRight className="w-2.5 h-2.5" />
              </span>
            </div>
            <span className="text-[9px] text-slate-500 font-mono">vs yesterday</span>
          </div>
        </div>
      </div>
    </div>
  );
};
