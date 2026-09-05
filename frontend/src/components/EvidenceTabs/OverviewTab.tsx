import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, Layers, Cpu, Compass } from 'lucide-react';
import { ScreeningAssessmentData, DimensionResultData, ContradictionData } from '../../types';

interface OverviewTabProps {
  assessment?: ScreeningAssessmentData;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ assessment }) => {
  const dimensions = assessment?.dimension_results || {};
  const contradictions = assessment?.contradictions || [];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pass':
      case 'conforming':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">PASS</span>;
      case 'concern':
      case 'high':
      case 'mismatch':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">CONCERN</span>;
      case 'review':
      case 'deviation':
      case 'unknown':
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 font-mono">REVIEW</span>;
    }
  };

  const dimNames: Record<string, string> = {
    document_consistency: 'Document Consistency (MRZ/VIZ/Checksums)',
    structural_conformity: 'Structural & Template Conformity',
    manipulation_evidence: 'Forensic Manipulation & Copy-Move',
    identity_consistency: 'Identity Verification & PAD Liveness',
  };

  return (
    <div className="space-y-6">
      {/* Contradiction Surfacing Alerts */}
      {contradictions.length > 0 && (
        <div className="bg-rose-950/40 border border-rose-500/40 rounded-xl p-4 space-y-2">
          <div className="flex items-center space-x-2 text-rose-300 font-bold text-xs">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span>EXPLICIT CONTRADICTIONS SURFACED BY FUSION ENGINE</span>
          </div>
          {contradictions.map((c, i) => (
            <p key={i} className="text-xs text-rose-200/90 leading-relaxed bg-rose-900/30 p-2 rounded border border-rose-800/40">
              {c.description}
            </p>
          ))}
        </div>
      )}

      {/* 4 Dimension Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(dimNames).map(([key, label]) => {
          const dimData: DimensionResultData | undefined = dimensions[key];
          const status = dimData?.status || 'unknown';
          const score = dimData?.weighted_score ?? 0;

          return (
            <div key={key} className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-200">{label}</span>
                {getStatusBadge(status)}
              </div>

              {/* Progress / Concern Meter */}
              <div>
                <div className="flex justify-between text-[10px] text-slate-400 font-mono mb-1">
                  <span>Concern Score</span>
                  <span>{(score * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div
                    className={`h-full transition-all ${
                      score > 0.6 ? 'bg-rose-500' : score > 0.3 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.max(score * 100, 5)}%` }}
                  />
                </div>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">
                {dimData?.explanation || 'No findings reported for this dimension.'}
              </p>
            </div>
          );
        })}
      </div>

      {/* Fusion Explanation Box */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-2">
        <div className="flex items-center space-x-2 text-cyan-400 font-semibold text-xs">
          <Cpu className="w-4 h-4" />
          <span>Rule-Based Fusion Summary</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          {assessment?.summary || 'The fusion engine aggregates findings across deterministic check digits, template geometry, copy-move clusters, and face similarity using reliability-weighted scoring.'}
        </p>
      </div>
    </div>
  );
};
