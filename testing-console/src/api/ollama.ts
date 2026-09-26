import { getServiceConfig } from '../config';
import { executeFetch } from './backend';

export const ollamaApi = {
  getHealth: (customUrl?: string) => {
    const url = customUrl || getServiceConfig().ollamaUrl;
    return executeFetch<{ models?: any[] }>('/api/tags', { method: 'GET' }, url);
  },
};
