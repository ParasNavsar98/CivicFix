import {
  Problem,
  ClassificationResponse,
  DuplicateCheckResponse,
  MatchingResponse,
  UniversityMatchResult,
  UniversityAssignment,
  SolutionItem,
  IndustryInterest,
  CollaborationItem,
} from '../types';
import {
  INITIAL_PROBLEMS,
  INITIAL_MATCHES,
  INITIAL_ASSIGNMENTS,
  INITIAL_SOLUTIONS,
  INITIAL_INTERESTS,
  INITIAL_COLLABORATIONS,
} from './mockData';

const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

// In-Memory state store for live UI responsiveness during development
let localProblems: Problem[] = [...INITIAL_PROBLEMS];
let localMatches: Record<string, UniversityMatchResult[]> = { ...INITIAL_MATCHES };
let localAssignments: UniversityAssignment[] = [...INITIAL_ASSIGNMENTS];
let localSolutions: SolutionItem[] = [...INITIAL_SOLUTIONS];
let localInterests: IndustryInterest[] = [...INITIAL_INTERESTS];
let localCollaborations: CollaborationItem[] = [...INITIAL_COLLABORATIONS];

export const api = {
  // --- HEALTH CHECK ---
  async checkHealth(): Promise<{ status: string; service?: string }> {
    try {
      const res = await fetch(`${BASE_URL}/health`);
      if (res.ok) return await res.json();
    } catch (err) {
      console.warn('FastAPI backend health check failed, using fallback mode:', err);
    }
    return { status: 'fallback', service: 'civicfix-local-store' };
  },

  // --- PROBLEMS ---
  async getProblems(): Promise<Problem[]> {
    return localProblems;
  },

  async getProblemById(id: string): Promise<Problem | undefined> {
    return localProblems.find((p) => p.problemId === id);
  },

  async submitProblem(data: {
    title: string;
    description: string;
    location: { district: string; state: string; address?: string; latitude?: number; longitude?: number };
    evidenceFiles?: string[];
  }): Promise<Problem> {
    const newId = `CF-2026-${Math.floor(100 + Math.random() * 900)}`;

    let classification: any = undefined;
    let confidence = 0.85;
    let status: Problem['status'] = 'AI Processing';
    let reviewRequired = false;
    let reviewReason = undefined;

    try {
      const res = await fetch(`${BASE_URL}/api/v1/classify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problemId: newId,
          title: data.title,
          description: data.description,
          location: data.location,
        }),
      });

      if (res.ok) {
        const json: ClassificationResponse = await res.json();
        if (json.classification) {
          classification = json.classification;
          confidence = classification.confidence;
          if (json.status === 'needs_review' || confidence < 0.85) {
            reviewRequired = true;
            reviewReason = 'Confidence < 0.85 or vague phrasing detected by AI';
            status = 'Under Review';
          } else {
            status = 'Validated';
          }
        }
      }
    } catch (e) {
      console.info('Using local classification fallback for submitProblem');
    }

    if (!classification) {
      const titleLower = data.title.toLowerCase() + ' ' + data.description.toLowerCase();
      let primaryDomain: any = 'Urban Infrastructure';
      let subcategory = 'Roads';
      let secondaryDomains: string[] = [];

      if (titleLower.includes('toilet') || titleLower.includes('sewage') || titleLower.includes('waste') || titleLower.includes('garbage')) {
        primaryDomain = 'Sanitation';
        subcategory = titleLower.includes('toilet') ? 'Toilets' : 'Waste';
        if (titleLower.includes('school') || titleLower.includes('student')) secondaryDomains.push('Education');
      } else if (titleLower.includes('water') || titleLower.includes('leak') || titleLower.includes('pond')) {
        primaryDomain = 'Water Resources';
        subcategory = 'Supply';
        if (titleLower.includes('health') || titleLower.includes('disease')) secondaryDomains.push('Healthcare');
      } else if (titleLower.includes('solar') || titleLower.includes('light') || titleLower.includes('electric')) {
        primaryDomain = 'Energy';
        subcategory = 'Renewable Energy';
      }

      classification = {
        primaryDomain,
        subcategory,
        secondaryDomains,
        severity: 'HIGH',
        urgency: 'HIGH',
        confidence: 0.88,
        reasoning: 'Structured heuristic classification generated locally',
        severityEvidence: ['reported community problem'],
        requiredExpertise: [`${primaryDomain} Engineering`, 'Public Infrastructure'],
        requiredResources: ['Technical Equipment', 'Field Team'],
        researchRequired: true,
        governmentActionPossible: true,
      };
      status = 'Validated';
    }

    const newProblem: Problem = {
      problemId: newId,
      title: data.title,
      description: data.description,
      location: data.location,
      submittedAt: new Date().toISOString(),
      submitterId: 'CIT-CURRENT',
      submitterName: 'Citizen Submitter',
      primaryDomain: classification.primaryDomain,
      subcategory: classification.subcategory,
      secondaryDomains: classification.secondaryDomains,
      severity: classification.severity || 'HIGH',
      urgency: classification.urgency || 'HIGH',
      confidence: classification.confidence || 0.88,
      status: status,
      stage: reviewRequired ? 'VALIDATE' : 'ROUTE',
      aiClassification: classification,
      reviewRequired,
      reviewReason,
      evidenceFiles: data.evidenceFiles || [],
    };

    localProblems.unshift(newProblem);
    return newProblem;
  },

  // --- REVIEWER ACTIONS ---
  async executeReviewerAction(
    problemId: string,
    action: 'ACCEPT' | 'CORRECT' | 'MERGE_DUPLICATE' | 'REQUEST_CLARIFICATION' | 'REJECT_INVALID',
    payload?: any
  ): Promise<Problem> {
    const prob = localProblems.find((p) => p.problemId === problemId);
    if (!prob) throw new Error('Problem not found');

    if (action === 'ACCEPT') {
      prob.status = 'Validated';
      prob.stage = 'ROUTE';
      prob.reviewRequired = false;
    } else if (action === 'CORRECT' && payload) {
      prob.primaryDomain = payload.primaryDomain || prob.primaryDomain;
      prob.subcategory = payload.subcategory || prob.subcategory;
      prob.secondaryDomains = payload.secondaryDomains || prob.secondaryDomains;
      prob.severity = payload.severity || prob.severity;
      prob.status = 'Validated';
      prob.stage = 'ROUTE';
      prob.reviewRequired = false;
    } else if (action === 'MERGE_DUPLICATE' && payload?.masterProblemId) {
      prob.status = 'Merged Duplicate';
      prob.masterProblemId = payload.masterProblemId;
      prob.reviewRequired = false;
    } else if (action === 'REQUEST_CLARIFICATION') {
      prob.status = 'Under Review';
      prob.reviewReason = `Clarification requested: ${payload?.message || 'Additional details required'}`;
    } else if (action === 'REJECT_INVALID') {
      prob.status = 'Rejected';
      prob.reviewRequired = false;
    }

    return prob;
  },

  // --- DUPLICATE CHECK ---
  async checkDuplicates(problem: Problem): Promise<DuplicateCheckResponse> {
    try {
      const candidates = localProblems.filter((p) => p.problemId !== problem.problemId);
      const res = await fetch(`${BASE_URL}/api/v1/duplicate-detection/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem: {
            problemId: problem.problemId,
            title: problem.title,
            description: problem.description,
            primaryDomain: problem.primaryDomain,
            subcategory: problem.subcategory,
            location: problem.location,
          },
          candidates: candidates.map((c) => ({
            problemId: c.problemId,
            title: c.title,
            description: c.description,
            primaryDomain: c.primaryDomain,
            subcategory: c.subcategory,
            location: c.location,
          })),
        }),
      });

      if (res.ok) return await res.json();
    } catch (e) {
      console.info('Using local duplicate detection fallback');
    }

    const cands = localProblems
      .filter((p) => p.problemId !== problem.problemId)
      .map((cand) => {
        const isSameDomain = cand.primaryDomain === problem.primaryDomain;
        const score = isSameDomain ? 0.89 : 0.45;
        return {
          candidateProblemId: cand.problemId,
          duplicateScore: score,
          semanticSimilarity: isSameDomain ? 0.91 : 0.52,
          primaryDomainMatch: isSameDomain,
          subcategoryMatch: cand.subcategory === problem.subcategory,
          secondaryDomainOverlap: 0.5,
          locationDistanceKm: 1.2,
          locationScore: 0.85,
          candidateStatus: score >= 0.85 ? ('strong_candidate' as const) : ('no_candidate' as const),
          reasons: isSameDomain ? ['High semantic similarity', 'Same primary domain'] : ['Low similarity'],
          candidateTitle: cand.title,
          candidateDescription: cand.description,
        };
      })
      .filter((c) => c.duplicateScore > 0.6);

    return {
      problemId: problem.problemId,
      status: cands.length > 0 ? 'candidate_found' : 'no_candidate',
      duplicateCandidates: cands,
    };
  },

  // --- UNIVERSITY MATCHING ---
  async getMatchingForProblem(problemId: string): Promise<UniversityMatchResult[]> {
    if (localMatches[problemId]) return localMatches[problemId];

    try {
      const prob = await this.getProblemById(problemId);
      if (prob) {
        const res = await fetch(`${BASE_URL}/api/v1/matching/${problemId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            classification: prob.aiClassification || {
              primaryDomain: prob.primaryDomain,
              subcategory: prob.subcategory,
              requiredExpertise: [prob.primaryDomain + ' Infrastructure'],
              requiredResources: ['Testing Lab'],
              researchRequired: true,
              governmentActionPossible: true,
            },
            location: {
              district: prob.location.district,
              state: prob.location.state,
              latitude: prob.location.latitude,
              longitude: prob.location.longitude,
            },
          }),
        });

        if (res.ok) {
          const json: MatchingResponse = await res.json();
          if (json.topUniversities && json.topUniversities.length > 0) {
            localMatches[problemId] = json.topUniversities;
            return json.topUniversities;
          }
        }
      }
    } catch (e) {
      console.info('Using local matching fallback');
    }

    return INITIAL_MATCHES['CF-2026-001'] || [];
  },

  // --- ASSIGNMENTS ---
  async getAssignments(): Promise<UniversityAssignment[]> {
    return localAssignments;
  },

  async acceptAssignment(assignmentId: string): Promise<UniversityAssignment> {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/assignments/${assignmentId}/accept`, { method: 'POST' });
      if (res.ok) {
        const json = await res.json();
        return json.assignment;
      }
    } catch (e) {
      console.info('Using local assignment accept fallback');
    }

    const asn = localAssignments.find((a) => a.assignmentId === assignmentId);
    if (asn) {
      asn.status = 'ACCEPTED';
      asn.respondedAt = new Date().toISOString();
      const prob = localProblems.find((p) => p.problemId === asn.problemId);
      if (prob) {
        prob.status = 'University Assigned';
        prob.stage = 'COLLABORATE';
      }
    }
    return asn!;
  },

  async rejectAssignment(assignmentId: string, reason: string): Promise<UniversityAssignment> {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/assignments/${assignmentId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.info('Using local assignment reject fallback');
    }

    const asn = localAssignments.find((a) => a.assignmentId === assignmentId);
    if (asn) {
      asn.status = 'REJECTED';
      asn.rejectionReason = reason;
      asn.respondedAt = new Date().toISOString();
    }
    return asn!;
  },

  // --- MARKETPLACE & SOLUTIONS ---
  async getSolutions(): Promise<SolutionItem[]> {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/marketplace/solutions`);
      if (res.ok) {
        const items = await res.json();
        if (Array.isArray(items) && items.length > 0) return items;
      }
    } catch (e) {
      console.info('Using local marketplace fallback');
    }
    return localSolutions;
  },

  async expressInterest(
    solutionId: string,
    partnerId: string,
    supportOffered: string[],
    message: string,
    contribution: Record<string, any>
  ): Promise<IndustryInterest> {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/marketplace/${solutionId}/interest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ partnerId, supportOffered, contribution, message }),
      });
      if (res.ok) return await res.json();
    } catch (e) {
      console.info('Using local express interest fallback');
    }

    const newInterest: IndustryInterest = {
      interestId: `INT-${Math.floor(1000 + Math.random() * 9000)}`,
      solutionId,
      partnerId,
      partnerName: 'Industry Partner',
      supportOffered,
      contribution,
      message,
      status: 'PENDING',
      createdAt: new Date().toISOString(),
    };

    localInterests.unshift(newInterest);
    return newInterest;
  },

  async getCollaborations(): Promise<CollaborationItem[]> {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/collaborations`);
      if (res.ok) return await res.json();
    } catch (e) {
      console.info('Using local collaborations fallback');
    }
    return localCollaborations;
  },
};
