import React, { useState } from 'react';
import { backendApi } from '../api/backend';
import { HTTPInspectorData, TestResultStatus } from '../types';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { TestResultBadge } from '../components/TestResultBadge';
import { ShieldCheck, Play, ShieldAlert, CheckCircle2, Lock } from 'lucide-react';

interface SecurityTestCase {
  id: string;
  name: string;
  targetRole: 'citizen' | 'reviewer' | 'admin' | 'government_official';
  endpoint: string;
  expectedStatus: number;
  actualStatus?: number;
  status: TestResultStatus;
  inspector?: HTTPInspectorData;
  notes: string;
}

export const SecurityRbacView: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [testCases, setTestCases] = useState<SecurityTestCase[]>([
    {
      id: 'SEC-1',
      name: 'Citizen header attempting to view Reviewer Queue',
      targetRole: 'citizen',
      endpoint: 'GET /api/reviewer/queue',
      expectedStatus: 403,
      status: 'NOT_RUN',
      notes: 'Citizen role must be rejected with HTTP 403 Forbidden.',
    },
    {
      id: 'SEC-2',
      name: 'Reviewer header viewing Reviewer Queue',
      targetRole: 'reviewer',
      endpoint: 'GET /api/reviewer/queue',
      expectedStatus: 200,
      status: 'NOT_RUN',
      notes: 'Reviewer role must be granted HTTP 200 OK.',
    },
    {
      id: 'SEC-3',
      name: 'Citizen header attempting Reviewer Action',
      targetRole: 'citizen',
      endpoint: 'POST /api/reviewer/P-SEC-TEST/action',
      expectedStatus: 403,
      status: 'NOT_RUN',
      notes: 'Citizen role attempting action must be rejected with 403 Forbidden.',
    },
    {
      id: 'SEC-4',
      name: 'Citizen header attempting Government Route',
      targetRole: 'citizen',
      endpoint: 'POST /api/government/P-SEC-TEST/route',
      expectedStatus: 403,
      status: 'NOT_RUN',
      notes: 'Citizen role attempting routing must be rejected with 403 Forbidden.',
    },
    {
      id: 'SEC-5',
      name: 'Government Official header attempting Government Route',
      targetRole: 'government_official',
      endpoint: 'POST /api/government/P-SEC-TEST/route',
      expectedStatus: 400, // 400 because P-SEC-TEST does not exist in store, but authorization checks pass!
      status: 'NOT_RUN',
      notes: 'Authorization check passes (returns 400 Bad Request due to missing problem, NOT 403 Forbidden).',
    },
  ]);

  const [selectedInspector, setSelectedInspector] = useState<HTTPInspectorData | null>(null);

  const runRbacSuite = async () => {
    setLoading(true);
    const updatedCases = [...testCases];

    for (let i = 0; i < updatedCases.length; i++) {
      const tc = updatedCases[i];
      let resInspector: HTTPInspectorData;
      let actualStatus = 0;

      if (tc.id === 'SEC-1') {
        const res = await backendApi.getReviewerQueue('citizen');
        resInspector = res.inspector;
        actualStatus = res.inspector.statusCode || 0;
      } else if (tc.id === 'SEC-2') {
        const res = await backendApi.getReviewerQueue('reviewer');
        resInspector = res.inspector;
        actualStatus = res.inspector.statusCode || 0;
      } else if (tc.id === 'SEC-3') {
        const res = await backendApi.executeReviewerAction('P-SEC-TEST', { action: 'ACCEPT' }, 'user_citizen', 'citizen');
        resInspector = res.inspector;
        actualStatus = res.inspector.statusCode || 0;
      } else if (tc.id === 'SEC-4') {
        const res = await backendApi.routeProblem('P-SEC-TEST', 'GOVERNMENT', 'user_citizen', 'citizen');
        resInspector = res.inspector;
        actualStatus = res.inspector.statusCode || 0;
      } else {
        const res = await backendApi.routeProblem('P-SEC-TEST', 'GOVERNMENT', 'user_official', 'government_official');
        resInspector = res.inspector;
        actualStatus = res.inspector.statusCode || 0;
      }

      tc.actualStatus = actualStatus;
      tc.inspector = resInspector;

      if (actualStatus === tc.expectedStatus) {
        tc.status = 'PASS';
      } else {
        tc.status = 'FAIL';
      }
    }

    setTestCases(updatedCases);
    setSelectedInspector(updatedCases[0].inspector || null);
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span>Development RBAC & Header Security Suite</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Tests header-based development authorization (`X-User-Role`). Verifies that protected API endpoints return HTTP 403 Forbidden for unauthorized citizen attempts.
          </p>
        </div>

        <button
          onClick={runRbacSuite}
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>{loading ? 'Running Security Matrix...' : 'Run Security Suite'}</span>
        </button>
      </div>

      {/* Test Matrix Table */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
        <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-3 flex items-center justify-between">
          <span>Role Authorization Test Matrix</span>
          <span className="text-[11px] font-mono text-slate-400">Header: `X-User-Role` Enforcement</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-sans">
            <thead>
              <tr className="border-b border-slate-800 font-mono text-slate-400">
                <th className="py-2.5 px-3">Test ID</th>
                <th className="py-2.5 px-3">Test Case Name</th>
                <th className="py-2.5 px-3">Role Header</th>
                <th className="py-2.5 px-3">Target Endpoint</th>
                <th className="py-2.5 px-3">Expected HTTP</th>
                <th className="py-2.5 px-3">Actual HTTP</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {testCases.map((tc) => (
                <tr key={tc.id} className="hover:bg-slate-800/40">
                  <td className="py-3 px-3 text-cyan-300 font-bold">{tc.id}</td>
                  <td className="py-3 px-3 font-sans text-slate-200 font-medium max-w-xs">{tc.name}</td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      tc.targetRole === 'citizen' ? 'bg-slate-800 text-slate-300' : 'bg-purple-950 text-purple-300 border border-purple-800'
                    }`}>
                      {tc.targetRole}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-300 text-[11px]">{tc.endpoint}</td>
                  <td className="py-3 px-3 text-slate-300 font-bold">HTTP {tc.expectedStatus}</td>
                  <td className="py-3 px-3 font-bold">
                    {tc.actualStatus ? (
                      <span className={tc.actualStatus === tc.expectedStatus ? 'text-emerald-400' : 'text-rose-400'}>
                        HTTP {tc.actualStatus}
                      </span>
                    ) : (
                      <span className="text-slate-500">-</span>
                    )}
                  </td>
                  <td className="py-3 px-3">
                    <TestResultBadge status={tc.status} />
                  </td>
                  <td className="py-3 px-3 text-right font-sans">
                    {tc.inspector && (
                      <button
                        onClick={() => setSelectedInspector(tc.inspector || null)}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-medium border border-slate-700"
                      >
                        Inspect
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedInspector && <RequestResponseInspector inspector={selectedInspector} />}
    </div>
  );
};
