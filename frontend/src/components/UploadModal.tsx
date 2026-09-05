import React, { useState, useRef } from 'react';
import { Upload, X, FileImage, Camera, CheckCircle2, AlertCircle, Loader2, Sparkles, Video } from 'lucide-react';
import Webcam from 'react-webcam';
import { SessionDetailData } from '../types';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: (sessionData: SessionDetailData, uploadedImageUrl: string) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  onUploadSuccess,
}) => {
  const [docFile, setDocFile] = useState<File | null>(null);
  const [faceFile, setFaceFile] = useState<File | null>(null);
  const [docPreview, setDocPreview] = useState<string | null>(null);
  const [facePreview, setFacePreview] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isWebcamMode, setIsWebcamMode] = useState<'doc' | 'face' | null>(null);

  const docInputRef = useRef<HTMLInputElement>(null);
  const faceInputRef = useRef<HTMLInputElement>(null);
  const webcamRef = useRef<Webcam>(null);

  const capture = (type: 'doc' | 'face') => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      fetch(imageSrc)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], `${type}_capture.jpg`, { type: 'image/jpeg' });
          if (type === 'doc') {
            setDocFile(file);
            setDocPreview(URL.createObjectURL(file));
            setErrorMsg(null);
          } else {
            setFaceFile(file);
            setFacePreview(URL.createObjectURL(file));
          }
          setIsWebcamMode(null);
        });
    }
  };

  if (!isOpen) return null;

  const handleDocSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setErrorMsg('Please select a valid image file (.jpg, .png, .bmp, .tiff)');
      return;
    }
    setErrorMsg(null);
    setDocFile(file);
    setDocPreview(URL.createObjectURL(file));
  };

  const handleFaceSelect = (file: File) => {
    if (!file.type.startsWith('image/')) return;
    setFaceFile(file);
    setFacePreview(URL.createObjectURL(file));
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleDocSelect(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docFile) return;

    setIsProcessing(true);
    setErrorMsg(null);

    try {
      // Step 1: Create Screening Session
      setCurrentStep('1. Creating Screening Session...');
      const createRes = await fetch('/screening/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Demo-Officer': 'true',
        },
        body: JSON.stringify({ notes: 'User uploaded document screening' }),
      });
      const createData = await createRes.json();
      if (!createData.success) throw new Error(createData.error?.message || 'Failed to create session');
      const sessionId = createData.data.id;

      // Step 2: Upload Document File
      setCurrentStep('2. Uploading Document & Hashing (SHA-256)...');
      const formData = new FormData();
      formData.append('file', docFile);

      const uploadRes = await fetch(`/screening/${sessionId}/document`, {
        method: 'POST',
        headers: {
          'X-Demo-Officer': 'true',
        },
        body: formData,
      });
      const uploadData = await uploadRes.json();
      if (!uploadData.success) throw new Error(uploadData.error?.message || 'Failed to upload document');

      // Step 2.5: Upload Face File if provided
      if (faceFile) {
        setCurrentStep('2.5 Uploading Live Face Photo...');
        const faceFormData = new FormData();
        faceFormData.append('file', faceFile);

        const faceRes = await fetch(`/screening/${sessionId}/face`, {
          method: 'POST',
          headers: {
            'X-Demo-Officer': 'true',
          },
          body: faceFormData,
        });
        const faceData = await faceRes.json();
        if (!faceData.success) throw new Error(faceData.error?.message || 'Failed to upload live face photo');
      }

      // Step 3: Trigger Pipeline Processing
      setCurrentStep('3. Running AI Quality Gate, OCR, MRZ & Forensics Pipeline...');
      const processRes = await fetch(`/screening/${sessionId}/process`, {
        method: 'POST',
        headers: {
          'X-Demo-Officer': 'true',
        },
      });
      const processData = await processRes.json();
      if (!processData.success) throw new Error(processData.error?.message || 'Failed to start pipeline');

      // Step 4: Poll session status until completed
      setCurrentStep('4. Executing Evidence Fusion Engine...');
      let attempts = 0;
      let sessionResult: SessionDetailData | null = null;

      while (attempts < 300) {
        await new Promise((r) => setTimeout(r, 1000));
        attempts++;
        const getRes = await fetch(`/screening/${sessionId}`, {
          headers: {
            'X-Demo-Officer': 'true',
          },
        });
        const getData = await getRes.json();
        if (getData.success) {
          const status = getData.data.status;
          if (status === 'completed' || status === 'quality_failed' || status === 'error') {
            sessionResult = getData.data;
            break;
          }
        }
      }

      if (sessionResult && docPreview) {
        onUploadSuccess(sessionResult, docPreview);
        onClose();
      } else {
        throw new Error('Pipeline processing timed out or encountered an error.');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred during screening submission.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="px-6 py-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Upload Your Document for AI Screening</h2>
              <p className="text-xs text-slate-400">Select or drop any document image (Passport, ID Card, Driver License)</p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content / Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6 flex-1 overflow-y-auto">
          {errorMsg && (
            <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-500/50 text-rose-300 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Primary Document Dropzone */}
          <div>
            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-2 flex justify-between items-center">
              <span>1. Document Front Image <span className="text-cyan-400">* Required</span></span>
              {!isWebcamMode && (
                <button type="button" onClick={() => setIsWebcamMode('doc')} className="flex items-center space-x-1 text-cyan-400 bg-cyan-400/10 hover:bg-cyan-400/20 px-2 py-1 rounded text-[10px]">
                  <Video className="w-3 h-3" />
                  <span>Scan via Camera</span>
                </button>
              )}
            </label>

            {isWebcamMode === 'doc' ? (
              <div className="flex flex-col items-center border-2 border-slate-700 bg-black rounded-xl overflow-hidden relative min-h-[180px]">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full h-full object-cover"
                />
                <div className="absolute bottom-3 flex space-x-3">
                  <button type="button" onClick={() => setIsWebcamMode(null)} className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-lg">Cancel</button>
                  <button type="button" onClick={() => capture('doc')} className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-lg text-xs font-bold shadow-lg shadow-cyan-600/50">Capture</button>
                </div>
              </div>
            ) : (

            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => docInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition flex flex-col items-center justify-center min-h-[180px] ${
                docPreview
                  ? 'border-cyan-500/60 bg-cyan-950/10'
                  : 'border-slate-700 bg-slate-950/60 hover:border-slate-500 hover:bg-slate-950'
              }`}
            >
              <input
                ref={docInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && handleDocSelect(e.target.files[0])}
              />

              {docPreview ? (
                <div className="flex flex-col items-center space-y-3">
                  <img
                    src={docPreview}
                    alt="Document Preview"
                    className="max-h-36 rounded-lg border border-slate-700 shadow-md object-contain"
                  />
                  <div className="flex items-center space-x-2 text-xs font-medium text-cyan-300">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>{docFile?.name} ({(docFile!.size / 1024 / 1024).toFixed(2)} MB)</span>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center space-y-2">
                  <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 mb-1">
                    <Upload className="w-6 h-6 text-cyan-400" />
                  </div>
                  <span className="text-sm font-semibold text-slate-200">
                    Click to browse or Drag & Drop Document Image
                  </span>
                  <span className="text-xs text-slate-500">
                    Supports JPG, PNG, BMP, TIFF (up to 20MB)
                  </span>
                </div>
              )}
            </div>
            )}
          </div>

          {/* Optional Live Face Photo Dropzone */}
          <div>
            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-2 flex justify-between items-center">
              <span>2. Live Facial Capture Photo <span className="text-slate-500">(Optional)</span></span>
              {!isWebcamMode && (
                <button type="button" onClick={() => setIsWebcamMode('face')} className="flex items-center space-x-1 text-cyan-400 bg-cyan-400/10 hover:bg-cyan-400/20 px-2 py-1 rounded text-[10px]">
                  <Video className="w-3 h-3" />
                  <span>Use Webcam</span>
                </button>
              )}
            </label>

            {isWebcamMode === 'face' ? (
              <div className="flex flex-col items-center border-2 border-slate-700 bg-black rounded-xl overflow-hidden relative min-h-[180px]">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full h-full object-cover"
                />
                <div className="absolute bottom-3 flex space-x-3">
                  <button type="button" onClick={() => setIsWebcamMode(null)} className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-lg">Cancel</button>
                  <button type="button" onClick={() => capture('face')} className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-lg text-xs font-bold shadow-lg shadow-cyan-600/50">Capture</button>
                </div>
              </div>
            ) : (

            <div
              onClick={() => faceInputRef.current?.click()}
              className={`border border-slate-800 rounded-xl p-3.5 cursor-pointer hover:border-slate-700 bg-slate-950/60 flex items-center justify-between transition ${
                facePreview ? 'border-cyan-500/50 bg-cyan-950/20' : ''
              }`}
            >
              <input
                ref={faceInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && handleFaceSelect(e.target.files[0])}
              />

              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-slate-800 text-slate-300">
                  <Camera className="w-4 h-4 text-cyan-400" />
                </div>
                <div>
                  <span className="text-xs font-semibold text-slate-200 block">
                    {faceFile ? faceFile.name : 'Select Live Face Portrait Photo'}
                  </span>
                  <span className="text-[11px] text-slate-500">
                    Compares live face against document photo (ArcFace similarity)
                  </span>
                </div>
              </div>

              {facePreview && (
                <img src={facePreview} alt="Face Preview" className="w-10 h-10 rounded-full object-cover border border-cyan-500" />
              )}
            </div>
            )}
          </div>

          {/* Processing Status Banner */}
          {isProcessing && (
            <div className="p-4 rounded-xl bg-cyan-950/50 border border-cyan-500/40 text-cyan-300 text-xs flex items-center space-x-3 animate-pulse">
              <Loader2 className="w-5 h-5 animate-spin text-cyan-400 shrink-0" />
              <div>
                <span className="font-bold block">Processing Document through AI Pipeline...</span>
                <span className="text-cyan-200/80 font-mono text-[11px]">{currentStep}</span>
              </div>
            </div>
          )}

          {/* Submit Action */}
          <div className="flex justify-end space-x-3 pt-2 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              disabled={isProcessing}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!docFile || isProcessing}
              className={`px-5 py-2.5 rounded-xl text-xs font-bold transition flex items-center space-x-2 ${
                docFile && !isProcessing
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-600/30'
                  : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
              }`}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>ANALYZING...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>UPLOAD & PROCESS DOCUMENT</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
