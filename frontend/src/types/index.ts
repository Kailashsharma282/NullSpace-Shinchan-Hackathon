export interface RequirementNode {
  id: string;
  research_id: string;
  key: string;
  name: string;
  description: string;
  mandatory: boolean;
  importance: number;
  order_index: number;
}

export interface SourceDocument {
  id: string;
  research_id: string;
  url: string;
  domain: string;
  title: string;
  content_hash: string;
  published_date?: string | null;
  retrieved_at: string;
  status: 'ingested' | 'failed' | 'pending';
  error_message?: string | null;
  is_fixture: boolean;
  text_length?: number;
  raw_text?: string;
}

export interface ExtractedClaim {
  id: string;
  research_id: string;
  source_id: string;
  requirement_id?: string | null;
  claim_text: string;
  exact_quote: string;
  char_start: number;
  char_end: number;
  is_grounded: boolean;
  confidence: number;
  extraction_method: string;
  source_title?: string | null;
  source_url?: string | null;
  source_domain?: string | null;
  published_date?: string | null;
}

export interface ConflictRecord {
  id: string;
  research_id: string;
  requirement_id: string;
  requirement_name?: string | null;
  claim_a_id: string;
  claim_b_id: string;
  claim_a?: ExtractedClaim | null;
  claim_b?: ExtractedClaim | null;
  relationship_type: 'contradiction' | 'agreement' | 'neutral' | 'uncertain';
  confidence: number;
  explanation: string;
  status: 'confirmed' | 'resolved' | 'false_positive' | 'requires_review';
  user_notes?: string | null;
}

export interface TemporalAudit {
  id: string;
  research_id: string;
  source_id: string;
  source_title?: string | null;
  source_url?: string | null;
  detected_years: string[];
  detected_cycles: string[];
  calendar_deadlines: string[];
  temporal_status: 'current' | 'potentially_outdated' | 'outdated' | 'date_unknown' | 'conflicting';
  staleness_reason?: string | null;
  published_date?: string | null;
}

export interface ChecklistItem {
  id: string;
  research_id: string;
  requirement_id: string;
  requirement_name?: string | null;
  priority_score: number;
  risk_category: 'Critical' | 'High' | 'Medium' | 'Low';
  entropy: number;
  title: string;
  reason: string;
  recommended_action: string;
  search_dork: string;
  is_resolved: boolean;
}

export interface EpistemicMatrixItem {
  requirement_id: string;
  requirement_name: string;
  mandatory: boolean;
  importance: number;
  status: 'verified' | 'conflict' | 'stale' | 'dark_spot' | 'review_required';
  mapped_claims_count: number;
  has_conflict: boolean;
  has_temporal_issue: boolean;
  is_dark_spot: boolean;
  claims: ExtractedClaim[];
  recommended_dork?: string | null;
}

export interface DashboardKPIs {
  total_requirements: number;
  evidence_coverage_pct: number;
  dark_spots_count: number;
  detected_conflicts_count: number;
  stale_claims_count: number;
  overall_risk_score: number;
}

export interface AnalysisResults {
  research_id: string;
  kpis: DashboardKPIs;
  matrix: EpistemicMatrixItem[];
  dark_spots: EpistemicMatrixItem[];
  conflicts: ConflictRecord[];
  temporal_audits: TemporalAudit[];
  checklist: ChecklistItem[];
}

export interface ResearchProject {
  id: string;
  title: string;
  domain: string;
  objective: string;
  created_at: string;
  updated_at: string;
  requirements_count?: number;
  sources_count?: number;
  requirements?: RequirementNode[];
  sources?: SourceDocument[];
}

