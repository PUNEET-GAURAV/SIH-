import React from 'react';
import { ForensicResultData } from '../../types';
import { ShieldAlert, Flame, Cpu, Search, CheckCircle } from 'lucide-react';

interface ForensicsTabProps {
  forensicResults?: ForensicResultData[];
}

export const ForensicsTab: React.FC<ForensicsTabProps> = ({ forensicResults = [] }) => {
  const hasHighConcern = forensicResults.some(f => f.status === 'high');

  return (
    <div className="space-y-6">
      {/* Forensic Summary Alert */}
      {hasHighConcern ? (
        <div className="bg-rose-950/40 border border-rose-500/40 rounded-xl p-4 flex items-start space-x-3">
          <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-xs font-bold text-rose-200">LOCALIZED MANIPULATION DETECTED</h4>
            <p className="text-xs text-rose-300/90 leading-relaxed">
              Feature keypoint matching and EfficientNet-B0 CNN patch evaluation detected suspicious copy-move or text substitution signatures on document fields.
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-emerald-950/30 border border-emerald-500/30 rounded-xl p-4 flex items-start space-x-3">
          <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-xs font-bold text-emerald-200">NO FORENSIC MANIPULATION DETECTED</h4>
            <p className="text-xs text-emerald-300/90 leading-relaxed">
              SIFT/ORB copy-move analysis and CNN patch evaluations indicate natural noise background without duplicated feature clusters.
            </p>
          </div>
        </div>
      )}

      {/* Detector Signals List */}
      <div className="space-y-3">
        <span className="text-xs font-bold text-slate-300 block uppercase tracking-wider">
          Concurrent Detector Results ({forensicResults.length})
        </span>

        {forensicResults.map((sig, idx) => (
          <div key={idx} className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <Search className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-bold text-slate-200 capitalize">
                  {sig.detector_type.replace('_', ' ')} Detector
                </span>
              </div>
              <span className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold ${
                sig.status === 'high' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' :
                sig.status === 'medium' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
              }`}>
                STATUS: {sig.status.toUpperCase()}
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">{sig.explanation}</p>

            <div className="flex justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/60">
              <span>Confidence: {(sig.confidence * 100).toFixed(0)}%</span>
              <span>Reliability: {(sig.reliability * 100).toFixed(0)}%</span>
              <span>Region: {sig.region ? `[${sig.region.join(', ')}]` : 'Full Image'}</span>
              <span>Version: {sig.model_version || 'v1'}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
