import React, { useEffect, useState } from 'react';
import { backendApi } from '../api/backend';
import { classificationApi } from '../api/classification';
import { duplicateApi } from '../api/duplicate';
import { ollamaApi } from '../api/ollama';
import { getServiceConfig } from '../config';
import { RefreshCw, Activity, Server, Cpu, Layers, Database } from 'lucide-react';

interface ServiceHealthState {
  status: 'ONLINE' | 'OFFLINE' | 'DEGRADED' | 'CHECKING';
  latencyMs?: number;
  details?: string;
}

export const Header: React.FC = () => {
  const [config, setConfig] = useState(getServiceConfig());
  const [backendHealth, setBackendHealth] = useState<ServiceHealthState>({ status: 'CHECKING' });
  const [classificationHealth, setClassificationHealth] = useState<ServiceHealthState>({ status: 'CHECKING' });
  const [duplicateHealth, setDuplicateHealth] = useState<ServiceHealthState>({ status: 'CHECKING' });
  const [ollamaHealth, setOllamaHealth] = useState<ServiceHealthState>({ status: 'CHECKING' });
  const [isRefreshing, setIsRefreshing] = useState(false);

  const checkAllServices = async () => {
    setIsRefreshing(true);
    const activeCfg = getServiceConfig();
    setConfig(activeCfg);

    // 1. Backend
    const bRes = await backendApi.getHealth();
    if (bRes.data && bRes.data.status === 'ok') {
      setBackendHealth({ status: 'ONLINE', latencyMs: bRes.inspector.durationMs, details: bRes.data.service });
    } else {
      setBackendHealth({ status: 'OFFLINE', details: bRes.error || 'Connection failed' });
    }

    // 2. Classification
    const cRes = await classificationApi.getHealth();
    if (cRes.data && cRes.data.status === 'healthy') {
      setClassificationHealth({ status: 'ONLINE', latencyMs: cRes.inspector.durationMs, details: 'Gemma 3 4B Service' });
    } else {
      setClassificationHealth({ status: 'OFFLINE', details: cRes.error || 'Connection failed' });
    }

    // 3. Duplicate
    const dRes = await duplicateApi.getHealth();
    if (dRes.data && (dRes.data.status === 'ok' || dRes.data.status === 'healthy')) {
      setDuplicateHealth({ status: 'ONLINE', latencyMs: dRes.inspector.durationMs, details: dRes.data.embeddingModel });
    } else {
      setDuplicateHealth({ status: 'OFFLINE', details: dRes.error || 'Connection failed' });
    }

    // 4. Ollama
    const oRes = await ollamaApi.getHealth();
    if (oRes.data && Array.isArray(oRes.data.models)) {
      const gemmaModel = oRes.data.models.find((m: any) => m.name?.includes('gemma'));
      setOllamaHealth({
        status: 'ONLINE',
        latencyMs: oRes.inspector.durationMs,
        details: gemmaModel ? `Model: ${gemmaModel.name}` : `${oRes.data.models.length} models loaded`,
      });
    } else {
      setOllamaHealth({ status: 'OFFLINE', details: oRes.error || 'Ollama server unreachable' });
    }

    setIsRefreshing(false);
  };

  useEffect(() => {
    checkAllServices();
  }, []);

  const renderBadge = (title: string, state: ServiceHealthState, icon: React.ReactNode, url: string) => {
    const isOnline = state.status === 'ONLINE';
    const isChecking = state.status === 'CHECKING';

    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/90 border border-slate-700/80 shadow-sm" title={`${title} @ ${url}`}>
        <div className="text-slate-400">{icon}</div>
        <div className="text-xs">
          <div className="font-semibold text-slate-200 flex items-center gap-1.5">
            <span>{title}</span>
            <span className={`w-2 h-2 rounded-full ${isChecking ? 'bg-amber-400 animate-ping' : isOnline ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' : 'bg-rose-500'}`} />
          </div>
          <div className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <span className={isOnline ? 'text-emerald-400 font-bold' : 'text-rose-400'}>
              {state.status}
            </span>
            {state.latencyMs !== undefined && (
              <span className="text-slate-500">• {state.latencyMs}ms</span>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <header className="bg-slate-900 border-b border-slate-800 px-6 py-3.5 sticky top-0 z-50 shadow-md">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left Title */}
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-950 border border-cyan-800 text-cyan-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-100 flex items-center gap-2">
              CivicFix <span className="text-xs font-mono font-medium px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">E2E Testing Console</span>
            </h1>
            <p className="text-xs text-slate-400">Engineering QA & Microservice Integration Dashboard</p>
          </div>
        </div>

        {/* System Health Badges */}
        <div className="flex flex-wrap items-center gap-2">
          {renderBadge('Main Backend', backendHealth, <Server className="w-4 h-4" />, config.backendUrl)}
          {renderBadge('Classification', classificationHealth, <Cpu className="w-4 h-4" />, config.classificationUrl)}
          {renderBadge('Duplicate Eng.', duplicateHealth, <Layers className="w-4 h-4" />, config.duplicateUrl)}
          {renderBadge('Ollama Service', ollamaHealth, <Database className="w-4 h-4" />, config.ollamaUrl)}

          <button
            onClick={checkAllServices}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition-colors disabled:opacity-50"
            title="Probe system health"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh Probes</span>
          </button>
        </div>
      </div>
    </header>
  );
};
