import React, { useState } from 'react';
import { backendApi } from '../api/backend';
import { HTTPInspectorData, ProblemTimelineData } from '../types';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { StatusBadge } from '../components/StatusBadge';
import { JsonViewer } from '../components/JsonViewer';
import { Clock, Search, CheckCircle2, Play } from 'lucide-react';

export const TimelineView: React.FC = () => {
  const [problemId, setProblemId] = useState('');
  const [loading, setLoading] = useState(false);
  const [inspector, setInspector] = useState<HTTPInspectorData | null>(null);
  const [timeline, setTimeline] = useState<ProblemTimelineData | null>(null);

  const handleFetchTimeline = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!problemId.trim()) return;
    setLoading(true);
    setTimeline(null);

    const res = await backendApi.getProblemTimeline(problemId.trim());
    setInspector(res.inspector);

    if (res.data?.success && res.data?.data) {
      setTimeline(res.data.data);
    }

    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Clock className="w-5 h-5 text-cyan-400" />
          <span>Citizen Status Timeline (`GET /api/problems/{'{problem_id}'}/timeline`)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Chronological citizen progress timeline. Internal reviewer prompts, raw LLM errors, and private notes are suppressed from this endpoint.
        </p>
      </div>

      <form onSubmit={handleFetchTimeline} className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-end gap-3 text-xs">
        <div className="flex-1 min-w-[250px]">
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

        <button
          type="submit"
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
        >
          <Search className="w-4 h-4" />
          <span>{loading ? 'Loading Timeline...' : 'Load Citizen Timeline'}</span>
        </button>
      </form>

      {/* Visual Timeline Steps */}
      {timeline && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <div className="text-xs text-slate-400 font-mono">Problem ID: {timeline.problemId}</div>
              <h3 className="text-base font-bold text-slate-100 mt-0.5">{timeline.title}</h3>
            </div>
            <StatusBadge status={timeline.currentStatus} />
          </div>

          <div className="relative border-l-2 border-slate-700 ml-3 space-y-6 py-2">
            {timeline.timeline.map((step, idx) => (
              <div key={idx} className="relative pl-6">
                <span className="absolute -left-[9px] top-1.5 w-4 h-4 rounded-full bg-cyan-950 border-2 border-cyan-400 flex items-center justify-center">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                </span>
                <div className="font-mono text-[11px] text-slate-400">{step.timestamp}</div>
                <div className="font-bold text-slate-200 text-sm mt-0.5 flex items-center gap-2">
                  <span>{step.step}</span>
                  <StatusBadge status={step.status} />
                </div>
                <div className="text-slate-300 font-sans mt-1 bg-slate-800/60 p-2.5 rounded border border-slate-700/80">
                  {step.summary}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {inspector && <RequestResponseInspector inspector={inspector} />}
    </div>
  );
};
