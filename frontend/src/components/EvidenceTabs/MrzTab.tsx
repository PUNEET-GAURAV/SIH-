import React from 'react';
import { MRZData } from '../../types';
import { CheckCircle, XCircle, AlertTriangle, FileCode } from 'lucide-react';

interface MrzTabProps {
  mrzData?: MRZData;
}

export const MrzTab: React.FC<MrzTabProps> = ({ mrzData }) => {
  const parsed = mrzData?.parsed_fields;
  const checksums = mrzData?.checksum_results || {};
  const isExpired = parsed?.expiry_date ? new Date(parsed.expiry_date) < new Date() : false;

  return (
    <div className="space-y-6">
      {/* Raw MRZ View */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-slate-200">Raw Machine Readable Zone (ICAO 9303)</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
            {parsed?.document_type ? `TYPE ${parsed.document_type}` : 'ICAO MRZ'}
          </span>
        </div>
        <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-sm tracking-widest text-emerald-400 leading-relaxed overflow-x-auto select-all">
          {mrzData?.raw_mrz || 'NO MRZ DETECTED ON DOCUMENT'}
        </div>
      </div>

      {/* Checksum Validation Matrix */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-4 py-3 bg-slate-900 border-b border-slate-800">
          <span className="text-xs font-bold text-slate-200">ICAO 7-3-1 Checksum Validation Matrix</span>
        </div>
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-slate-950/60 text-slate-400 text-[11px] uppercase border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-4">Field</th>
              <th className="py-2.5 px-4">Field Value</th>
              <th className="py-2.5 px-4 text-center">Expected Check Digit</th>
              <th className="py-2.5 px-4 text-center">Actual Check Digit</th>
              <th className="py-2.5 px-4 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {Object.entries(checksums).map(([key, item]) => (
              <tr key={key} className="hover:bg-slate-800/40 transition">
                <td className="py-2.5 px-4 capitalize font-semibold text-slate-300">{key.replace('_', ' ')}</td>
                <td className="py-2.5 px-4 text-slate-100">{item.field || 'N/A'}</td>
                <td className="py-2.5 px-4 text-center text-slate-400">{item.expected ?? '-'}</td>
                <td className="py-2.5 px-4 text-center text-slate-400">{item.actual ?? '-'}</td>
                <td className="py-2.5 px-4 text-center">
                  {item.valid ? (
                    <span className="inline-flex items-center text-emerald-400 font-bold text-[10px]">
                      <CheckCircle className="w-3.5 h-3.5 mr-1" /> VALID
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-rose-400 font-bold text-[10px]">
                      <XCircle className="w-3.5 h-3.5 mr-1" /> FAILED
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Parsed Fields Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-900/60 border border-slate-800 p-4 rounded-xl text-xs font-mono">
        <div>
          <span className="text-[10px] text-slate-500 uppercase block">Surname</span>
          <span className="font-bold text-slate-100">{parsed?.surname || '-'}</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 uppercase block">Given Names</span>
          <span className="font-bold text-slate-100">{parsed?.given_names || '-'}</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 uppercase block">Document Number</span>
          <span className="font-bold text-cyan-400">{parsed?.document_number || '-'}</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 uppercase block">Nationality</span>
          <span className="font-bold text-slate-100">{parsed?.nationality || '-'}</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 uppercase block">Date of Birth</span>
          <span className="font-bold text-slate-100">{parsed?.date_of_birth || '-'}</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 uppercase block">Date of Expiry</span>
          <span className={`font-bold ${isExpired ? 'text-amber-400' : 'text-slate-100'}`}>
            {parsed?.expiry_date || '-'} {isExpired ? '(EXPIRED)' : ''}
          </span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 uppercase block">Sex</span>
          <span className="font-bold text-slate-100">{parsed?.sex || '-'}</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 uppercase block">Issuing Country</span>
          <span className="font-bold text-slate-100">{parsed?.country_code || '-'}</span>
        </div>
      </div>
    </div>
  );
};
