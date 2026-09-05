import React, { useState } from 'react';
import { AuditLogData } from '../../types';
import { ShieldCheck, Lock, Hash, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';

interface AuditTabProps {
  sessionId: string;
  auditTrail: AuditLogData[];
  onVerifyAudit: () => Promise<{ is_valid: boolean; total_entries: number; broken_entry_id?: string }>;
}

export const AuditTab: React.FC<AuditTabProps> = ({ sessionId, auditTrail, onVerifyAudit }) => {
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<{ is_valid: boolean; total_entries: number; broken_entry_id?: string } | null>(null);

  const handleVerify = async () => {
    setIsVerifying(true);
    try {
      const res = await onVerifyAudit();
      setVerificationResult(res);
    } catch (e) {
      console.error('Audit verification error', e);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Verify Chain Header & Action */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Lock className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-100">Tamper-Evident Hash-Chained Audit Log</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Every pipeline stage and officer decision is cryptographically hash-chained (H_n = SHA256(event_n + H_n-1)).
          </p>
        </div>

        <button
          onClick={handleVerify}
          disabled={isVerifying}
          className="px-4 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs transition flex items-center justify-center space-x-2 shadow-lg shadow-cyan-600/20 shrink-0"
        >
          <RefreshCw className={`w-4 h-4 ${isVerifying ? 'animate-spin' : ''}`} />
          <span>VERIFY AUDIT CHAIN INTEGRITY</span>
        </button>
      </div>

      {/* Verification Result Alert */}
      {verificationResult && (
        <div className={`p-4 rounded-xl border flex items-start space-x-3 transition ${
          verificationResult.is_valid
            ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
            : 'bg-rose-950/40 border-rose-500/40 text-rose-300'
        }`}>
          {verificationResult.is_valid ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          )}
          <div className="space-y-1 text-xs">
            <h4 className="font-bold">
              {verificationResult.is_valid ? 'AUDIT CHAIN INTEGRITY CONFIRMED' : 'AUDIT CHAIN BROKEN — RETROACTIVE TAMPERING DETECTED'}
            </h4>
            <p className="opacity-90">
              Verified {verificationResult.total_entries} log entries sequentially.
              {verificationResult.is_valid
                ? ' All entry hashes match cryptographic previous hash linkages perfectly.'
                : ` Broken link detected at entry ID: ${verificationResult.broken_entry_id}.`}
            </p>
          </div>
        </div>
      )}

      {/* Timeline Entries */}
      <div className="space-y-3">
        <span className="text-xs font-bold text-slate-300 block uppercase tracking-wider">
          Audit Event History ({auditTrail.length} Events)
        </span>

        <div className="space-y-3 relative before:absolute before:inset-0 before:left-4 before:w-0.5 before:bg-slate-800">
          {auditTrail.map((entry, idx) => (
            <div key={entry.id || idx} className="relative pl-10">
              {/* Dot */}
              <div className="absolute left-2.5 top-3.5 -translate-x-1/2 w-3 h-3 rounded-full bg-cyan-500 border-2 border-slate-900 shadow-md shadow-cyan-500/50" />

              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider font-mono">
                    {entry.event_type.replace('_', ' ')}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    {new Date(entry.timestamp).toLocaleString()}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-950 p-2.5 rounded border border-slate-850">
                  <div>
                    <span className="text-slate-500 block">Previous Hash H(n-1)</span>
                    <span className="truncate block text-slate-300">{entry.previous_hash || 'GENESIS_NODE_00000'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Entry Hash H(n)</span>
                    <span className="truncate block text-cyan-400 font-bold">{entry.entry_hash}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
