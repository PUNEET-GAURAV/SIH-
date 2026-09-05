import React from 'react';
import { OCRFieldData } from '../../types';
import { FileText, CheckCircle2, AlertCircle } from 'lucide-react';

interface OcrTabProps {
  fields?: OCRFieldData[];
  rawText?: string;
}

export const OcrTab: React.FC<OcrTabProps> = ({ fields = [], rawText }) => {
  return (
    <div className="space-y-6">
      {/* OCR Fields Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-200">Extracted VIZ Text Fields (OCR)</span>
          <span className="text-[10px] font-mono text-slate-400">{fields.length} Fields Extracted</span>
        </div>

        {fields.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs">No OCR fields extracted yet.</div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 font-mono text-[11px] uppercase border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Field Name</th>
                <th className="py-2.5 px-4">Extracted Value</th>
                <th className="py-2.5 px-4 text-center">Confidence</th>
                <th className="py-2.5 px-4 text-center">Bounding Box</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {fields.map((f, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="py-2.5 px-4 font-mono font-medium text-cyan-400 capitalize">
                    {f.field_name.replace('_', ' ')}
                  </td>
                  <td className="py-2.5 px-4 font-mono font-bold text-slate-100">
                    {f.field_value}
                  </td>
                  <td className="py-2.5 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded font-mono text-[10px] ${
                      f.confidence > 0.85 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      {(f.confidence * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-center font-mono text-[10px] text-slate-500">
                    {f.bbox ? `[${f.bbox.join(', ')}]` : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Raw OCR Output */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-2">
        <span className="text-xs font-bold text-slate-300 block">Raw OCR Engine Text Output</span>
        <pre className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed">
          {rawText || fields.map(f => `${f.field_name}: ${f.field_value}`).join('\n') || 'No raw text available.'}
        </pre>
      </div>
    </div>
  );
};
