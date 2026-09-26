import React, { useEffect, useState } from 'react';
import { backendApi } from '../api/backend';
import { classificationApi } from '../api/classification';
import { duplicateApi } from '../api/duplicate';
import { ollamaApi } from '../api/ollama';
import { getServiceConfig, resetServiceConfig, saveServiceConfig } from '../config';
import { HTTPInspectorData } from '../types';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { HeartPulse, RefreshCw, Server, Cpu, Layers, Database, RotateCcw, AlertTriangle, CheckCircle } from 'lucide-react';

export const SystemHealthView: React.FC = () => {
  const [config, setConfig] = useState(getServiceConfig());
  const [inspectors, setInspectors] = useState<Record<string, HTTPInspectorData>>({});
  const [loading, setLoading] = useState(false);

  const [backendUrlInput, setBackendUrlInput] = useState(config.backendUrl);
  const [clsUrlInput, setClsUrlInput] = useState(config.classificationUrl);
  const [dupUrlInput, setDupUrlInput] = useState(config.duplicateUrl);
  const [ollamaUrlInput, setOllamaUrlInput] = useState(config.ollamaUrl);

  const runProbes = async () => {
    setLoading(true);
    const activeCfg = getServiceConfig();

    const [b, bd, c, d, o] = await Promise.all([
      backendApi.getHealth(activeCfg.backendUrl),
      backendApi.getDependencyHealth(activeCfg.backendUrl),
      classificationApi.getHealth(activeCfg.classificationUrl),
      duplicateApi.getHealth(activeCfg.duplicateUrl),
      ollamaApi.getHealth(activeCfg.ollamaUrl),
    ]);

    setInspectors({
      backend: b.inspector,
      backendDeps: bd.inspector,
      classification: c.inspector,
      duplicate: d.inspector,
      ollama: o.inspector,
    });

    setLoading(false);
  };

  useEffect(() => {
    runProbes();
  }, []);

  const handleSaveOverrides = (e: React.FormEvent) => {
    e.preventDefault();
    const updated = saveServiceConfig({
      backendUrl: backendUrlInput,
      classificationUrl: clsUrlInput,
      duplicateUrl: dupUrlInput,
      ollamaUrl: ollamaUrlInput,
    });
    setConfig(updated);
    runProbes();
  };

  const handleResetDefaults = () => {
    const res = resetServiceConfig();
    setConfig(res);
    setBackendUrlInput(res.backendUrl);
    setClsUrlInput(res.classificationUrl);
    setDupUrlInput(res.duplicateUrl);
    setOllamaUrlInput(res.ollamaUrl);
    runProbes();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-xl bg-slate-900 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <HeartPulse className="w-5 h-5 text-cyan-400" />
            <span>System Health & Readiness Probes</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Live HTTP health probes for CivicFix microservices. Use this tab to verify service readiness or configure URL overrides for failure testing.
          </p>
        </div>
        <button
          onClick={runProbes}
          disabled={loading}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Probe All Services</span>
        </button>
      </div>

      {/* URL Overrides Form */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-2.5 mb-4 flex items-center justify-between">
          <span>Target Service URLs Configuration</span>
          <button
            type="button"
            onClick={handleResetDefaults}
            className="text-xs text-slate-400 hover:text-cyan-400 flex items-center gap-1 font-mono font-normal"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset to Defaults</span>
          </button>
        </h3>

        <form onSubmit={handleSaveOverrides} className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Main Backend URL</label>
            <input
              type="text"
              value={backendUrlInput}
              onChange={(e) => setBackendUrlInput(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Classification Engine URL</label>
            <input
              type="text"
              value={clsUrlInput}
              onChange={(e) => setClsUrlInput(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Duplicate Detection Engine URL</label>
            <input
              type="text"
              value={dupUrlInput}
              onChange={(e) => setDupUrlInput(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Ollama Service URL</label>
            <input
              type="text"
              value={ollamaUrlInput}
              onChange={(e) => setOllamaUrlInput(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="md:col-span-2 flex justify-end">
            <button
              type="submit"
              className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 font-semibold text-xs"
            >
              Apply & Save URL Overrides
            </button>
          </div>
        </form>
      </div>

      {/* Individual Probe Results */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-200">Raw HTTP Probe Inspector Logs</h3>

        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-300 flex items-center gap-2">
            <Server className="w-4 h-4 text-cyan-400" />
            <span>1. Main Backend Health (`GET /health`)</span>
          </div>
          <RequestResponseInspector inspector={inspectors.backend} />
        </div>

        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-300 flex items-center gap-2">
            <Server className="w-4 h-4 text-purple-400" />
            <span>2. Main Backend Microservice Dependency Probe (`GET /health/dependencies`)</span>
          </div>
          <RequestResponseInspector inspector={inspectors.backendDeps} />
        </div>

        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-300 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span>3. Classification Engine Health (`GET /health`)</span>
          </div>
          <RequestResponseInspector inspector={inspectors.classification} />
        </div>

        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-300 flex items-center gap-2">
            <Layers className="w-4 h-4 text-amber-400" />
            <span>4. Duplicate Detection Engine Health (`GET /health`)</span>
          </div>
          <RequestResponseInspector inspector={inspectors.duplicate} />
        </div>

        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-300 flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-400" />
            <span>5. Ollama Inference Server Tags (`GET /api/tags`)</span>
          </div>
          <RequestResponseInspector inspector={inspectors.ollama} />
        </div>
      </div>
    </div>
  );
};
