/**
 * Centralized Configuration for CivicFix Testing Console
 */

export interface ServiceConfig {
  backendUrl: string;
  classificationUrl: string;
  duplicateUrl: string;
  ollamaUrl: string;
}

const DEFAULT_CONFIG: ServiceConfig = {
  backendUrl: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8002',
  classificationUrl: import.meta.env.VITE_CLASSIFICATION_URL || 'http://localhost:8000',
  duplicateUrl: import.meta.env.VITE_DUPLICATE_URL || 'http://localhost:8001',
  ollamaUrl: import.meta.env.VITE_OLLAMA_URL || 'http://localhost:11434',
};

const OVERRIDE_STORAGE_KEY = 'civicfix_service_config_overrides';

export function getServiceConfig(): ServiceConfig {
  try {
    const saved = localStorage.getItem(OVERRIDE_STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      return {
        backendUrl: parsed.backendUrl || DEFAULT_CONFIG.backendUrl,
        classificationUrl: parsed.classificationUrl || DEFAULT_CONFIG.classificationUrl,
        duplicateUrl: parsed.duplicateUrl || DEFAULT_CONFIG.duplicateUrl,
        ollamaUrl: parsed.ollamaUrl || DEFAULT_CONFIG.ollamaUrl,
      };
    }
  } catch (e) {
    console.error('Error reading service config from localStorage:', e);
  }
  return { ...DEFAULT_CONFIG };
}

export function saveServiceConfig(config: Partial<ServiceConfig>): ServiceConfig {
  const current = getServiceConfig();
  const updated = { ...current, ...config };
  localStorage.setItem(OVERRIDE_STORAGE_KEY, JSON.stringify(updated));
  return updated;
}

export function resetServiceConfig(): ServiceConfig {
  localStorage.removeItem(OVERRIDE_STORAGE_KEY);
  return { ...DEFAULT_CONFIG };
}

export function getDefaultConfig(): ServiceConfig {
  return { ...DEFAULT_CONFIG };
}
