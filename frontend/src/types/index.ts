// CivicFix Platform Types

export type UserRole = 'citizen' | 'government' | 'university' | 'industry';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  subRole?: string; // e.g. 'SPOC', 'Faculty', 'Officer', 'CSR'
  organization?: string;
  department?: string;
  universityId?: string;
  avatarUrl?: string;
}

export type DomainType =
  | 'Education'
  | 'Healthcare'
  | 'Agriculture'
  | 'Water Resources'
  | 'Sanitation'
  | 'Environment'
  | 'Energy'
  | 'Urban Infrastructure'
  | 'Accessibility'
  | 'Public Administration'
  | 'Rural Livelihoods'
  | 'Other';

export type SeverityLevel = 'NONE' | 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | 'UNKNOWN';
export type UrgencyLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';

export type WorkflowStage =
  | 'CAPTURE'
  | 'UNDERSTAND'
  | 'VALIDATE'
  | 'ROUTE'
  | 'MATCH'
  | 'COLLABORATE'
  | 'IMPLEMENT'
  | 'MEASURE';

export type ProblemStatus =
  | 'Submitted'
  | 'AI Processing'
  | 'Under Review'
  | 'Validated'
  | 'Routed Government'
  | 'Pending Match'
  | 'University Assigned'
  | 'In Progress'
  | 'Merged Duplicate'
  | 'Resolved'
  | 'Rejected';

export interface LocationInput {
  address?: string;
  district: string;
  state: string;
  latitude?: number;
  longitude?: number;
}

export interface ClassificationResult {
  primaryDomain: DomainType;
  subcategory: string;
  secondaryDomains: string[];
  severity: SeverityLevel;
  urgency?: UrgencyLevel;
  confidence: number;
  reasoning?: string;
  severityEvidence?: string[];
  requiredExpertise?: string[];
  requiredResources?: string[];
  researchRequired?: boolean;
  governmentActionPossible?: boolean;
}

export interface ClassificationResponse {
  problemId: string;
  status: 'high_confidence' | 'needs_review' | 'failed';
  classification?: ClassificationResult;
  error?: {
    errorCode: string;
    message: string;
  };
}

export interface SignalState {
  primaryDomain: 'MATCH' | 'MISMATCH' | 'UNKNOWN';
  subcategory: 'MATCH' | 'MISMATCH' | 'UNKNOWN';
  secondaryDomains: 'MATCH' | 'MISMATCH' | 'UNKNOWN';
  location: 'AVAILABLE' | 'UNAVAILABLE';
  fingerprint?: string;
}

export interface DuplicateCandidate {
  candidateProblemId: string;
  duplicateScore: number; // 0.0 - 1.0
  semanticSimilarity: number;
  primaryDomainMatch: boolean;
  subcategoryMatch: boolean;
  secondaryDomainOverlap: number;
  locationDistanceKm?: number;
  locationScore?: number;
  candidateStatus: 'strong_candidate' | 'potential_duplicate' | 'no_candidate';
  reasons: string[];
  signalStates?: SignalState;
  candidateTitle?: string;
  candidateDescription?: string;
}

export interface DuplicateCheckResponse {
  problemId: string;
  status: 'candidate_found' | 'no_candidate';
  duplicateCandidates: DuplicateCandidate[];
  scoringVersion?: string;
}

export interface FactorScores {
  expertise: number;
  faculty: number;
  infrastructure: number;
  pastProjects: number;
  geography: number;
  capacity: number;
  industry: number;
}

export interface UniversityMatchResult {
  universityId: string;
  universityName: string;
  finalScore: number; // 0 - 100
  rank?: number;
  factorScores: FactorScores;
  matchedExpertise: string[];
  unmatchedExpertise: string[];
  matchedFaculty: string[];
  matchedInfrastructure: string[];
  relevantPastProjects: string[];
  geographyReason: string;
  capacityReason: string;
  industryReason: string;
  explanation: string;
  weightsUsed?: Record<string, number>;
}

export interface MatchingResponse {
  problemId: string;
  topUniversities: UniversityMatchResult[];
  assignmentWarning?: string;
}

export type AssignmentStatus = 'PENDING' | 'SENT' | 'ACCEPTED' | 'REJECTED' | 'TIMED_OUT' | 'CANCELLED';

export interface UniversityAssignment {
  assignmentId: string;
  problemId: string;
  universityId: string;
  rank: number;
  status: AssignmentStatus;
  score: number;
  scoreSnapshot: FactorScores;
  explanation: string;
  sentAt?: string;
  deadline?: string;
  respondedAt?: string;
  rejectionReason?: string;
}

export interface SolutionItem {
  solutionId: string;
  problemId: string;
  projectId: string;
  universityId: string;
  universityName?: string;
  title: string;
  domain: string;
  subcategory: string;
  location: {
    state: string;
    district: string;
  };
  developmentStage: 'IDEA' | 'PROTOTYPE' | 'PILOT' | 'DEPLOYED';
  supportNeeded: string[];
  partnerType: string[];
  visibility: 'PUBLIC' | 'PRIVATE';
  status: 'PUBLISHED' | 'DRAFT';
  description?: string;
}

export interface IndustryInterest {
  interestId: string;
  solutionId: string;
  partnerId: string;
  partnerName?: string;
  supportOffered: string[];
  contribution: Record<string, any>;
  message: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
  createdAt: string;
  rejectionReason?: string;
}

export interface CollaborationItem {
  collaborationId: string;
  solutionId: string;
  partnerId: string;
  acceptedBy: string;
  supportDetails: {
    supportOffered: string[];
    contribution: Record<string, any>;
  };
  status: 'ACTIVE' | 'COMPLETED';
  createdAt: string;
}

export interface Problem {
  problemId: string;
  title: string;
  description: string;
  location: LocationInput;
  submittedAt: string;
  submitterId?: string;
  submitterName?: string;
  primaryDomain?: DomainType;
  subcategory?: string;
  secondaryDomains?: string[];
  severity?: SeverityLevel;
  urgency?: UrgencyLevel;
  confidence?: number;
  status: ProblemStatus;
  stage: WorkflowStage;
  aiClassification?: ClassificationResult;
  reviewRequired?: boolean;
  reviewReason?: string;
  masterProblemId?: string;
  evidenceFiles?: string[];
  assignedOfficer?: string;
  assignedDepartment?: string;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  type: 'info' | 'success' | 'warning' | 'error';
  link?: string;
}
