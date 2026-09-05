import React, { useState } from 'react';
import { Upload, ChevronDown, ShieldCheck } from 'lucide-react';
import { DemoScenario } from '../types';

interface HeaderProps {
  currentScenario: DemoScenario;
  onSelectScenario: (scenario: DemoScenario) => void;
  isMockMode: boolean;
  isProcessing: boolean;
  onOpenUploadModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentScenario,
  onSelectScenario,
  isMockMode,
  isProcessing,
  onOpenUploadModal,
}) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const scenarios: { id: DemoScenario; label: string; color: string }[] = [
    { id: 'altered_dob', label: 'Suspected Tampering (Specimen #4489)', color: 'bg-amber-500' },
    { id: 'genuine', label: 'Genuine Passport (Specimen #1024)', color: 'bg-emerald-500' },
    { id: 'expired', label: 'Expired ID Card (Specimen #8820)', color: 'bg-rose-500' },
    { id: 'wrong_face', label: 'Face Mismatch (Specimen #3319)', color: 'bg-purple-500' },
    { id: 'poor_capture', label: 'Poor Quality Scan (Specimen #7721)', color: 'bg-slate-400' },
    { id: 'unknown_document', label: 'Unknown Document (Specimen #9900)', color: 'bg-indigo-500' },
  ];

  const currentObj = scenarios.find((s) => s.id === currentScenario) || scenarios[0];

  return (
    <header className="fixed top-0 left-0 md:left-[72px] right-0 h-16 bg-white/95 backdrop-blur-md border-b border-slate-200 z-40 flex items-center justify-between px-3 md:px-8 select-none">
      {/* Left: Logo & Context */}
      <div className="flex items-center gap-2 md:gap-4">
        <div className="flex items-center gap-1.5 md:gap-2.5">
          <span className="text-lg md:text-xl font-bold tracking-tight text-slate-950 flex items-center gap-1">
            DocShield <span className="text-[#00d084] font-extrabold text-2xl leading-none">.</span>
          </span>
          <span className="hidden xs:inline-block text-[10px] md:text-[11px] font-semibold uppercase tracking-wider px-1.5 md:px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200/80">
            SIH26188
          </span>
        </div>

        <div className="h-4 w-[1px] bg-slate-200 mx-1 hidden sm:block" />

        <div className="hidden lg:flex items-center gap-2 text-slate-500 text-xs font-medium">
          <span className="text-slate-900 font-semibold">Government & Enterprise Specimen Screening</span>
          <span className="text-slate-400">•</span>
          <span>Inspection Rail A-04</span>
        </div>
      </div>

      {/* Center: Scenario Presets Dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          disabled={isProcessing}
          className="flex items-center gap-1.5 md:gap-2 bg-slate-50 border border-slate-200 rounded-full py-1.5 px-2.5 md:px-3.5 text-[11px] md:text-xs text-slate-700 shadow-sm hover:border-slate-300 cursor-pointer transition-colors"
        >
          <span className="hidden sm:inline text-slate-400 font-medium">Scenario:</span>
          <span className="font-semibold text-slate-900 flex items-center gap-1 md:gap-1.5 truncate max-w-[140px] sm:max-w-none">
            <span className={`w-2 h-2 rounded-full ${currentObj.color}`} />
            {currentObj.label.split('(')[0]}
          </span>
          <ChevronDown className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        </button>

        {isDropdownOpen && (
          <div className="absolute top-full mt-2 right-0 sm:left-0 w-72 sm:w-80 bg-white border border-slate-200 rounded-2xl shadow-xl z-50 p-2 space-y-1">
            <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Select Demo Scenario
            </div>
            {scenarios.map((sc) => (
              <button
                key={sc.id}
                onClick={() => {
                  onSelectScenario(sc.id);
                  setIsDropdownOpen(false);
                }}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition cursor-pointer ${
                  currentScenario === sc.id
                    ? 'bg-slate-900 text-white font-semibold'
                    : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${sc.color}`} />
                  <span>{sc.label}</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Right: Security Badge & Action Buttons */}
      <div className="flex items-center gap-2 md:gap-3">
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-[#00d084]" />
          <span>Air-Gapped & Secure</span>
        </div>

        <button className="hidden xl:block px-3.5 py-1.5 rounded-lg border border-slate-200 text-slate-700 font-medium text-xs hover:bg-slate-50 hover:text-slate-900 transition-colors cursor-pointer">
          Batch Queue (12)
        </button>

        {/* Jumio Signature High-Contrast CTA button */}
        <button
          onClick={onOpenUploadModal}
          className="px-3 md:px-4 py-1.5 md:py-2 rounded-full bg-slate-950 text-white hover:bg-slate-800 font-semibold text-xs tracking-tight transition-all flex items-center gap-1.5 md:gap-2 shadow-sm cursor-pointer active:scale-95"
        >
          <Upload className="w-3.5 h-3.5 text-[#00d084]" />
          <span className="hidden sm:inline">Upload New Document</span>
          <span className="sm:hidden">Upload</span>
        </button>
      </div>
    </header>
  );
};
