// TypeScript type definitions for DocShield AI Officer Workbench

export type ConcernLevel = 'low_concern' | 'review_required' | 'high_concern';
export type Recommendation = 'clear' | 'request_recapture' | 'secondary_inspection' | 'escalate';
export type DecisionAction = 'clear' | 'secondary_inspection' | 'escalate' | 'request_recapture';

export type DemoScenario = 'genuine' | 'altered_dob' | 'expired' | 'wrong_face' | 'poor_capture' | 'unknown_document';

export interface QualityDetails {
  blur_score: number;
  glare_ratio: number;
  resolution: [number, number];
  corner_count: number;
  issues: string[];
}

export interface OCRFieldData {
  field_name: string;
  field_value: string;
  confidence: number;
  bbox?: [number, number, number, number];
  source?: string;
  is_mock?: boolean;
}

export interface MRZChecksumItem {
  field?: string;
  expected?: string;
  actual?: string;
  valid: boolean;
}

export interface MRZData {
  raw_mrz: string;
  parsed_fields?: {
    document_type?: string;
    country_code?: string;
    surname?: string;
    given_names?: string;
    document_number?: string;
    nationality?: string;
    date_of_birth?: string;
    sex?: string;
    expiry_date?: string;
    optional_data?: string;
    is_valid?: boolean;
    issues?: string[];
  };
  checksum_results?: Record<string, MRZChecksumItem>;
  overall_status?: string;
  is_mock?: boolean;
}

export interface TemplateResultData {
  template_id?: string;
  template_version?: string;
  alignment_score?: number;
  status?: string;
  deviations?: string[];
  is_mock?: boolean;
}

export interface ForensicResultData {
  detector_type: string;
  signal: string;
  status: string;
  confidence: number;
  reliability: number;
  applicable: boolean;
  region?: [number, number, number, number];
  explanation: string;
  details?: Record<string, any>;
  model_version?: string;
  is_mock?: boolean;
}

export interface FaceVerificationData {
  similarity_score: number;
  identity_status: string;
  face_quality?: Record<string, any>;
  pad_status?: string;
  pad_details?: Record<string, any>;
  explanation?: string;
  is_mock?: boolean;
}

export interface DimensionResultData {
  dimension: string;
  status: string;
  weighted_score: number;
  explanation: string;
  signal_count: number;
}

export interface ContradictionData {
  type: string;
  description: string;
  dimensions: string[];
}

export interface ScreeningAssessmentData {
  concern_level: ConcernLevel;
  recommendation: Recommendation;
  summary: string;
  dimension_results?: Record<string, DimensionResultData>;
  contradictions?: ContradictionData[];
  fusion_details?: Record<string, any>;
  is_mock?: boolean;
}

export interface AuditLogData {
  id: string;
  session_id: string;
  actor_id: string;
  event_type: string;
  payload_hash?: string;
  previous_hash?: string;
  entry_hash: string;
  timestamp: string;
}

export interface OfficerDecisionData {
  id: string;
  session_id: string;
  decision: DecisionAction;
  notes?: string;
  created_at: string;
}

export interface SessionDetailData {
  id: string;
  officer_id: string;
  status: string;
  pipeline_stage?: string;
  mock_mode: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
  documents?: {
    id: string;
    file_path?: string;
    original_filename?: string;
    quality_status: string;
    quality_details?: QualityDetails;
    document_type?: string;
    classification_confidence?: number;
    ocr_fields?: OCRFieldData[];
    mrz_result?: MRZData;
    template_result?: TemplateResultData;
    forensic_results?: ForensicResultData[];
  }[];
  face_verification?: FaceVerificationData;
  evidence?: any[];
  assessment?: ScreeningAssessmentData;
  officer_decision?: OfficerDecisionData;
}
