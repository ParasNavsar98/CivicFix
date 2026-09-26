import React, { useState } from 'react';
import { backendApi } from '../api/backend';
import { HTTPInspectorData, Problem } from '../types';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { StatusBadge } from '../components/StatusBadge';
import { JsonViewer } from '../components/JsonViewer';
import { Building2, Play, CheckCircle2, AlertTriangle, ShieldAlert } from 'lucide-react';

export const GovernmentRoutingView: React.FC = () => {
  const [problemId, setProblemId] = useState('');
  const [destination, setDestination] = useState('GOVERNMENT');
  const [userId, setUserId] = useState('reviewer_001');
  const [userRole, setUserRole] = useState('reviewer');

  const [loading, setLoading] = useState(false);
  const [inspector, setInspector] = useState<HTTPInspectorData | null>(null);
  const [result, setResult] = useState<Problem | null>(null);

  const handleRoute = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    const res = await backendApi.routeProblem(
      problemId.trim(),
      destination,
      userId.trim(),
      userRole.trim()
    );

    setInspector(res.inspector);

    if (res.data?.success && res.data?.data) {
      setResult(res.data.data);
    }

    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Building2 className="w-5 h-5 text-cyan-400" />
          <span>Government & Research Routing (`POST /api/government/{'{problem_id}'}/route`)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Routes a validated problem to municipal government authorities (`ROUTED_GOVERNMENT`) or university research matching (`PENDING_MATCH`).
        </p>
      </div>

      <form onSubmit={handleRoute} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Target Problem ID</label>
            <input
              type="text"
              required
              placeholder="e.g. P-TEST-001"
              value={problemId}
              onChange={(e) => setProblemId(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-cyan-300 font-bold focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">X-User-ID (Header)</label>
            <input
              type="text"
              required
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">X-User-Role (Header)</label>
            <select
              value={userRole}
              onChange={(e) => setUserRole(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 font-mono"
            >
              <option value="reviewer">reviewer (Allowed)</option>
              <option value="admin">admin (Allowed)</option>
              <option value="government_official">government_official (Allowed)</option>
              <option value="citizen">citizen (FORBIDDEN 403)</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-slate-300 font-semibold mb-1">Target Routing Destination</label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button
              type="button"
              onClick={() => setDestination('GOVERNMENT')}
              className={`p-3 rounded-lg border text-left transition-colors ${
                destination === 'GOVERNMENT'
                  ? 'bg-cyan-950/80 border-cyan-600 text-cyan-200 font-bold'
                  : 'bg-slate-800/80 border-slate-700 text-slate-300'
              }`}
            >
              <div className="font-semibold text-xs">GOVERNMENT</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Routes to municipal case ref (State: ROUTED_GOVERNMENT)</div>
            </button>

            <button
              type="button"
              onClick={() => setDestination('RESEARCH')}
              className={`p-3 rounded-lg border text-left transition-colors ${
                destination === 'RESEARCH'
                  ? 'bg-indigo-950/80 border-indigo-600 text-indigo-200 font-bold'
                  : 'bg-slate-800/80 border-slate-700 text-slate-300'
              }`}
            >
              <div className="font-semibold text-xs">RESEARCH</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Routes for university innovation matching (State: PENDING_MATCH)</div>
            </button>

            <button
              type="button"
              onClick={() => setDestination('BOTH')}
              className={`p-3 rounded-lg border text-left transition-colors ${
                destination === 'BOTH'
                  ? 'bg-purple-950/80 border-purple-600 text-purple-200 font-bold'
                  : 'bg-slate-800/80 border-slate-700 text-slate-300'
              }`}
            >
              <div className="font-semibold text-xs">BOTH</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Dual municipal + research pathway</div>
            </button>
          </div>
        </div>

        {destination !== 'GOVERNMENT' && (
          <div className="p-3 rounded bg-indigo-950/60 border border-indigo-800 text-[11px] text-indigo-300 font-mono flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-indigo-400" />
            <span>Implementation Note: Routing foundation exists; university matching engine is model-only / not fully implemented.</span>
          </div>
        )}

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>{loading ? 'Routing Problem...' : `Execute Route (${destination})`}</span>
          </button>
        </div>
      </form>

      {result && (
        <div className="p-5 rounded-xl bg-slate-900 border border-cyan-800/80 space-y-3 text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2 font-bold text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
              <span>Problem Successfully Routed!</span>
            </div>
            <StatusBadge status={result.status} />
          </div>
          <JsonViewer data={result} title="Updated Problem Model" />
        </div>
      )}

      {inspector && <RequestResponseInspector inspector={inspector} />}
    </div>
  );
};
