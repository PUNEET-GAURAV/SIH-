import React, { useState, useEffect } from 'react';
import { NavRail } from './components/NavRail';
import { Header } from './components/Header';
import { DocumentInspectionHero } from './components/DocumentInspectionHero';
import { StructuredFindings } from './components/StructuredFindings';
import { AdjudicationSuite } from './components/AdjudicationSuite';
import { UploadModal } from './components/UploadModal';
import { NavModal } from './components/NavModal';

import {
  DemoScenario, SessionDetailData, DecisionAction, AuditLogData
} from './types';

export const App: React.FC = () => {
  const [activeNav, setActiveNav] = useState<string>('verify');
  const [scenario, setScenario] = useState<DemoScenario>('altered_dob');
  const [sessionData, setSessionData] = useState<SessionDetailData | null>(null);
  const [auditTrail, setAuditTrail] = useState<AuditLogData[]>([]);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [isSubmittingDecision, setIsSubmittingDecision] = useState<boolean>(false);
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false);
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null);

  // Load deterministic demo scenario data
  const loadScenario = (sc: DemoScenario) => {
    setIsProcessing(true);
    setScenario(sc);
    setUploadedImageUrl(null);

    setTimeout(() => {
      const mockSession: SessionDetailData = {
        id: `session-${sc}-001`,
        officer_id: 'officer-01',
        status: sc === 'poor_capture' ? 'quality_failed' : 'completed',
        mock_mode: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        documents: [
          {
            id: `doc-${sc}`,
            original_filename: 'passport_scan.jpg',
            quality_status: sc === 'poor_capture' ? 'recapture_required' : 'accept',
            quality_details: {
              blur_score: 420.0,
              glare_ratio: 0.021,
              resolution: [1920, 1080],
              corner_count: 4,
              issues: [],
            },
            document_type: sc === 'unknown_document' ? 'unknown' : sc === 'expired' ? 'id_card_td1' : 'passport_td3',
            classification_confidence: 0.98,
            ocr_fields: [
              { field_name: 'surname', field_value: 'VANCE', confidence: 0.96 },
              { field_name: 'given_names', field_value: 'JULIAN STERLING', confidence: 0.95 },
              { field_name: 'document_number', field_value: 'PA8849201', confidence: 0.94 },
              { field_name: 'date_of_birth', field_value: '1987-08-14', confidence: 0.93 },
              { field_name: 'expiry_date', field_value: sc === 'altered_dob' ? '2029-11-24' : '2026-11-24', confidence: 0.92 },
            ],
            forensic_results: sc === 'altered_dob' ? [
              {
                detector_type: 'sift_copy_move',
                signal: 'copy_move_clusters',
                status: 'high',
                confidence: 0.91,
                reliability: 0.85,
                applicable: true,
                explanation: 'Localized DCT recompression signature detected around the expiry glyphs.',
              },
            ] : [],
          },
        ],
        assessment: {
          concern_level: sc === 'altered_dob' ? 'high_concern' : 'low_concern',
          recommendation: sc === 'altered_dob' ? 'secondary_inspection' : 'clear',
          summary: sc === 'altered_dob'
            ? 'HIGH CONCERN: VIZ Date 2029 contradicts MRZ Checksum 2026. Localized recompression signature detected.'
            : 'LOW CONCERN: All checksums valid and document fully consistent.',
          is_mock: true,
        },
      };

      setSessionData(mockSession);
      setIsProcessing(false);
    }, 300);
  };

  useEffect(() => {
    loadScenario('altered_dob');
  }, []);

  const handleSelectScenario = (sc: DemoScenario) => {
    loadScenario(sc);
  };

  const handleUploadSuccess = (newSession: SessionDetailData, imageUrl: string) => {
    setSessionData(newSession);
    setUploadedImageUrl(imageUrl);
    setIsUploadOpen(false);
  };

  const handleSubmitDecision = async (action: DecisionAction, notes: string) => {
    setIsSubmittingDecision(true);
    setTimeout(() => {
      if (sessionData) {
        setSessionData({
          ...sessionData,
          officer_decision: {
            id: `dec-${Date.now()}`,
            session_id: sessionData.id,
            decision: action,
            notes,
            created_at: new Date().toISOString(),
          },
        });
      }
      setIsSubmittingDecision(false);
    }, 400);
  };

  const doc = sessionData?.documents?.[0];

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="bg-[#f6f8fb] text-slate-950 font-sans antialiased min-h-screen">
      {/* 72px Fixed Enterprise Nav Rail (Desktop sidebar / Mobile bottom bar) */}
      <NavRail activeTab={activeNav} onSelectTab={setActiveNav} />

      {/* Navigation Modal overlay for Cases, Graph, Library, Audit, Settings */}
      <NavModal activeTab={activeNav} onClose={() => setActiveNav('verify')} />

      {/* Main Workspace Area with Responsive Mobile Offset */}
      <div className="pl-0 md:pl-[72px] pb-20 md:pb-0">
        {/* Top Header Bar */}
        <Header
          currentScenario={scenario}
          onSelectScenario={handleSelectScenario}
          isMockMode={sessionData?.mock_mode ?? true}
          isProcessing={isProcessing}
          onOpenUploadModal={() => setIsUploadOpen(true)}
        />

        {/* Mobile-Only Phone Segmented Pill Selector (Paytm / PhonePe Style) */}
        <div className="md:hidden sticky top-16 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200 px-3 py-2 flex items-center justify-center">
          <div className="flex items-center bg-slate-100 p-1 rounded-full border border-slate-200 text-xs w-full max-w-sm justify-between shadow-xs">
            <button
              onClick={() => scrollToSection('sec-doc')}
              className="px-3 py-1.5 rounded-full font-semibold text-slate-800 hover:bg-white transition-all cursor-pointer text-[11px] flex items-center gap-1 active:scale-95 shadow-xs"
            >
              📷 Document
            </button>
            <button
              onClick={() => scrollToSection('sec-findings')}
              className="px-3 py-1.5 rounded-full font-semibold text-slate-800 hover:bg-white transition-all cursor-pointer text-[11px] flex items-center gap-1 active:scale-95 shadow-xs"
            >
              🔍 Findings
            </button>
            <button
              onClick={() => scrollToSection('sec-adjudicate')}
              className="px-3 py-1.5 rounded-full font-semibold text-slate-800 hover:bg-white transition-all cursor-pointer text-[11px] flex items-center gap-1 active:scale-95 shadow-xs"
            >
              ⚡ Adjudicate
            </button>
          </div>
        </div>

        {/* Main Workspace Responsive Layout */}
        <main className="relative pt-4 sm:pt-20 w-full px-3 sm:px-8 pb-10 min-h-screen">
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-5 sm:gap-6 w-full max-w-[1680px] mx-auto">
            {/* LEFT / CENTER COLUMN: Document Inspection & Structured Findings (58% / 7 cols) */}
            <section className="xl:col-span-7 flex flex-col gap-5 sm:gap-6 min-w-0">
              <div id="sec-doc" className="scroll-mt-28">
                <DocumentInspectionHero
                  scenario={scenario}
                  uploadedImageUrl={uploadedImageUrl}
                  qualityDetails={doc?.quality_details}
                  ocrFields={doc?.ocr_fields}
                  forensicResults={doc?.forensic_results}
                />
              </div>

              <div id="sec-findings" className="scroll-mt-28">
                <StructuredFindings
                  scenario={scenario}
                  assessment={sessionData?.assessment}
                />
              </div>
            </section>

            {/* RIGHT COLUMN: Adjudication & Decision Suite (42% / 5 cols) */}
            <section id="sec-adjudicate" className="xl:col-span-5 flex flex-col gap-5 sm:gap-6 min-w-0 scroll-mt-28">
              <AdjudicationSuite
                assessment={sessionData?.assessment}
                decision={sessionData?.officer_decision}
                onSubmitDecision={handleSubmitDecision}
                isSubmitting={isSubmittingDecision}
              />
            </section>
          </div>
        </main>
      </div>

      {/* Upload Document Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
};
