import React, { useState } from 'react';
import { Maximize2, ShieldCheck, CheckCircle2, Sliders, Layers, Eye } from 'lucide-react';
import { QualityDetails, OCRFieldData, ForensicResultData, DemoScenario } from '../types';

interface DocumentPreviewColProps {
  documentType?: string;
  qualityStatus?: string;
  qualityDetails?: QualityDetails;
  ocrFields?: OCRFieldData[];
  forensicResults?: ForensicResultData[];
  scenario: DemoScenario;
  uploadedImageUrl?: string | null;
}

export const DocumentPreviewCol: React.FC<DocumentPreviewColProps> = ({
  documentType,
  qualityStatus,
  qualityDetails,
  ocrFields = [],
  forensicResults = [],
  scenario,
  uploadedImageUrl,
}) => {
  const [activeMode, setActiveMode] = useState<string>('Original');
  const [showOverlays, setShowOverlays] = useState<boolean>(true);
  const [showHeatmap, setShowHeatmap] = useState<boolean>(false);

  // Map demo scenarios to default preview images if no user upload
  const defaultScenarioImages: Record<DemoScenario, string> = {
    genuine: 'https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=800&q=80',
    altered_dob: 'https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=800&q=80',
    expired: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80',
    wrong_face: 'https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=800&q=80',
    poor_capture: 'https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=800&q=80',
    unknown_document: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80',
  };

  const imageSrc = uploadedImageUrl || defaultScenarioImages[scenario] || defaultScenarioImages.genuine;
  const isAadhaar = documentType?.toLowerCase().includes('aadhaar') || uploadedImageUrl;

  const blurScore = qualityDetails?.blur_score ?? 420.0;
  const glareRatio = qualityDetails?.glare_ratio ?? 0.01;
  const blurPct = Math.min(Math.round((blurScore / 500) * 100), 99);
  const glarePct = Math.round(glareRatio * 100);

  return (
    <div className="flex flex-col space-y-4 h-full overflow-y-auto select-none pr-1">
      {/* CARD 1: DOCUMENT PREVIEW */}
      <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-4 flex flex-col space-y-3 shadow-xl">
        {/* Preview Top Header & Filters */}
        <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
          <span className="text-xs font-bold text-slate-200 tracking-wider uppercase">Document Preview</span>
          
          <div className="flex items-center space-x-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800">
            {['Original', 'Enhance', 'UV (Sim.)', 'IR (Sim.)'].map((mode) => (
              <button
                key={mode}
                onClick={() => setActiveMode(mode)}
                className={`px-2.5 py-1 rounded-lg text-[10px] font-bold transition cursor-pointer ${
                  activeMode === mode
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                {mode}
              </button>
            ))}
            <button className="p-1 text-slate-400 hover:text-white transition ml-1" title="Fullscreen">
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Canvas Display Frame */}
        <div className="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800/90 flex items-center justify-center min-h-[310px] p-2 group">
          <img
            src={imageSrc}
            alt="Document Display Canvas"
            className={`max-h-[320px] w-auto object-contain rounded-lg shadow-2xl transition duration-300 ${
              activeMode === 'Enhance' ? 'contrast-125 brightness-110 saturate-110' :
              activeMode === 'UV (Sim.)' ? 'hue-rotate-180 invert brightness-90' :
              activeMode === 'IR (Sim.)' ? 'grayscale contrast-150' : ''
            }`}
          />

          {/* Bounding Boxes Overlay */}
          {showOverlays && (
            <div className="absolute inset-2 pointer-events-none flex items-center justify-center">
              <div className="relative w-full h-full max-h-[320px]">
                {/* Simulated bounding boxes for extracted OCR / Forensics */}
                {scenario === 'altered_dob' ? (
                  <div className="absolute top-[48%] left-[25%] w-[45%] h-[12%] border-2 border-rose-500 bg-rose-500/20 rounded shadow-lg animate-pulse flex items-center justify-end px-1">
                    <span className="bg-rose-950 text-rose-300 text-[9px] font-bold px-1 rounded border border-rose-500">
                      TAMPER DETECTED
                    </span>
                  </div>
                ) : (
                  <div className="absolute top-[60%] left-[20%] w-[55%] h-[10%] border border-cyan-400/80 bg-cyan-500/10 rounded flex items-center justify-end px-1">
                    <span className="bg-cyan-950 text-cyan-300 text-[9px] font-mono px-1 rounded border border-cyan-500/50">
                      OCR_VERIFIED
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Heatmap Layer Simulation */}
          {showHeatmap && (
            <div className="absolute inset-2 pointer-events-none rounded-lg overflow-hidden mix-blend-color-dodge opacity-70 bg-gradient-to-tr from-blue-600 via-yellow-500 to-rose-600" />
          )}

          {/* Floating Canvas Controls */}
          <div className="absolute bottom-3 right-3 flex items-center space-x-1.5 bg-slate-900/90 backdrop-blur-md p-1 rounded-xl border border-slate-800 opacity-90 group-hover:opacity-100 transition">
            <button
              onClick={() => setShowOverlays(!showOverlays)}
              className={`px-2 py-1 rounded-lg text-[10px] font-bold flex items-center space-x-1 cursor-pointer ${
                showOverlays ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400'
              }`}
            >
              <Eye className="w-3 h-3" />
              <span>Overlays</span>
            </button>
            <button
              onClick={() => setShowHeatmap(!showHeatmap)}
              className={`px-2 py-1 rounded-lg text-[10px] font-bold flex items-center space-x-1 cursor-pointer ${
                showHeatmap ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'text-slate-400'
              }`}
            >
              <Layers className="w-3 h-3" />
              <span>Heatmap</span>
            </button>
          </div>
        </div>

        {/* Capture Quality Bar */}
        <div className="bg-slate-950/80 rounded-xl p-3 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-xs font-bold">
            <span className="text-slate-300">Capture Quality</span>
            <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono text-[10px]">
              Excellent 92%
            </span>
          </div>

          <div className="grid grid-cols-4 gap-2 pt-1">
            <div className="bg-slate-900/80 p-1.5 rounded-lg border border-slate-800 text-center">
              <span className="text-[9px] text-slate-400 uppercase block font-semibold">Blur</span>
              <span className="text-[11px] font-mono font-bold text-emerald-400">2%</span>
            </div>
            <div className="bg-slate-900/80 p-1.5 rounded-lg border border-slate-800 text-center">
              <span className="text-[9px] text-slate-400 uppercase block font-semibold">Glare</span>
              <span className="text-[11px] font-mono font-bold text-emerald-400">3%</span>
            </div>
            <div className="bg-slate-900/80 p-1.5 rounded-lg border border-slate-800 text-center">
              <span className="text-[9px] text-slate-400 uppercase block font-semibold">Crop</span>
              <span className="text-[11px] font-mono font-bold text-emerald-400">1%</span>
            </div>
            <div className="bg-slate-900/80 p-1.5 rounded-lg border border-slate-800 text-center">
              <span className="text-[9px] text-slate-400 uppercase block font-semibold">Resolution</span>
              <span className="text-[11px] font-mono font-bold text-cyan-300">1080p</span>
            </div>
          </div>
        </div>
      </div>

      {/* CARD 2: DOCUMENT INFO METADATA */}
      <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-4 flex flex-col space-y-3 shadow-xl">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
          <span className="text-xs font-bold text-slate-200 tracking-wider uppercase">Document Info</span>
          <span className="text-[10px] text-cyan-400 font-mono flex items-center space-x-1">
            <CheckCircle2 className="w-3 h-3 text-cyan-400" />
            <span>Verified</span>
          </span>
        </div>

        <div className="space-y-2 text-xs">
          <div className="flex justify-between items-center py-1 border-b border-slate-800/40">
            <span className="text-slate-400 font-medium">Type</span>
            <span className="font-semibold text-slate-200">{uploadedImageUrl ? 'Aadhaar Card' : documentType || 'Passport TD3'}</span>
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-800/40">
            <span className="text-slate-400 font-medium">Country</span>
            <span className="font-semibold text-slate-200">India</span>
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-800/40">
            <span className="text-slate-400 font-medium">Template Match</span>
            <span className="font-semibold text-emerald-400 flex items-center space-x-1">
              <span>98%</span>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            </span>
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-800/40">
            <span className="text-slate-400 font-medium">Orientation</span>
            <span className="font-mono text-slate-300">0°</span>
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-800/40">
            <span className="text-slate-400 font-medium">Dimensions</span>
            <span className="font-mono text-slate-300">1024 x 1280</span>
          </div>
          <div className="flex justify-between items-center py-1 border-b border-slate-800/40">
            <span className="text-slate-400 font-medium">File Size</span>
            <span className="font-mono text-slate-300">1.2 MB</span>
          </div>
          <div className="flex justify-between items-center pt-1">
            <span className="text-slate-400 font-medium">Captured At</span>
            <span className="font-mono text-[11px] text-slate-400">19 May 2025, 11:42 AM</span>
          </div>
        </div>
      </div>
    </div>
  );
};
