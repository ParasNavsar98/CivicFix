import { getServiceConfig } from '../config';
import { APIExecutionResult, executeFetch } from './backend';
import { ClassificationResponse } from '../types';

export const classificationApi = {
  getHealth: (customUrl?: string) => {
    const url = customUrl || getServiceConfig().classificationUrl;
    return executeFetch<{ status: string }>('/health', { method: 'GET' }, url);
  },

  classifyProblem: (
    payload: {
      problemId: string;
      title: string;
      description: string;
      location: {
        district: string;
        state: string;
        latitude?: number | null;
        longitude?: number | null;
      };
    },
    customUrl?: string
  ): Promise<APIExecutionResult<ClassificationResponse>> => {
    const url = customUrl || getServiceConfig().classificationUrl;
    return executeFetch<ClassificationResponse>(
      '/classify',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      url
    );
  },
};
