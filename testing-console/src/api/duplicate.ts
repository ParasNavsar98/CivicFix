import { getServiceConfig } from '../config';
import { APIExecutionResult, executeFetch } from './backend';
import { DuplicateCheckResponse } from '../types';

export const duplicateApi = {
  getHealth: (customUrl?: string) => {
    const url = customUrl || getServiceConfig().duplicateUrl;
    return executeFetch<{
      status: string;
      service: string;
      embeddingModel: string;
      embeddingDimension: number;
      duplicateThreshold: number;
    }>('/health', { method: 'GET' }, url);
  },

  checkDuplicates: (
    payload: {
      problem: {
        problemId?: string;
        title: string;
        description: string;
        location?: { lat?: number; long?: number; address?: string };
        primaryDomain?: string;
        secondaryDomains?: string[];
        subcategory?: string;
      };
      candidates?: any[];
      topK?: number;
    },
    customUrl?: string
  ): Promise<APIExecutionResult<DuplicateCheckResponse>> => {
    const url = customUrl || getServiceConfig().duplicateUrl;
    return executeFetch<DuplicateCheckResponse>(
      '/duplicate-check',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      url
    );
  },
};
