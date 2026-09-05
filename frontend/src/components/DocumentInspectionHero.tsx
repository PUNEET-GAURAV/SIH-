import React, { useState } from 'react';
import {
  CheckCircle2, AlertTriangle, Search, ZoomIn, ZoomOut, Maximize2, ChevronDown, Check, Globe
} from 'lucide-react';
import { DemoScenario, QualityDetails, OCRFieldData, ForensicResultData } from '../types';

interface DocumentInspectionHeroProps {
  scenario: DemoScenario;
  uploadedImageUrl?: string | null;
  qualityDetails?: QualityDetails;
  ocrFields?: OCRFieldData[];
  forensicResults?: ForensicResultData[];
}

export const DocumentInspectionHero: React.FC<DocumentInspectionHeroProps> = ({
  scenario,
  uploadedImageUrl,
  qualityDetails,
  ocrFields = [],
  forensicResults = [],
}) => {
  const [viewMode, setViewMode] = useState<'standard' | 'enhanced' | 'forensic'>('forensic');
  const [showTelemetryModal, setShowTelemetryModal] = useState(false);
  const [zoomScale, setZoomScale] = useState<number>(1.0);

  const isAltered = scenario === 'altered_dob' || forensicResults.some((f) => f.status === 'high');

  const handleZoomIn = () => setZoomScale((prev) => Math.min(prev + 0.25, 2.5));
  const handleZoomOut = () => setZoomScale((prev) => Math.max(prev - 0.25, 0.75));
  const handleResetZoom = () => setZoomScale(1.0);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-4 sm:p-6 flex flex-col gap-4 sm:gap-5 select-none transition-all">
      {/* Meta Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-sm sm:text-base font-bold text-slate-950 tracking-tight">Passport Inspection</span>
            <span className="text-[10px] sm:text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
              SPECIMEN #4489
            </span>
          </div>

          {/* Verification Pill Badges */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="inline-flex items-center gap-1 text-[10px] sm:text-[11px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 sm:px-2.5 py-0.5 rounded-full">
              <CheckCircle2 className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-emerald-600" />
              ICAO 9303
            </span>
            <span className="inline-flex items-center gap-1 text-[10px] sm:text-[11px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 sm:px-2.5 py-0.5 rounded-full">
              <CheckCircle2 className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-emerald-600" />
              Liveness: Passed
            </span>
            <span className="inline-flex items-center gap-1 text-[10px] sm:text-[11px] font-semibold text-slate-700 bg-slate-100 border border-slate-200 px-2 sm:px-2.5 py-0.5 rounded-full">
              <Search className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-slate-500" />
              Substrate: Inspected
            </span>
          </div>
        </div>

        {/* View Mode & Zoom Controls */}
        <div className="flex items-center justify-between w-full sm:w-auto gap-2">
          <div className="flex items-center bg-slate-100 p-1 rounded-full border border-slate-200/80 text-xs overflow-x-auto">
            <button
              onClick={() => setViewMode('standard')}
              className={`px-2.5 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-medium transition-all cursor-pointer whitespace-nowrap active:scale-95 ${
                viewMode === 'standard'
                  ? 'bg-white text-slate-950 shadow-sm border border-slate-200 font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Standard
            </button>
            <button
              onClick={() => setViewMode('enhanced')}
              className={`px-2.5 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-medium transition-all cursor-pointer whitespace-nowrap active:scale-95 ${
                viewMode === 'enhanced'
                  ? 'bg-white text-slate-950 shadow-sm border border-slate-200 font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Enhanced UV
            </button>
            <button
              onClick={() => setViewMode('forensic')}
              className={`px-2.5 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer whitespace-nowrap active:scale-95 ${
                viewMode === 'forensic'
                  ? 'bg-white text-slate-950 shadow-sm border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
              <span>Forensic</span>
            </button>
          </div>

          <div className="flex items-center bg-slate-100 rounded-lg p-0.5 border border-slate-200 text-slate-600 shrink-0">
            <button
              onClick={handleZoomIn}
              className="w-8 h-8 flex items-center justify-center rounded hover:bg-white hover:text-slate-900 active:scale-90 transition-all cursor-pointer"
              title="Zoom in (+25%)"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={handleZoomOut}
              className="w-8 h-8 flex items-center justify-center rounded hover:bg-white hover:text-slate-900 active:scale-90 transition-all cursor-pointer"
              title="Zoom out (-25%)"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={handleResetZoom}
              className="w-8 h-8 flex items-center justify-center rounded hover:bg-white hover:text-slate-900 active:scale-90 transition-all cursor-pointer"
              title="Reset Zoom (100%)"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Realistic Passport Inspection Stage */}
      <div className="relative w-full bg-[#eef2f6] rounded-xl p-6 flex items-center justify-center overflow-hidden border border-slate-200 min-h-[410px]">
        {/* Optical Scanner Calibrated Marks */}
        <div className="absolute top-3 left-4 font-mono text-[11px] text-slate-400 select-none flex items-center gap-2">
          <span className="inline-block w-2 h-2 border border-slate-400" />
          SPEC-ARC-9042 // HIGH-RES SCANNER #02
        </div>
        <div className="absolute top-3 right-4 font-mono text-[11px] text-slate-400 select-none">
          600 DPI • CALIBRATED OPTICAL SENSOR
        </div>

        {/* Passport Biometric Booklet Canvas */}
        <div
          style={{ transform: `scale(${zoomScale})`, transformOrigin: 'center center' }}
          className={`relative w-full max-w-[650px] bg-[#fcfcfc] rounded-lg border border-slate-300 shadow-lg p-3 sm:p-5 flex flex-col justify-between select-none transition-all duration-300 ${
            viewMode === 'enhanced'
              ? 'contrast-125 saturate-110 brightness-105'
              : viewMode === 'forensic'
              ? 'contrast-105'
              : ''
          }`}
        >
          {zoomScale !== 1.0 && (
            <div className="absolute top-2 right-2 bg-slate-900/90 text-white text-[10px] font-mono px-2 py-0.5 rounded-full z-40">
              {(zoomScale * 100).toFixed(0)}%
            </div>
          )}
          {/* Microprint Security Border */}
          <div className="absolute inset-1.5 border border-slate-200/60 rounded pointer-events-none" />

          {/* Passport Header Band */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-200 bg-slate-50/70 -m-5 mb-3 px-5 pt-4 rounded-t-lg">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-slate-900 flex items-center justify-center text-white shadow-xs">
                <Globe className="w-5 h-5 text-[#00d084]" />
              </div>
              <div className="flex flex-col">
                <span className="text-xs uppercase tracking-wider text-slate-900 font-bold">Republic of Arcasia</span>
                <span className="text-[10px] tracking-wide text-slate-500 font-medium">PASSPORT • PASSEPORT • TYPE P</span>
              </div>
            </div>
            <div className="text-right">
              <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">Document No.</span>
              <span className="font-mono text-base text-slate-950 font-bold tracking-wider">PA8849201</span>
            </div>
          </div>

          {/* Main Biometric Zone: Photo & Metadata */}
          <div className="grid grid-cols-12 gap-5 mt-2 items-start">
            {/* Left Portrait & Signature */}
            <div className="col-span-4 flex flex-col gap-2">
              <div className="relative w-full aspect-[3/4] bg-slate-200 rounded border border-slate-300 overflow-hidden shadow-inner flex items-center justify-center group">
                <img
                  src={uploadedImageUrl || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80'}
                  alt="Specimen Biometric Photo"
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-tr from-emerald-500/10 via-transparent to-indigo-500/10 pointer-events-none" />
                <div className="absolute bottom-1.5 right-1.5 bg-slate-950/80 backdrop-blur-xs text-white px-1.5 py-0.5 rounded text-[9px] font-mono font-medium flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#00d084]" />
                  ICAO-BIO-99
                </div>
              </div>
              <div className="flex flex-col text-center pt-0.5">
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold">Bearer's Signature</span>
                <div className="h-6 flex items-center justify-center font-serif italic text-sm text-slate-800 select-none opacity-85">
                  J. S. Vance
                </div>
              </div>
            </div>

            {/* Right VIZ Identity Metadata */}
            <div className="col-span-8 grid grid-cols-2 gap-y-2 gap-x-4 text-left">
              <div className="col-span-2">
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">Surname / Nom</span>
                <span className="font-mono text-sm text-slate-900 font-bold">VANCE</span>
              </div>
              <div className="col-span-2">
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">Given Names / Prénoms</span>
                <span className="font-mono text-sm text-slate-900 font-bold">JULIAN STERLING</span>
              </div>
              <div>
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">Nationality / Nationalité</span>
                <span className="font-mono text-xs text-slate-800 font-medium">ARCASIAN</span>
              </div>
              <div>
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">Date of Birth / Date de naiss.</span>
                <span className="font-mono text-xs text-slate-800 font-medium">14 AUG 1987</span>
              </div>
              <div>
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">Sex / Sexe</span>
                <span className="font-mono text-xs text-slate-800 font-medium">M</span>
              </div>
              <div>
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">Place of Birth / Lieu de naiss.</span>
                <span className="font-mono text-xs text-slate-800 font-medium">VALIS, ARC</span>
              </div>
              <div>
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">Date of Issue / Date d'émission</span>
                <span className="font-mono text-xs text-slate-800 font-medium">25 NOV 2016</span>
              </div>

              {/* CRITICAL EXPIRY FIELD WITH FORENSIC HIGHLIGHT */}
              <div className="relative group">
                <div className="flex items-center justify-between">
                  <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">Date of Expiry / Date d'exp.</span>
                  {viewMode === 'forensic' && isAltered && (
                    <span className="w-2 h-2 rounded-full bg-rose-500 inline-block animate-pulse" />
                  )}
                </div>

                <div
                  className={`p-1 rounded transition-all flex items-center justify-between ${
                    viewMode === 'forensic' && isAltered
                      ? 'bg-rose-50 border border-rose-300'
                      : 'bg-transparent border-transparent'
                  }`}
                >
                  <span className="font-mono text-xs text-slate-900 font-bold tracking-wide">
                    {isAltered ? '24 NOV 2029' : '24 NOV 2026'}
                  </span>
                  {viewMode === 'forensic' && isAltered && (
                    <span className="text-[9px] font-bold text-rose-700 uppercase bg-rose-100 px-1 rounded">
                      Mismatch
                    </span>
                  )}
                </div>

                {/* Forensic Tooltip */}
                {viewMode === 'forensic' && isAltered && (
                  <div className="absolute -top-11 -left-2 z-30 bg-slate-900 text-white px-2.5 py-1 rounded-md shadow-xl border border-slate-700 flex items-center gap-1.5 whitespace-nowrap animate-fadeIn">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                    <span className="text-[11px] font-medium">VIZ Date '2029' contradicts MRZ Checksum '2026'</span>
                  </div>
                )}
              </div>

              <div className="col-span-2 pt-1 border-t border-slate-100">
                <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">Authority / Autorité</span>
                <span className="font-mono text-xs text-slate-800 font-medium">PASSPORT OFFICE • VALIS CAPITOL</span>
              </div>
            </div>
          </div>

          {/* Machine Readable Zone (MRZ) */}
          <div className="mt-4 pt-2.5 pb-2 bg-slate-100/90 border border-slate-200 px-3 rounded font-mono text-xs tracking-[0.24em] leading-relaxed text-slate-900 select-text overflow-hidden">
            <div className="truncate">P&lt;ARCVANCE&lt;&lt;JULIAN&lt;STERLING&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;</div>
            <div className="truncate flex items-center">
              <span>PA88492018ARC8708149M</span>
              <span className="bg-rose-200 text-rose-900 px-1 rounded font-bold border border-rose-300">261124</span>
              <span>8&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;44</span>
            </div>
          </div>
        </div>
      </div>

      {/* Optical Telemetry Divider Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-1 text-xs text-slate-500 border-t border-slate-100">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-1.5 font-medium text-slate-900">
            <span className="w-2 h-2 rounded-full bg-[#00d084]" />
            <span>Optical Quality: <strong className="text-slate-950 font-bold">96/100</strong></span>
          </div>
          <span className="text-slate-300">|</span>
          <span>Resolution: <strong className="text-slate-700">600 DPI</strong></span>
          <span className="text-slate-300">|</span>
          <span>Glare: <strong className="text-slate-700">2.1%</strong> (Passed)</span>
          <span className="text-slate-300">|</span>
          <span>Perspective Skew: <strong className="text-slate-700">0.2°</strong></span>
          <span className="text-slate-300">|</span>
          <span>Substrate Noise: <strong className="text-slate-700">Minimal</strong></span>
        </div>

        <button
          onClick={() => setShowTelemetryModal(!showTelemetryModal)}
          className="text-xs font-semibold text-slate-900 hover:text-[#00d084] transition-colors flex items-center gap-1 cursor-pointer"
        >
          <span>View Full Telemetry</span>
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>

      {/* Collapsible Raw Metadata Tray */}
      {showTelemetryModal && (
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl font-mono text-xs text-slate-600 grid grid-cols-2 md:grid-cols-4 gap-3 animate-fadeIn">
          <div><span className="text-[10px] uppercase text-slate-400 font-semibold block">Sensor ICC Profile</span> AdobeRGB (1998)</div>
          <div><span className="text-[10px] uppercase text-slate-400 font-semibold block">Exposure Time</span> 1/120s @ f/5.6</div>
          <div><span className="text-[10px] uppercase text-slate-400 font-semibold block">Optical Color Space</span> Calibrated sRGB D65</div>
          <div><span className="text-[10px] uppercase text-slate-400 font-semibold block">Hardware Hash</span> SHA256-e9b41a...</div>
        </div>
      )}
    </div>
  );
};
