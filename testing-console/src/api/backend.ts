import { getServiceConfig } from '../config';
import {
  AuditEvent,
  HTTPInspectorData,
  Problem,
  ProblemTimelineData,
  ReviewerQueueItem,
  StandardApiResponse,
} from '../types';

export interface APIExecutionResult<T = any> {
  data?: T;
  error?: string;
  inspector: HTTPInspectorData;
}

export async function executeFetch<T = any>(
  path: string,
  options: RequestInit = {},
  customBaseUrl?: string
): Promise<APIExecutionResult<T>> {
  const baseUrl = customBaseUrl || getServiceConfig().backendUrl;
  const url = `${baseUrl.replace(/\/$/, '')}${path}`;
  const startTime = performance.now();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  let reqBody: any = undefined;
  if (options.body) {
    try {
      reqBody = JSON.parse(options.body as string);
    } catch {
      reqBody = options.body;
    }
  }

  const inspectorData: HTTPInspectorData = {
    method: options.method || 'GET',
    url,
    headers,
    requestBody: reqBody,
    timestamp: new Date().toISOString(),
  };

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    const endTime = performance.now();
    inspectorData.durationMs = Math.round(endTime - startTime);
    inspectorData.statusCode = res.status;

    let resData: any;
    const text = await res.text();
    try {
      resData = JSON.parse(text);
    } catch {
      resData = text;
    }

    inspectorData.responseBody = resData;

    if (!res.ok) {
      const errMsg = typeof resData === 'object' && resData?.detail
        ? (typeof resData.detail === 'string' ? resData.detail : JSON.stringify(resData.detail))
        : (typeof resData === 'object' && resData?.error?.message ? resData.error.message : `HTTP Error ${res.status}`);
      inspectorData.error = errMsg;
      return { error: errMsg, inspector: inspectorData };
    }

    return { data: resData as T, inspector: inspectorData };
  } catch (err: any) {
    const endTime = performance.now();
    inspectorData.durationMs = Math.round(endTime - startTime);
    inspectorData.statusCode = 0;
    inspectorData.error = err.message || 'Network failure or server unreachable';
    return { error: inspectorData.error, inspector: inspectorData };
  }
}

// Backend API Endpoints
export const backendApi = {
  getHealth: (customUrl?: string) =>
    executeFetch<{ status: string; service: string; version: string; database: string }>('/health', { method: 'GET' }, customUrl),

  getDependencyHealth: (customUrl?: string) =>
    executeFetch<{ status: string; dependencies: { classificationEngine: string; duplicateDetectionEngine: string } }>('/health/dependencies', { method: 'GET' }, customUrl),

  createProblem: (
    payload: {
      problemId?: string;
      title: string;
      description: string;
      location?: { lat?: number; long?: number; address?: string };
      privacyClass?: string;
    },
    userId = 'citizen_001',
    userRole = 'citizen',
    customUrl?: string
  ) =>
    executeFetch<StandardApiResponse<Problem>>(
      '/api/problems',
      {
        method: 'POST',
        headers: {
          'X-User-ID': userId,
          'X-User-Role': userRole,
        },
        body: JSON.stringify(payload),
      },
      customUrl
    ),

  getProblem: (problemId: string, customUrl?: string) =>
    executeFetch<StandardApiResponse<Problem>>(`/api/problems/${problemId}`, { method: 'GET' }, customUrl),

  getProblemTimeline: (problemId: string, customUrl?: string) =>
    executeFetch<StandardApiResponse<ProblemTimelineData>>(`/api/problems/${problemId}/timeline`, { method: 'GET' }, customUrl),

  getReviewerQueue: (userRole = 'reviewer', customUrl?: string) =>
    executeFetch<StandardApiResponse<{ count: number; queue: ReviewerQueueItem[] }>>(
      '/api/reviewer/queue',
      {
        method: 'GET',
        headers: { 'X-User-Role': userRole },
      },
      customUrl
    ),

  executeReviewerAction: (
    problemId: string,
    payload: {
      action: string;
      reason?: string;
      masterProblemId?: string;
      payload?: Record<string, any>;
    },
    userId = 'reviewer_001',
    userRole = 'reviewer',
    customUrl?: string
  ) =>
    executeFetch<StandardApiResponse<{ problem: Problem; reviewRecord: any }>>(
      `/api/reviewer/${problemId}/action`,
      {
        method: 'POST',
        headers: {
          'X-User-ID': userId,
          'X-User-Role': userRole,
        },
        body: JSON.stringify(payload),
      },
      customUrl
    ),

  routeProblem: (
    problemId: string,
    destination = 'GOVERNMENT',
    userId = 'reviewer_001',
    userRole = 'reviewer',
    customUrl?: string
  ) =>
    executeFetch<StandardApiResponse<Problem>>(
      `/api/government/${problemId}/route?destination=${encodeURIComponent(destination)}`,
      {
        method: 'POST',
        headers: {
          'X-User-ID': userId,
          'X-User-Role': userRole,
        },
      },
      customUrl
    ),

  getAuditTrail: (entityId: string, customUrl?: string) =>
    executeFetch<StandardApiResponse<{ entityId: string; count: number; events: AuditEvent[] }>>(
      `/api/audit/${entityId}`,
      { method: 'GET' },
      customUrl
    ),
};
