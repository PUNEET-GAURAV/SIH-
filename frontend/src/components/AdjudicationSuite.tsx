import React, { useState } from 'react';
import {
  AlertTriangle, ShieldAlert, CheckCircle2, RotateCcw, Lock, ShieldCheck, FileCheck, Check
} from 'lucide-react';
import { DecisionAction, OfficerDecisionData, ScreeningAssessmentData } from '../types';

interface AdjudicationSuiteProps {
  assessment?: ScreeningAssessmentData;
  decision?: OfficerDecisionData;
  onSubmitDecision: (action: DecisionAction, notes: string) => Promise<void>;
  isSubmitting: boolean;
}

export const AdjudicationSuite: React.FC<AdjudicationSuiteProps> = ({
  assessment,
  decision,
  onSubmitDecision,
  isSubmitting,
}) => {
  const [selectedAction, setSelectedAction] = useState<DecisionAction>('secondary_inspection');
  const [notes, setNotes] = useState<string>(
    'Flagged for physical verification of date field substrate under 365nm UV light and tactile micro-perforation check.'
  );

  const handleActionClick = (action: DecisionAction) => {
    setSelectedAction(action);
    if (action === 'secondary_inspection') {
      setNotes('Flagged for physical verification of date field substrate under 365nm UV light and tactile micro-perforation check.');
    } else if (action === 'clear') {
      setNotes('Manual officer override applied. Discrepancy evaluated as allowable specimen printing registration variance.');
    } else if (action === 'escalate') {
      setNotes('Escalated to Duty Inspector STN-01 for suspected fraudulent mechanical erasure and printing forgery.');
    } else if (action === 'request_recapture') {
      setNotes('Requested high-resolution rescanning with calibrated optical angle to eliminate substrate sheen.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAction || isSubmitting) return;
    await onSubmitDecision(selectedAction, notes);
  };

  return (
    <aside className="flex flex-col gap-6 select-none">
      {/* Main Decision Suite Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6 flex flex-col gap-5">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Screening Adjudication</span>
          <span className="font-mono text-xs font-semibold text-slate-600">SESSION #SCN-9941</span>
        </div>

        {/* Executive Review Required Banner (Warm Gold / Amber) */}
        <div className="rounded-xl p-4 bg-amber-50/80 border border-amber-200/90 text-amber-950 flex flex-col gap-2 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
              <span className="text-sm font-bold tracking-tight text-amber-900">REVIEW REQUIRED</span>
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-200/80 text-amber-900">
              Risk: High
            </span>
          </div>
          <ul className="text-xs text-amber-900/90 space-y-1 pl-5 list-disc font-sans">
            <li>OCR visual expiration contradicts encrypted MRZ strip</li>
            <li>Digital recompression signature detected on expiration line</li>
            <li>Physical tamper check required prior to release</li>
          </ul>
        </div>

        {/* Evidence Contribution Breakdown Bars */}
        <div className="flex flex-col gap-2.5">
          <div className="flex justify-between items-center text-xs">
            <span className="font-semibold text-slate-700">Evidence Risk Contribution</span>
            <span className="text-slate-400 font-mono text-[11px]">Combined Index: 80/100</span>
          </div>

          {/* Bar 1 */}
          <div className="flex flex-col gap-1">
            <div className="flex justify-between text-xs">
              <span className="text-slate-600">Document Consistency</span>
              <span className="font-mono font-semibold text-rose-600">Needs Review (42%)</span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-rose-500 rounded-full w-[42%]" />
            </div>
          </div>

          {/* Bar 2 */}
          <div className="flex flex-col gap-1">
            <div className="flex justify-between text-xs">
              <span className="text-slate-600">Forensic Integrity</span>
              <span className="font-mono font-semibold text-rose-600">Elevated (38%)</span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-rose-500 rounded-full w-[38%]" />
            </div>
          </div>

          {/* Bar 3 */}
          <div className="flex flex-col gap-1">
            <div className="flex justify-between text-xs">
              <span className="text-slate-600">Structural Conformity</span>
              <span className="font-mono font-semibold text-emerald-600">Consistent (12%)</span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-[#00d084] rounded-full w-[12%]" />
            </div>
          </div>

          {/* Bar 4 */}
          <div className="flex flex-col gap-1">
            <div className="flex justify-between text-xs">
              <span className="text-slate-600">Identity Consistency</span>
              <span className="font-mono font-semibold text-emerald-600">Consistent (8%)</span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-[#00d084] rounded-full w-[8%]" />
            </div>
          </div>
        </div>

        {/* Recommended Action Anchored Box */}
        <div className="p-4 rounded-xl bg-slate-900 text-white flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">System Recommendation</span>
            <span className="w-2 h-2 rounded-full bg-amber-400" />
          </div>
          <div className="flex items-center gap-2 text-sm font-bold text-white tracking-wide">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            SECONDARY PHYSICAL INSPECTION
          </div>
          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            Optical microscope & tactile examination recommended to authenticate date substrate overlay and UV ink integrity.
          </p>
        </div>

        {/* Officer Workflow Outcome Selector */}
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold text-slate-700">Select Adjudication Action</span>
          <div className="grid grid-cols-2 gap-2">
            {/* Secondary Inspection (Primary Option) */}
            <button
              type="button"
              onClick={() => handleActionClick('secondary_inspection')}
              className={`col-span-2 py-2.5 px-4 rounded-xl font-semibold text-xs flex items-center justify-between transition-all cursor-pointer ${
                selectedAction === 'secondary_inspection'
                  ? 'bg-slate-950 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <span className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Secondary Inspection Required
              </span>
              {selectedAction === 'secondary_inspection' && (
                <CheckCircle2 className="w-4.5 h-4.5 text-[#00d084]" />
              )}
            </button>

            {/* Clear Document */}
            <button
              type="button"
              onClick={() => handleActionClick('clear')}
              className={`py-2.5 px-3 rounded-xl font-semibold text-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                selectedAction === 'clear'
                  ? 'bg-slate-950 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <Check className="w-4 h-4 text-[#00d084]" />
              Clear Document
            </button>

            {/* Escalate */}
            <button
              type="button"
              onClick={() => handleActionClick('escalate')}
              className={`py-2.5 px-3 rounded-xl font-semibold text-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                selectedAction === 'escalate'
                  ? 'bg-rose-600 text-white shadow-sm'
                  : 'bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200'
              }`}
            >
              <ShieldAlert className="w-4 h-4 text-rose-600" />
              Escalate to Supervisor
            </button>

            {/* Request Recapture */}
            <button
              type="button"
              onClick={() => handleActionClick('request_recapture')}
              className={`col-span-2 py-2 px-3 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-100 font-medium text-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                selectedAction === 'request_recapture' ? 'bg-slate-200 text-slate-900 border-slate-400' : 'bg-slate-50'
              }`}
            >
              <RotateCcw className="w-4 h-4 text-slate-500" />
              Request Re-scan / High-Res Optical Ingestion
            </button>
          </div>
        </div>

        {/* Mandatory Adjudication Notes */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-2 pt-1">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-700">
              Adjudication Note <span className="text-rose-600">*</span>
            </label>
            <span className="font-mono text-[11px] text-slate-400">{notes.length} chars</span>
          </div>

          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-slate-950 transition-all resize-none leading-relaxed font-sans"
          />

          {/* Submit Decision CTA with Jumio green accent */}
          <div className="flex flex-col gap-2 pt-1">
            {decision ? (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-950 flex flex-col gap-1 animate-fadeIn">
                <div className="flex items-center justify-between text-xs font-bold">
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-[#00d084]" />
                    Official Decision Recorded: {decision.decision.toUpperCase()}
                  </span>
                  <span className="font-mono text-[10px] text-emerald-700">{decision.id}</span>
                </div>
                <div className="text-[11px] text-emerald-800 font-mono">
                  Timestamp: {new Date(decision.created_at).toLocaleTimeString()} • Officer STN-09
                </div>
                <div className="text-xs text-emerald-900 font-medium italic mt-1 bg-white/60 p-2 rounded">
                  "{decision.notes}"
                </div>
              </div>
            ) : (
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3.5 px-4 rounded-xl font-semibold text-xs flex items-center justify-center gap-2 shadow-sm transition-all cursor-pointer active:scale-95 bg-slate-950 hover:bg-slate-900 text-white jumio-glow"
              >
                <Lock className="w-4.5 h-4.5 text-[#00d084]" />
                <span>{isSubmitting ? 'Recording Sealed Decision...' : 'Submit Official Decision'}</span>
              </button>
            )}

            <div className="flex items-center justify-center gap-1.5 text-center text-[11px] text-slate-400 font-mono">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#00d084]" />
              <span>Signed with cryptographic seal: STN-09-SHA256</span>
            </div>
          </div>
        </form>
      </div>

      {/* Quick Telemetry Micro-Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-4 flex items-center justify-between text-xs text-slate-500 shadow-xs">
        <div className="flex items-center gap-2.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#00d084] animate-pulse" />
          <span className="font-medium text-slate-800">DocShield Neural Engine v4.8</span>
        </div>
        <span className="font-mono text-slate-400">Latency: 142ms</span>
      </div>
    </aside>
  );
};
