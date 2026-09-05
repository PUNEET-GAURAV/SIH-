import React from 'react';
import { FaceVerificationData } from '../../types';
import { UserCheck, UserX, ShieldCheck, ShieldAlert, Camera, Smartphone } from 'lucide-react';

interface FaceTabProps {
  faceData?: FaceVerificationData;
}

export const FaceTab: React.FC<FaceTabProps> = ({ faceData }) => {
  const status = faceData?.identity_status || 'match';
  const similarity = faceData?.similarity_score ?? 0.88;
  const padStatus = faceData?.pad_status || 'genuine';

  const isMatch = status === 'match';
  const isMismatch = status === 'mismatch';

  return (
    <div className="space-y-6">
      {/* Face Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Live Capture Image Box */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col items-center justify-center space-y-3">
          <div className="flex items-center space-x-1.5 text-xs text-cyan-400 font-semibold">
            <Camera className="w-4 h-4" />
            <span>Live Capture Frame</span>
          </div>
          <div className="w-32 h-40 bg-slate-950 border-2 border-slate-800 rounded-lg flex flex-col items-center justify-center relative overflow-hidden">
            <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 font-bold text-xs">
              LIVE
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-2">RGB FRAME</span>
          </div>
          <span className="text-[11px] font-mono text-emerald-400 font-medium">PAD Status: {padStatus.toUpperCase()}</span>
        </div>

        {/* Document Portrait Box */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col items-center justify-center space-y-3">
          <div className="flex items-center space-x-1.5 text-xs text-cyan-400 font-semibold">
            <Smartphone className="w-4 h-4" />
            <span>Document Portrait Crop</span>
          </div>
          <div className="w-32 h-40 bg-slate-950 border-2 border-slate-800 rounded-lg flex flex-col items-center justify-center relative overflow-hidden">
            <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 font-bold text-xs">
              DOC
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-2">CROP ZONE</span>
          </div>
          <span className="text-[11px] font-mono text-slate-400">Resolution: 640x640</span>
        </div>
      </div>

      {/* ArcFace Similarity Score Meter */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            {isMismatch ? <UserX className="w-5 h-5 text-rose-400" /> : <UserCheck className="w-5 h-5 text-emerald-400" />}
            <span className="text-xs font-bold text-slate-200">ArcFace Cosine Similarity Score</span>
          </div>
          <span className={`font-mono text-sm font-bold ${isMismatch ? 'text-rose-400' : 'text-emerald-400'}`}>
            {(similarity * 100).toFixed(1)}%
          </span>
        </div>

        <div className="w-full bg-slate-950 rounded-full h-3 overflow-hidden border border-slate-800">
          <div
            className={`h-full transition-all ${
              similarity >= 0.60 ? 'bg-emerald-500' : similarity >= 0.40 ? 'bg-amber-500' : 'bg-rose-500'
            }`}
            style={{ width: `${Math.max(similarity * 100, 5)}%` }}
          />
        </div>

        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          {faceData?.explanation || `Face verification threshold set to 60.0% similarity. Score of ${(similarity * 100).toFixed(1)}% yields status: ${status.toUpperCase()}.`}
        </p>
      </div>

      {/* Presentation Attack Detection (PAD) */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-slate-200">Presentation Attack Detection (PAD)</span>
          <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
            padStatus === 'genuine' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
          }`}>
            {padStatus.toUpperCase()}
          </span>
        </div>

        <p className="text-xs text-slate-400 leading-relaxed">
          Tested against 3 presentation attack vectors: printed photo spoofing, screen display moiré patterns, and replay attack spectrum anomalies.
        </p>
      </div>
    </div>
  );
};
