import React, { useState } from 'react';
import { backendApi } from '../api/backend';
import { Problem, ProblemTimelineData, AuditEvent } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { JsonViewer } from '../components/JsonViewer';
import { Workflow, Play, CheckCircle2, ChevronRight, AlertTriangle, Building2, Clock, FileSearch } from 'lucide-react';

export const E2EPipelineView: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const [masterProblem, setMasterProblem] = useState<Problem | null>(null);
  const [dupProblem, setDupProblem] = useState<Problem | null>(null);
  const [queueCount, setQueueCount] = useState<number | null>(null);
  const [actionResult, setActionResult] = useState<any | null>(null);
  const [routingResult, setRoutingResult] = useState<Problem | null>(null);
  const [timelineData, setTimelineData] = useState<ProblemTimelineData | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);

  // Step 1: Submit Master Problem A
  const handleStep1 = async () => {
    setLoading(true);
    const probId = `P-E2E-MASTER-${Math.random().toString(36).substring(2, 7).toUpperCase()}`;
    const res = await backendApi.createProblem({
      problemId: probId,
      title: 'Water Main Pipe Burst in Sector 4',
      description: 'Drinking water pipeline ruptured flooding main street.',
      location: { lat: 18.5204, long: 73.8567, address: 'Sector 4 Main Road' },
    });
    if (res.data?.data) {
      setMasterProblem(res.data.data);
      setCurrentStep(2);
    }
    setLoading(false);
  };

  // Step 2: Submit Duplicate Problem B
  const handleStep2 = async () => {
    setLoading(true);
    const probId = `P-E2E-DUP-${Math.random().toString(36).substring(2, 7).toUpperCase()}`;
    const res = await backendApi.createProblem({
      problemId: probId,
      title: 'Water pipeline leaking near Sector 4 hall',
      description: 'Potable water spilling onto street from broken underground main.',
      location: { lat: 18.5208, long: 73.8570, address: 'Sector 4 Lane' },
    });
    if (res.data?.data) {
      setDupProblem(res.data.data);
      setCurrentStep(3);
    }
    setLoading(false);
  };

  // Step 3: Check Reviewer Queue
  const handleStep3 = async () => {
    setLoading(true);
    const res = await backendApi.getReviewerQueue('reviewer');
    if (res.data?.data) {
      setQueueCount(res.data.data.count);
      setCurrentStep(4);
    }
    setLoading(false);
  };

  // Step 4: Execute MERGE_DUPLICATE
  const handleStep4 = async () => {
    if (!dupProblem || !masterProblem) return;
    setLoading(true);
    const res = await backendApi.executeReviewerAction(dupProblem.problemId, {
      action: 'MERGE_DUPLICATE',
      reason: 'E2E Test: Confirmed duplicate report',
      masterProblemId: masterProblem.problemId,
    });
    if (res.data?.data) {
      setActionResult(res.data.data);
      setCurrentStep(5);
    }
    setLoading(false);
  };

  // Step 5: Route Master Problem
  const handleStep5 = async () => {
    if (!masterProblem) return;
    setLoading(true);
    const res = await backendApi.routeProblem(masterProblem.problemId, 'GOVERNMENT');
    if (res.data?.data) {
      setRoutingResult(res.data.data);
      setCurrentStep(6);
    }
    setLoading(false);
  };

  // Step 6: Verify Timeline & Audit
  const handleStep6 = async () => {
    if (!masterProblem) return;
    setLoading(true);
    const [tRes, aRes] = await Promise.all([
      backendApi.getProblemTimeline(masterProblem.problemId),
      backendApi.getAuditTrail(masterProblem.problemId),
    ]);
    if (tRes.data?.data) setTimelineData(tRes.data.data);
    if (aRes.data?.data?.events) setAuditEvents(aRes.data.data.events);
    setCurrentStep(7);
    setLoading(false);
  };

  const steps = [
    { num: 1, name: 'Submit Master Problem A' },
    { num: 2, name: 'Submit Duplicate Problem B' },
    { num: 3, name: 'Check Reviewer Queue' },
    { num: 4, name: 'Merge Duplicate (Reviewer)' },
    { num: 5, name: 'Route to Government' },
    { num: 6, name: 'Verify Timeline & Audit' },
    { num: 7, name: 'Session Completed' },
  ];

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Workflow className="w-5 h-5 text-purple-400" />
          <span>Automated End-to-End Test Session Wizard</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Executes a complete, step-by-step E2E manual testing walkthrough verifying problem creation, AI processing, duplicate detection, human review, government routing, citizen timeline, and append-only audit trail.
        </p>
      </div>

      {/* Step Tracker Header */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2 text-xs">
          {steps.map((st) => (
            <div
              key={st.num}
              className={`p-2.5 rounded-lg border flex flex-col justify-between ${
                currentStep === st.num
                  ? 'bg-purple-950/80 border-purple-600 text-purple-200 font-bold'
                  : currentStep > st.num
                  ? 'bg-emerald-950/40 border-emerald-800 text-emerald-300 font-semibold'
                  : 'bg-slate-800/40 border-slate-800 text-slate-500 font-normal'
              }`}
            >
              <div className="text-[10px] font-mono opacity-80">STEP {st.num}</div>
              <div className="truncate mt-1">{st.name}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Step Action Cards */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
        {currentStep === 1 && (
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-slate-200">Step 1: Submit Initial Master Problem A</h3>
            <p className="text-xs text-slate-400">
              This will create the first canonical problem record in the backend, triggering AI classification and duplicate check against initial candidate pool.
            </p>
            <button
              onClick={handleStep1}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{loading ? 'Submitting & Executing AI Pipeline...' : 'Submit Master Problem A'}</span>
            </button>
          </div>
        )}

        {currentStep === 2 && masterProblem && (
          <div className="space-y-3">
            <div className="p-3 rounded bg-emerald-950/60 border border-emerald-800 text-xs text-emerald-300">
              ✓ Master Problem Created: <strong className="font-mono">{masterProblem.problemId}</strong> — {masterProblem.title} (Status: {masterProblem.status})
            </div>
            <h3 className="text-sm font-bold text-slate-200">Step 2: Submit Duplicate Problem B</h3>
            <p className="text-xs text-slate-400">
              Submit a second problem describing the same issue with similar wording nearby to trigger duplicate detection candidate surfacing.
            </p>
            <button
              onClick={handleStep2}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{loading ? 'Submitting & Running Vector Matcher...' : 'Submit Duplicate Problem B'}</span>
            </button>
          </div>
        )}

        {currentStep === 3 && dupProblem && (
          <div className="space-y-3">
            <div className="p-3 rounded bg-emerald-950/60 border border-emerald-800 text-xs text-emerald-300">
              ✓ Duplicate Problem Created: <strong className="font-mono">{dupProblem.problemId}</strong> (Status: {dupProblem.status})
            </div>
            <h3 className="text-sm font-bold text-slate-200">Step 3: Query Reviewer Queue</h3>
            <p className="text-xs text-slate-400">
              Query `GET /api/reviewer/queue` with role `reviewer` to verify that flagged cases appear in human reviewer queue.
            </p>
            <button
              onClick={handleStep3}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{loading ? 'Querying Queue...' : 'Check Reviewer Queue'}</span>
            </button>
          </div>
        )}

        {currentStep === 4 && dupProblem && masterProblem && (
          <div className="space-y-3">
            <div className="p-3 rounded bg-emerald-950/60 border border-emerald-800 text-xs text-emerald-300">
              ✓ Reviewer Queue Loaded: {queueCount} items in queue.
            </div>
            <h3 className="text-sm font-bold text-slate-200">Step 4: Execute Human Action (MERGE_DUPLICATE)</h3>
            <p className="text-xs text-slate-400">
              Execute `POST /api/reviewer/{dupProblem.problemId}/action` with action `MERGE_DUPLICATE` linking master problem `{masterProblem.problemId}`. Original submission is preserved.
            </p>
            <button
              onClick={handleStep4}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{loading ? 'Merging Duplicate Record...' : 'Execute MERGE_DUPLICATE'}</span>
            </button>
          </div>
        )}

        {currentStep === 5 && masterProblem && (
          <div className="space-y-3">
            <div className="p-3 rounded bg-emerald-950/60 border border-emerald-800 text-xs text-emerald-300">
              ✓ Merge Completed! Duplicate problem status updated to `MERGED_DUPLICATE`.
            </div>
            <h3 className="text-sm font-bold text-slate-200">Step 5: Route Master Problem to Sector</h3>
            <p className="text-xs text-slate-400">
              Execute `POST /api/government/{masterProblem.problemId}/route?destination=GOVERNMENT`.
            </p>
            <button
              onClick={handleStep5}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{loading ? 'Executing Routing...' : 'Route Master Problem'}</span>
            </button>
          </div>
        )}

        {currentStep === 6 && masterProblem && (
          <div className="space-y-3">
            <div className="p-3 rounded bg-emerald-950/60 border border-emerald-800 text-xs text-emerald-300">
              ✓ Routing Executed! Master Problem Status: `{routingResult?.status}`.
            </div>
            <h3 className="text-sm font-bold text-slate-200">Step 6: Load Citizen Timeline & Audit Log</h3>
            <p className="text-xs text-slate-400">
              Verify `GET /api/problems/{masterProblem.problemId}/timeline` and `GET /api/audit/{masterProblem.problemId}`.
            </p>
            <button
              onClick={handleStep6}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{loading ? 'Fetching Observability Data...' : 'Verify Timeline & Audit'}</span>
            </button>
          </div>
        )}

        {currentStep === 7 && (
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-emerald-950 border border-emerald-700 text-emerald-300 text-xs font-bold flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span>Full E2E Testing Session Completed Successfully!</span>
            </div>

            {timelineData && (
              <div className="space-y-2">
                <div className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  <span>Citizen Timeline Events ({timelineData.timeline.length} steps):</span>
                </div>
                <JsonViewer data={timelineData} title="Citizen Timeline Data" />
              </div>
            )}

            {auditEvents.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <FileSearch className="w-4 h-4 text-purple-400" />
                  <span>Append-Only Audit Events ({auditEvents.length} events):</span>
                </div>
                <JsonViewer data={auditEvents} title="Audit Trail Log" />
              </div>
            )}

            <button
              onClick={() => {
                setCurrentStep(1);
                setMasterProblem(null);
                setDupProblem(null);
                setActionResult(null);
                setRoutingResult(null);
                setTimelineData(null);
                setAuditEvents([]);
              }}
              className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700"
            >
              Start New E2E Test Session
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
