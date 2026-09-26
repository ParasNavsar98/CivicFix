/**
 * TypeScript Type Definitions for CivicFix Testing Console
 */

export interface LocationData {
  lat?: number | null;
  long?: number | null;
  address?: string | null;
}

export interface Problem {
  problemId: string;
  submitterId: string;
  title: string;
  description: string;
  location?: LocationData | null;
  primaryDomain?: string | null;
  secondaryDomains: string[];
  subcategory?: string | null;
  status: string;
  severity?: string | null;
  urgency?: string | null;
  mediaRefs?: string[];
  governmentCaseRef?: string | null;
  universityMatches?: Record<string, any>[];
  projectRef?: string | null;
  publicSummary?: string | null;
  privacyClass: string;
  processingState: string;
  classificationState: string;
  duplicateDetectionState: string;
  reviewRequired: boolean;
  reviewReasons: string[];
  masterProblemId?: string | null;
  duplicateStatus?: string | null;
  currentProblemVersionId?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ProblemVersion {
  versionId: string;
  problemId: string;
  source: 'system' | 'ai' | 'reviewer' | string;
  title: string;
  description: string;
  primaryDomain?: string | null;
  secondaryDomains?: string[];
  subcategory?: string | null;
  severity?: string | null;
  urgency?: string | null;
  researchRequired?: boolean | null;
  governmentActionPossible?: boolean | null;
  requiredExpertise?: string[];
  requiredResources?: string[];
  publicSummary?: string | null;
  reasoning?: string | null;
  createdBy: string;
  createdAt: string;
  changeReason?: string | null;
}

export interface DuplicateCandidateRecord {
  recordId: string;
  problemId: string;
  candidateProblemId: string;
  duplicateScore: number;
  semanticSimilarity: number;
  primaryDomainMatch: boolean;
  subcategoryMatch: boolean;
  secondaryDomainOverlap: number;
  locationDistanceKm?: number | null;
  locationScore: number;
  thresholdUsed: number;
  status: string;
  reasons: string[];
  createdAt: string;
  updatedAt: string;
}

export interface ReviewActionRecord {
  reviewId: string;
  problemId: string;
  reviewerId: string;
  action: string;
  reason?: string | null;
  masterProblemId?: string | null;
  payload?: Record<string, any>;
  previousState: string;
  newState: string;
  createdAt: string;
}

export interface AuditEvent {
  eventId: string;
  entityType: string;
  entityId: string;
  actorId: string;
  actorRole: string;
  action: string;
  previousState?: string | null;
  newState?: string | null;
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface StandardApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  requestId?: string;
}

export interface ClassificationResult {
  problemSummary: string;
  primaryDomain: string;
  secondaryDomains: string[];
  subcategory: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  urgency: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  researchRequired: boolean;
  governmentActionPossible: boolean;
  requiredExpertise: string[];
  requiredResources: string[];
  confidence: number;
  reasoning: string;
}

export interface ClassificationResponse {
  problemId: string;
  status: 'classified' | 'review_required' | 'failed' | string;
  classification?: ClassificationResult | null;
  error?: {
    errorCode: string;
    message: string;
  } | null;
}

export interface CandidateMatch {
  candidateProblemId: string;
  duplicateScore: number;
  semanticSimilarity: number;
  primaryDomainMatch: boolean;
  subcategoryMatch: boolean;
  secondaryDomainOverlap: number;
  locationDistanceKm?: number | null;
  locationScore: number;
  candidateStatus: 'strong_candidate' | 'potential_duplicate' | 'no_candidate' | string;
  reasons: string[];
  signalStates?: Record<string, string>;
  scoreBreakdown?: Record<string, {
    rawValue?: number | null;
    state: string;
    weight: number;
    contribution?: number | null;
    used: boolean;
  }>;
  weights?: Record<string, number>;
  weightedContributions?: Record<string, number | null>;
  availableWeight?: number;
  normalizedCompositeScore?: number;
  decisionEvidence?: Record<string, any>;
  fingerprint?: Record<string, any>;
  scoringVersion?: string;
}

export interface DuplicateCheckResponse {
  problemId: string;
  status: 'candidate_found' | 'no_candidate' | string;
  duplicateCandidates: CandidateMatch[];
  scoringVersion?: string;
}

export interface ReviewerQueueItem {
  problem: Problem;
  activeVersion?: ProblemVersion | null;
  duplicateCandidates: DuplicateCandidateRecord[];
  versionHistoryCount: number;
}

export interface TimelineStep {
  step: string;
  status: string;
  timestamp: string;
  summary: string;
}

export interface ProblemTimelineData {
  problemId: string;
  title: string;
  currentStatus: string;
  timeline: TimelineStep[];
}

export interface HTTPInspectorData {
  method: string;
  url: string;
  headers?: Record<string, string>;
  requestBody?: any;
  statusCode?: number;
  durationMs?: number;
  responseBody?: any;
  error?: string;
  timestamp: string;
}

export type TestResultStatus = 'PASS' | 'FAIL' | 'WARNING' | 'NOT_RUN' | 'NOT_IMPLEMENTED';

export interface TestResultRecord {
  id: string;
  testName: string;
  timestamp: string;
  endpoint?: string;
  method?: string;
  request?: any;
  response?: any;
  statusCode?: number;
  durationMs?: number;
  expected?: string;
  actual?: string;
  status: TestResultStatus;
  notes?: string;
  problemId?: string;
}

export interface E2ESessionState {
  sessionId: string;
  startedAt: string;
  masterProblem?: Problem | null;
  duplicateProblem?: Problem | null;
  duplicateCheckResult?: DuplicateCheckResponse | null;
  reviewerActionData?: any;
  routingResult?: Problem | null;
  timelineData?: ProblemTimelineData | null;
  auditTrail?: AuditEvent[];
  currentStep: number;
  completedSteps: number[];
}
