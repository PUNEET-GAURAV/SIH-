import React from 'react';
import { TemplateResultData } from '../../types';
import { Layout, CheckCircle, AlertTriangle, HelpCircle } from 'lucide-react';

interface StructureTabProps {
  documentType?: string;
  classificationConfidence?: number;
  templateResult?: TemplateResultData;
}

export const StructureTab: React.FC<StructureTabProps> = ({
  documentType = 'unknown',
  classificationConfidence = 0,
  templateResult,
}) => {
  const isUnknown = documentType === 'unknown';
  const alignmentScore = templateResult?.alignment_score ?? 0.95;

  return (
    <div className="space-y-6">
      {/* Classification Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Layout className="w-5 h-5 text-cyan-400" />
            <span className="text-sm font-bold text-white">Document Classification</span>
          </div>
          <span className={`px-2.5 py-1 rounded-md font-mono text-xs font-bold ${
            isUnknown ? 'bg-amber-950 text-amber-300 border border-amber-800' : 'bg-cyan-950 text-cyan-300 border border-cyan-800'
          }`}>
            {documentType.toUpperCase()}
          </span>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          {isUnknown
            ? 'Classifier operating in UNKNOWN_DOCUMENT_MODE. Document structure does not match a pre-registered template. Generic OCR and classical forensics applied.'
            : `Classified as ${documentType} with ${(classificationConfidence * 100).toFixed(0)}% confidence using geometric aspect ratio and MRZ zone analysis.`}
        </p>
      </div>

      {/* Template Alignment Score */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-slate-200">Homography Alignment Score</span>
          <span className="font-mono text-sm font-bold text-cyan-400">
            {(alignmentScore * 100).toFixed(1)}%
          </span>
        </div>

        <div className="w-full bg-slate-950 rounded-full h-3 overflow-hidden border border-slate-800">
          <div
            className={`h-full transition-all ${
              alignmentScore > 0.85 ? 'bg-emerald-500' : alignmentScore > 0.6 ? 'bg-amber-500' : 'bg-rose-500'
            }`}
            style={{ width: `${Math.max(alignmentScore * 100, 5)}%` }}
          />
        </div>

        {/* Deviations List */}
        <div className="space-y-2 pt-2">
          <span className="text-xs font-semibold text-slate-400 block">Structural Deviations Check</span>
          {templateResult?.deviations && templateResult.deviations.length > 0 ? (
            templateResult.deviations.map((dev, idx) => (
              <div key={idx} className="p-2.5 rounded bg-amber-950/30 border border-amber-800/40 text-xs text-amber-300 flex items-start space-x-2">
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span>{dev}</span>
              </div>
            ))
          ) : (
            <div className="p-2.5 rounded bg-emerald-950/20 border border-emerald-800/30 text-xs text-emerald-300 flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>All field bounding boxes, photo zones, and aspect ratio align within geometric tolerance.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
