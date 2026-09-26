import React, { useState } from 'react';
import { backendApi } from '../api/backend';
import { getServiceConfig, resetServiceConfig, saveServiceConfig } from '../config';
import { HTTPInspectorData, Problem } from '../types';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { StatusBadge } from '../components/StatusBadge';
import { AlertTriangle, Play, CheckCircle2, RotateCcw, ShieldAlert, Cpu } from 'lucide-react';

export const FailureTestingView: React.FC = () => {
  const [config, setConfig] = useState(getServiceConfig());
  const [invalidUrl, setInvalidUrl] = useState('http://localhost:9999');
  const [problemId, setProblemId] = useState('P-FAIL-TEST-01');
  const [title, setTitle] = useState('Critical Pipe Leakage (Failure Test)');
  const [description, setDescription] = useState('Testing backend resilience when Classification Engine service is offline.');

  const [loading, setLoading] = useState(false);
  const [inspector, setInspector] = useState<HTTPInspectorData | null>(null);
  const [resultProblem, setResultProblem] = useState<Problem | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSimulateOutage = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResultProblem(null);
    setError(null);

    // Save override with invalid classification URL
    saveServiceConfig({ classificationUrl: invalidUrl });
    setConfig(getServiceConfig());

    // Submit problem to main backend
    const res = await backendApi.createProblem({
      problemId: problemId.trim(),
      title: title.trim(),
      description: description.trim(),
    });

    setInspector(res.inspector);

    if (res.data?.success && res.data?.data) {
      setResultProblem(res.data.data);
    } else {
      setError(res.error || 'Submission error');
    }

    setLoading(false);
  };

  const handleRestoreUrls = () => {
    const res = resetServiceConfig();
    setConfig(res);
    setResultProblem(null);
    setInspector(null);
  };

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span>Failure Isolation & Microservice Outage Testing</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Tests backend resilience under AI microservice failure (timeout, network outage, port unreachable).
          </p>
        </div>

        <button
          onClick={handleRestoreUrls}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 font-mono"
        >
          <RotateCcw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Restore Default URLs</span>
        </button>
      </div>

      <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-800 text-xs text-amber-300 space-y-1 font-mono">
        <div className="font-bold flex items-center gap-1.5 text-amber-400">
          <ShieldAlert className="w-4 h-4" />
          <span>SRS Resilience Mandate:</span>
        </div>
        <div>
          1. Citizen problem submission must be stored in database FIRST (`SUBMITTED`) before AI invocation.
        </div>
        <div>
          2. AI microservice outages must NEVER cause deletion or loss of the citizen submission.
        </div>
        <div>
          3. On AI failure, problem status becomes `REVIEW_REQUIRED`, state set to `failed`, review reasons appended.
        </div>
      </div>

      <form onSubmit={handleSimulateOutage} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Simulated Invalid Classification Service URL</label>
            <input
              type="text"
              required
              value={invalidUrl}
              onChange={(e) => setInvalidUrl(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-amber-700 font-mono text-amber-300 font-bold"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Test Problem ID</label>
            <input
              type="text"
              required
              value={problemId}
              onChange={(e) => setProblemId(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-cyan-300 font-bold"
            />
          </div>
        </div>

        <div>
          <label className="block text-slate-300 font-semibold mb-1">Problem Title</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200"
          />
        </div>

        <div>
          <label className="block text-slate-300 font-semibold mb-1">Description</label>
          <textarea
            required
            rows={2}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200"
          />
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>{loading ? 'Submitting with Outage Simulation...' : 'Simulate Classification Outage'}</span>
          </button>
        </div>
      </form>

      {/* Outage Verification Result */}
      {resultProblem && (
        <div className="p-5 rounded-xl bg-slate-900 border border-emerald-800/80 space-y-4 text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="font-bold text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 className="w-5 h-5" />
              <span>Resilience Mandate Verified: Problem Retained in DB!</span>
            </div>
            <StatusBadge status={resultProblem.status} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono">
            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-sans font-semibold">Problem ID</div>
              <div className="text-cyan-300 font-bold mt-1">{resultProblem.problemId}</div>
            </div>

            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-sans font-semibold">Classification State</div>
              <div className="text-rose-400 font-bold mt-1">{resultProblem.classificationState}</div>
            </div>

            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-sans font-semibold">Review Flagged</div>
              <div className="text-amber-400 font-bold mt-1">{resultProblem.reviewRequired ? 'YES (REVIEW_REQUIRED)' : 'NO'}</div>
            </div>
          </div>

          <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
            <div className="text-slate-400 font-semibold mb-1">Review Reasons Logged:</div>
            <div className="font-mono text-amber-300">{resultProblem.reviewReasons?.join(', ')}</div>
          </div>
        </div>
      )}

      {inspector && <RequestResponseInspector inspector={inspector} />}
    </div>
  );
};
