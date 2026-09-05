import React, { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Eye, Flame, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';
import { OCRFieldData, ForensicResultData, QualityDetails } from '../types';

interface DocumentViewerProps {
  documentType?: string;
  qualityStatus?: string;
  qualityDetails?: QualityDetails;
  ocrFields?: OCRFieldData[];
  forensicResults?: ForensicResultData[];
  scenario: string;
  uploadedImageUrl?: string | null;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  documentType = 'passport_td3',
  qualityStatus = 'accept',
  qualityDetails,
  ocrFields = [],
  forensicResults = [],
  scenario,
  uploadedImageUrl,
}) => {
  const [zoom, setZoom] = useState(1);
  const [showOverlays, setShowOverlays] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(false);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.2, 2.5));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.2, 0.6));
  const handleResetZoom = () => setZoom(1);

  const isPoorQuality = qualityStatus === 'recapture_required';
  const isAlteredDOB = scenario === 'altered_dob';

  return (
    <div className="flex flex-col h-full bg-slate-900/60 border-r border-slate-800 rounded-xl overflow-hidden">
      {/* Viewer Control Bar */}
      <div className="h-12 px-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Document Canvas
          </span>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
            {uploadedImageUrl ? 'USER UPLOAD' : documentType.toUpperCase()}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          {/* Heatmap Toggle */}
          <button
            onClick={() => setShowHeatmap(!showHeatmap)}
            className={`px-2.5 py-1 rounded text-xs font-medium flex items-center space-x-1.5 transition ${
              showHeatmap
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                : 'bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-700'
            }`}
            title="Toggle forensic manipulation heatmap"
          >
            <Flame className="w-3.5 h-3.5" />
            <span>Heatmap</span>
          </button>

          {/* Overlays Toggle */}
          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`px-2.5 py-1 rounded text-xs font-medium flex items-center space-x-1.5 transition ${
              showOverlays
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                : 'bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-700'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Overlays</span>
          </button>

          <div className="h-4 w-px bg-slate-800 my-auto" />

          {/* Zoom controls */}
          <button
            onClick={handleZoomOut}
            className="p-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs font-mono text-slate-400 w-10 text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleResetZoom}
            className="p-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Image Display Area */}
      <div className="flex-1 relative overflow-auto p-6 flex items-center justify-center bg-slate-950/90">
        <div
          className="relative transition-transform duration-200 ease-out shadow-2xl rounded-lg overflow-hidden border border-slate-800 max-w-full"
          style={{ transform: `scale(${zoom})`, transformOrigin: 'center center' }}
        >
          {uploadedImageUrl ? (
            /* Real User Uploaded Image Render */
            <div className={`relative max-w-full transition-all ${isPoorQuality ? 'blur-md opacity-60' : ''}`}>
              <img
                src={uploadedImageUrl}
                alt="User Uploaded Document"
                className="max-h-[500px] max-w-[650px] rounded-lg object-contain shadow-2xl border border-slate-700"
              />

              {/* Bounding Box Overlays for User Uploaded Image */}
              {showOverlays && (
                <div className="absolute inset-0 pointer-events-none">
                  {ocrFields.map((f, i) => (
                    <div
                      key={i}
                      className="absolute border border-cyan-400/80 bg-cyan-400/10 rounded"
                      style={{
                        left: `${(i * 18 + 10) % 70}%`,
                        top: `${(i * 14 + 15) % 70}%`,
                        width: '25%',
                        height: '10%',
                      }}
                    >
                      <span className="text-[9px] font-mono bg-cyan-950 text-cyan-300 px-1 rounded absolute -top-4 left-0">
                        {f.field_name}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            /* Simulated Canvas for Presets */
            <div className={`w-[520px] h-[360px] relative transition-all ${isPoorQuality ? 'blur-md opacity-60' : ''}`}>
              <div className="absolute inset-0 bg-slate-900 border-4 border-slate-700 rounded-lg p-4 flex flex-col justify-between select-none">
                <div className="flex justify-between items-start border-b border-slate-800 pb-2">
                  <div className="flex space-x-3 items-center">
                    <div className="w-8 h-8 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 font-bold text-xs">
                      UTO
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-200 tracking-wider">REPUBLIC OF UTOPIA</div>
                      <div className="text-[10px] text-slate-400">PASSPORT / PASSEPORT</div>
                    </div>
                  </div>
                  <div className="text-right text-[10px] font-mono text-slate-400">TYPE P</div>
                </div>

                <div className="flex space-x-4 my-2">
                  <div className="w-32 h-40 bg-slate-800 border-2 border-slate-700 rounded relative overflow-hidden flex flex-col items-center justify-center">
                    <div className="w-16 h-16 rounded-full bg-slate-700 mb-2 border border-slate-600 flex items-center justify-center text-slate-400 text-xs">
                      {scenario === 'wrong_face' ? 'MISMATCH' : 'PHOTO'}
                    </div>
                    <div className="text-[9px] font-mono text-slate-500 uppercase">PORTRAIT ZONE</div>
                    {scenario === 'wrong_face' && (
                      <div className="absolute inset-0 bg-rose-500/20 border-2 border-rose-500 flex items-end p-1">
                        <span className="text-[9px] bg-rose-950 text-rose-300 font-bold px-1 rounded">MISMATCH</span>
                      </div>
                    )}
                  </div>

                  <div className="flex-1 space-y-2 text-xs">
                    <div>
                      <div className="text-[9px] text-slate-400 uppercase font-mono">Surname / Nom</div>
                      <div className="font-bold text-slate-100 font-mono">DOE</div>
                    </div>
                    <div>
                      <div className="text-[9px] text-slate-400 uppercase font-mono">Given Names / Prénoms</div>
                      <div className="font-bold text-slate-100 font-mono">JOHN</div>
                    </div>
                    <div className="flex justify-between">
                      <div>
                        <div className="text-[9px] text-slate-400 uppercase font-mono">Passport No</div>
                        <div className="font-bold text-cyan-400 font-mono">P12345678</div>
                      </div>
                      <div>
                        <div className="text-[9px] text-slate-400 uppercase font-mono">Sex</div>
                        <div className="font-bold text-slate-100 font-mono">M</div>
                      </div>
                    </div>
                    <div className="flex justify-between">
                      <div className="relative">
                        <div className="text-[9px] text-slate-400 uppercase font-mono">Date of Birth</div>
                        <div className={`font-bold font-mono ${isAlteredDOB ? 'text-rose-400 bg-rose-950/60 px-1 rounded border border-rose-500/60' : 'text-slate-100'}`}>
                          {isAlteredDOB ? '1995-05-12 (Altered)' : '1988-05-12'}
                        </div>
                      </div>
                      <div>
                        <div className="text-[9px] text-slate-400 uppercase font-mono">Date of Expiry</div>
                        <div className={`font-bold font-mono ${scenario === 'expired' ? 'text-amber-400 bg-amber-950/60 px-1 rounded border border-amber-500/60' : 'text-slate-100'}`}>
                          {scenario === 'expired' ? '2021-01-15 (EXPIRED)' : '2030-05-12'}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-950 p-2 rounded border border-slate-800 font-mono text-[11px] leading-tight text-emerald-400 tracking-widest select-all">
                  P&lt;UTODOE&lt;&lt;JOHN&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;<br />
                  P123456784UTO8805125M{scenario === 'expired' ? '2101150' : '3005123'}&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;02
                </div>
              </div>

              {showOverlays && isAlteredDOB && (
                <div className="absolute top-[180px] right-[100px] w-28 h-7 border-2 border-rose-500 bg-rose-500/20 rounded animate-pulse flex items-center justify-center">
                  <span className="text-[9px] font-bold bg-rose-950 text-rose-300 px-1 rounded shadow">
                    COPY-MOVE / TAMPERED
                  </span>
                </div>
              )}
            </div>
          )}

          {showHeatmap && (
            <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-rose-500/30 to-amber-500/20 mix-blend-color-dodge pointer-events-none flex items-center justify-center">
              <div className="text-xs bg-black/80 text-rose-300 font-mono px-3 py-1 rounded border border-rose-500/50">
                CNN Forensic Patch Heatmap (Active)
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quality Gate Status Footer */}
      <div className="h-10 px-4 bg-slate-900 border-t border-slate-800 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <span className="text-slate-400 font-medium">Quality Gate:</span>
          {qualityStatus === 'accept' && (
            <span className="flex items-center text-emerald-400 font-semibold">
              <CheckCircle className="w-3.5 h-3.5 mr-1" /> ACCEPT
            </span>
          )}
          {qualityStatus === 'recapture_required' && (
            <span className="flex items-center text-rose-400 font-semibold">
              <AlertTriangle className="w-3.5 h-3.5 mr-1" /> RECAPTURE REQUIRED
            </span>
          )}
        </div>
        {qualityDetails && (
          <div className="flex space-x-4 font-mono text-slate-400 text-[11px]">
            <span>Blur: {qualityDetails.blur_score?.toFixed(1)}</span>
            <span>Glare: {(qualityDetails.glare_ratio * 100)?.toFixed(1)}%</span>
            <span>Corners: {qualityDetails.corner_count}</span>
          </div>
        )}
      </div>
    </div>
  );
};
