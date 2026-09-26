import React, { useState } from 'react';
import { backendApi } from '../api/backend';
import { AuditEvent, HTTPInspectorData } from '../types';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { JsonViewer } from '../components/JsonViewer';
import { FileSearch, Search, Lock } from 'lucide-react';

export const AuditView: React.FC = () => {
  const [entityId, setEntityId] = useState('');
  const [loading, setLoading] = useState(false);
  const [inspector, setInspector] = useState<HTTPInspectorData | null>(null);
  const [events, setEvents] = useState<AuditEvent[]>([]);

  const handleFetchAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!entityId.trim()) return;
    setLoading(true);
    setEvents([]);

    const res = await backendApi.getAuditTrail(entityId.trim());
    setInspector(res.inspector);

    if (res.data?.success && res.data?.data?.events) {
      setEvents(res.data.data.events);
    }

    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <FileSearch className="w-5 h-5 text-purple-400" />
          <span>Append-Only Audit Log Viewer (`GET /api/audit/{'{entity_id}'}`)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Surfaces immutable append-only audit trail logs capturing all system and human state transitions. No update or delete operations exist.
        </p>
      </div>

      <form onSubmit={handleFetchAudit} className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-end gap-3 text-xs">
        <div className="flex-1 min-w-[250px]">
          <label className="block text-slate-300 font-semibold mb-1">Target Entity ID (Problem ID)</label>
          <input
            type="text"
            required
            placeholder="e.g. P-TEST-001"
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-purple-300 font-bold focus:outline-none focus:border-purple-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2.5 rounded bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
        >
          <Search className="w-4 h-4" />
          <span>{loading ? 'Fetching Audit Trail...' : 'Load Audit Trail'}</span>
        </button>
      </form>

      {/* Audit Log Table */}
      {events.length > 0 && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Lock className="w-4 h-4 text-emerald-400" />
              <span>Immutable Audit Trail Events ({events.length})</span>
            </h3>
            <span className="text-[11px] font-mono text-slate-400">Strictly Append-Only</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left font-sans">
              <thead>
                <tr className="border-b border-slate-800 font-mono text-slate-400">
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Event Action</th>
                  <th className="py-2.5 px-3">Actor (Role)</th>
                  <th className="py-2.5 px-3">Prev State → New State</th>
                  <th className="py-2.5 px-3">Metadata</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {events.map((ev) => (
                  <tr key={ev.eventId} className="hover:bg-slate-800/40">
                    <td className="py-3 px-3 text-slate-400 text-[11px] whitespace-nowrap">{ev.timestamp}</td>
                    <td className="py-3 px-3 text-purple-300 font-bold">{ev.action}</td>
                    <td className="py-3 px-3 text-slate-300">
                      {ev.actorId} <span className="text-slate-500 font-normal">({ev.actorRole})</span>
                    </td>
                    <td className="py-3 px-3 text-slate-300 text-[11px]">
                      {ev.previousState || 'None'} → <strong className="text-cyan-300">{ev.newState || 'Same'}</strong>
                    </td>
                    <td className="py-3 px-3 text-slate-400 text-[11px] max-w-xs truncate">
                      {JSON.stringify(ev.metadata)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <JsonViewer data={events} title="Complete Audit Log Array JSON" />
        </div>
      )}

      {inspector && <RequestResponseInspector inspector={inspector} />}
    </div>
  );
};
