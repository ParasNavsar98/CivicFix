import React, { useState } from 'react';
import { backendApi } from '../api/backend';
import { HTTPInspectorData, Problem } from '../types';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { StatusBadge } from '../components/StatusBadge';
import { JsonViewer } from '../components/JsonViewer';
import { NavTab } from '../components/Sidebar';
import { CheckSquare, Play, ShieldAlert, AlertTriangle, ArrowRight, CheckCircle2 } from 'lucide-react';

interface Props {
  onNavigate: (tab: NavTab) => void;
}

const ACTION_TYPES = [
  { id: 'ACCEPT', label: 'ACCEPT — Validate AI classification & clear review flag', reqReason: false, reqMaster: false },
  { id: 'CORRECT', label: 'CORRECT — Override taxonomy fields (Creates NEW reviewer version)', reqReason: true, reqMaster: false, hasPayload: true },
  { id: 'MERGE_DUPLICATE', label: 'MERGE_DUPLICATE — Link duplicate to master (Preserves original record)', reqReason: true, reqMaster: true },
  { id: 'REQUEST_CLARIFICATION', label: 'REQUEST_CLARIFICATION — Request citizen clarification', reqReason: true, reqMaster: false },
  { id: 'REQUEST_VERIFICATION', label: 'REQUEST_VERIFICATION — Request field verification', reqReason: false, reqMaster: false },
  { id: 'REJECT_INVALID', label: 'REJECT_INVALID — Reject spam / invalid report', reqReason: true, reqMaster: false },
  { id: 'REDIRECT', label: 'REDIRECT — Redirect jurisdiction', reqReason: true, reqMaster: false, hasPayload: true },
  { id: 'ESCALATE', label: 'ESCALATE — Escalate to executive authority', reqReason: true, reqMaster: false },
];

export const ReviewerActionsView: React.FC<Props> = ({ onNavigate }) => {
  const [problemId, setProblemId] = useState('');
  const [selectedAction, setSelectedAction] = useState('ACCEPT');
  const [reason, setReason] = useState('Classification validated by human reviewer');
  const [masterProblemId, setMasterProblemId] = useState('');
  const [userId, setUserId] = useState('reviewer_001');
  const [userRole, setUserRole] = useState('reviewer');

  // Payload fields for CORRECT action
  const [primaryDomain, setPrimaryDomain] = useState('Public Health');
  const [subcategory, setSubcategory] = useState('Sanitation Hazard');
  const [severity, setSeverity] = useState('HIGH');
  const [urgency, setUrgency] = useState('CRITICAL');

  const [loading, setLoading] = useState(false);
  const [inspector, setInspector] = useState<HTTPInspectorData | null>(null);
  const [result, setResult] = useState<{ problem: Problem; reviewRecord: any } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const activeActionObj = ACTION_TYPES.find((a) => a.id === selectedAction);

  const handleExecuteAction = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    let payloadObj: Record<string, any> | undefined = undefined;

    if (selectedAction === 'CORRECT') {
      payloadObj = {
        primaryDomain: primaryDomain.trim(),
        subcategory: subcategory.trim(),
        severity,
        urgency,
      };
    } else if (selectedAction === 'REDIRECT') {
      payloadObj = { targetJurisdiction: 'Municipal Water Board' };
    }

    const reqPayload = {
      action: selectedAction,
      reason: reason.trim() || undefined,
      masterProblemId: masterProblemId.trim() || undefined,
      payload: payloadObj,
    };

    const res = await backendApi.executeReviewerAction(
      problemId.trim(),
      reqPayload,
      userId.trim(),
      userRole.trim()
    );

    setInspector(res.inspector);

    if (res.data?.success && res.data?.data) {
      setResult(res.data.data);
    } else {
      setError(res.error || 'Reviewer action failed');
    }

    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <CheckSquare className="w-5 h-5 text-cyan-400" />
          <span>Human Reviewer Actions (`POST /api/reviewer/{'{problem_id}'}/action`)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Execute authorized human reviewer actions. AI microservices recommend; authorized reviewers own all consequential state transitions.
        </p>
      </div>

      <form onSubmit={handleExecuteAction} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Target Problem ID (Required)</label>
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
            <label className="block text-slate-300 font-semibold mb-1">X-User-ID (Reviewer Header)</label>
            <input
              type="text"
              required
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">X-User-Role (Reviewer Header)</label>
            <select
              value={userRole}
              onChange={(e) => setUserRole(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200"
            >
              <option value="reviewer">reviewer (Allowed)</option>
              <option value="admin">admin (Allowed)</option>
              <option value="citizen">citizen (FORBIDDEN 403)</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-slate-300 font-semibold mb-1">Select Reviewer Action</label>
          <select
            value={selectedAction}
            onChange={(e) => setSelectedAction(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-800 border border-cyan-700 font-bold text-slate-100"
          >
            {ACTION_TYPES.map((a) => (
              <option key={a.id} value={a.id}>{a.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-slate-300 font-semibold mb-1">
            Reviewer Justification Reason {activeActionObj?.reqReason ? '(Required for ' + selectedAction + ')' : '(Optional)'}
          </label>
          <input
            type="text"
            required={activeActionObj?.reqReason}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200"
          />
        </div>

        {/* Action Specific Input: MERGE_DUPLICATE */}
        {selectedAction === 'MERGE_DUPLICATE' && (
          <div className="p-3 rounded-lg bg-amber-950/60 border border-amber-800 space-y-2">
            <div className="font-bold text-amber-300 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4" />
              <span>MERGE_DUPLICATE Requirements</span>
            </div>
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Master Problem ID (Required)</label>
              <input
                type="text"
                required
                placeholder="e.g. P-MASTER-001"
                value={masterProblemId}
                onChange={(e) => setMasterProblemId(e.target.value)}
                className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-cyan-300 font-bold"
              />
            </div>
            <div className="text-[11px] text-amber-400/90 font-mono">
              Note: This links target problem {problemId || 'ID'} to master problem {masterProblemId || 'MASTER_ID'}. Original submission records are strictly preserved without deletion.
            </div>
          </div>
        )}

        {/* Action Specific Input: CORRECT */}
        {selectedAction === 'CORRECT' && (
          <div className="p-3 rounded-lg bg-purple-950/60 border border-purple-800 space-y-3">
            <div className="font-bold text-purple-300">
              CORRECT Payload Overrides (Creates NEW `source="reviewer"` ProblemVersion)
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Primary Domain</label>
                <input
                  type="text"
                  value={primaryDomain}
                  onChange={(e) => setPrimaryDomain(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Subcategory</label>
                <input
                  type="text"
                  value={subcategory}
                  onChange={(e) => setSubcategory(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Severity</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                >
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="CRITICAL">CRITICAL</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Urgency</label>
                <select
                  value={urgency}
                  onChange={(e) => setUrgency(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                >
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="CRITICAL">CRITICAL</option>
                </select>
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>{loading ? 'Executing Action...' : `Execute Action: ${selectedAction}`}</span>
          </button>
        </div>
      </form>

      {/* Action Execution Result */}
      {result && (
        <div className="p-5 rounded-xl bg-slate-900 border border-emerald-800/80 space-y-3 text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2 font-bold text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
              <span>Reviewer Action `{result.reviewRecord?.action}` Executed Successfully!</span>
            </div>
            <StatusBadge status={result.problem?.status} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="font-semibold text-slate-300 mb-1">Updated Problem Record</div>
              <JsonViewer data={result.problem} title="Updated Problem" />
            </div>

            <div>
              <div className="font-semibold text-slate-300 mb-1">Logged Review Record</div>
              <JsonViewer data={result.reviewRecord} title="Review Record" />
            </div>
          </div>
        </div>
      )}

      {inspector && <RequestResponseInspector inspector={inspector} />}
    </div>
  );
};
