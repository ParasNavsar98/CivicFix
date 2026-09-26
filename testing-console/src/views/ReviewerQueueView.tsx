import React, { useEffect, useState } from 'react';
import { backendApi } from '../api/backend';
import { ReviewerQueueItem, HTTPInspectorData } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { JsonViewer } from '../components/JsonViewer';
import { NavTab } from '../components/Sidebar';
import { Inbox, RefreshCw, AlertTriangle, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';

interface Props {
  onNavigate: (tab: NavTab) => void;
}

export const ReviewerQueueView: React.FC<Props> = ({ onNavigate }) => {
  const [role, setRole] = useState('reviewer');
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<ReviewerQueueItem[]>([]);
  const [inspector, setInspector] = useState<HTTPInspectorData | null>(null);
  const [selectedItem, setSelectedItem] = useState<ReviewerQueueItem | null>(null);

  const loadQueue = async () => {
    setLoading(true);
    const res = await backendApi.getReviewerQueue(role);
    setInspector(res.inspector);

    if (res.data?.data?.queue) {
      setItems(res.data.data.queue);
    } else {
      setItems([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadQueue();
  }, [role]);

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Inbox className="w-5 h-5 text-amber-400" />
            <span>Reviewer Queue (`GET /api/reviewer/queue`)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Surfaces problems flagged for human reviewer attention due to low AI confidence (&lt; 0.85), surfaced duplicate candidates, ambiguity, or AI service errors.
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <label className="text-slate-400 font-semibold">Header Role:</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="px-3 py-1.5 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200 focus:outline-none focus:border-amber-500"
            >
              <option value="reviewer">reviewer (Allowed)</option>
              <option value="admin">admin (Allowed)</option>
              <option value="citizen">citizen (FORBIDDEN 403)</option>
            </select>
          </div>

          <button
            onClick={loadQueue}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-amber-600 hover:bg-amber-500 text-white font-semibold shadow transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Reload Queue</span>
          </button>
        </div>
      </div>

      {/* Queue Table */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-3 mb-3 flex items-center justify-between">
          <span>Pending Review Cases ({items.length})</span>
          {role === 'citizen' && (
            <span className="text-xs text-rose-400 font-mono font-bold flex items-center gap-1">
              <ShieldAlert className="w-4 h-4" /> 403 Forbidden Expected
            </span>
          )}
        </h3>

        {loading ? (
          <div className="py-8 text-center text-xs text-slate-400 animate-pulse">Loading queue...</div>
        ) : items.length === 0 ? (
          <div className="py-10 text-center text-xs text-slate-500">
            {inspector?.statusCode === 403 ? (
              <div className="text-rose-400 font-mono">
                <ShieldAlert className="w-8 h-8 text-rose-500 mx-auto mb-2" />
                <div>Access Denied: Header X-User-Role='citizen' cannot access reviewer queue.</div>
              </div>
            ) : (
              <div>
                <CheckCircle2 className="w-8 h-8 text-slate-700 mx-auto mb-2" />
                <div>Queue is empty. No cases currently require review.</div>
              </div>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-sans">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono">
                  <th className="py-2.5 px-3">Problem ID</th>
                  <th className="py-2.5 px-3">Title</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Review Reasons</th>
                  <th className="py-2.5 px-3">Active Domain</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {items.map((item) => (
                  <tr key={item.problem.problemId} className="hover:bg-slate-800/40">
                    <td className="py-3 px-3 font-mono text-cyan-300 font-bold">{item.problem.problemId}</td>
                    <td className="py-3 px-3 font-medium text-slate-200 max-w-xs truncate">{item.problem.title}</td>
                    <td className="py-3 px-3">
                      <StatusBadge status={item.problem.status} />
                    </td>
                    <td className="py-3 px-3 font-mono text-amber-400 max-w-xs truncate">
                      {item.problem.reviewReasons?.join(', ') || 'Review Flagged'}
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-300">
                      {item.problem.primaryDomain || 'Unassigned'}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => setSelectedItem(item)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 font-medium text-xs border border-slate-700"
                      >
                        Inspect Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Selected Item Drawer / Detail */}
      {selectedItem && (
        <div className="p-5 rounded-xl bg-slate-900 border border-cyan-800/80 space-y-4 text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <div className="text-cyan-400 font-mono font-bold">Inspect Review Queue Item: {selectedItem.problem.problemId}</div>
              <h3 className="text-base font-bold text-slate-100 mt-0.5">{selectedItem.problem.title}</h3>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => onNavigate('reviewer-actions')}
                className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center gap-1 shadow"
              >
                <span>Execute Reviewer Action</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="font-bold text-slate-300 mb-1">Problem Details</div>
              <JsonViewer data={selectedItem.problem} title="Problem Object" />
            </div>

            <div>
              <div className="font-bold text-slate-300 mb-1">Active Version Snapshot (`{selectedItem.activeVersion?.source}`)</div>
              <JsonViewer data={selectedItem.activeVersion || { message: 'No active version' }} title="Active Version Object" />
            </div>
          </div>

          {selectedItem.duplicateCandidates?.length > 0 && (
            <div>
              <div className="font-bold text-amber-400 mb-1 flex items-center gap-1">
                <AlertTriangle className="w-4 h-4" />
                <span>Surfaced Duplicate Candidates ({selectedItem.duplicateCandidates.length}):</span>
              </div>
              <JsonViewer data={selectedItem.duplicateCandidates} title="Surfaced Duplicate Candidates" />
            </div>
          )}
        </div>
      )}

      {inspector && <RequestResponseInspector inspector={inspector} />}
    </div>
  );
};
