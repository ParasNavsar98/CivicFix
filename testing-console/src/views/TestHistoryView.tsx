import React, { useEffect, useState } from 'react';
import { TestResultRecord } from '../types';
import { TestResultBadge } from '../components/TestResultBadge';
import { History, Trash2, Search } from 'lucide-react';

const HISTORY_STORAGE_KEY = 'civicfix_test_history_logs';

export function addTestHistoryRecord(record: Omit<TestResultRecord, 'id' | 'timestamp'>) {
  try {
    const existingStr = localStorage.getItem(HISTORY_STORAGE_KEY);
    const history: TestResultRecord[] = existingStr ? JSON.parse(existingStr) : [];

    const newRecord: TestResultRecord = {
      ...record,
      id: `TH-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
      timestamp: new Date().toLocaleTimeString(),
    };

    history.unshift(newRecord);
    // Limit to last 50 entries
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history.slice(0, 50)));
  } catch (e) {
    console.error('Error writing test history:', e);
  }
}

export const TestHistoryView: React.FC = () => {
  const [history, setHistory] = useState<TestResultRecord[]>([]);
  const [filter, setFilter] = useState<'ALL' | 'PASS' | 'FAIL' | 'WARNING'>('ALL');

  const loadHistory = () => {
    try {
      const saved = localStorage.getItem(HISTORY_STORAGE_KEY);
      if (saved) {
        setHistory(JSON.parse(saved));
      } else {
        setHistory([]);
      }
    } catch {
      setHistory([]);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleClearHistory = () => {
    localStorage.removeItem(HISTORY_STORAGE_KEY);
    setHistory([]);
  };

  const filteredItems = history.filter((h) => {
    if (filter === 'ALL') return true;
    return h.status === filter;
  });

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" />
            <span>Local Browser Test History Log</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Browser-side execution history stored in localStorage for tracking manual test runs.
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1 font-mono">
            <button
              onClick={() => setFilter('ALL')}
              className={`px-2.5 py-1 rounded ${filter === 'ALL' ? 'bg-slate-700 text-white font-bold' : 'text-slate-400 hover:text-slate-200'}`}
            >
              All ({history.length})
            </button>
            <button
              onClick={() => setFilter('PASS')}
              className={`px-2.5 py-1 rounded ${filter === 'PASS' ? 'bg-emerald-950 text-emerald-400 font-bold border border-emerald-800' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Pass
            </button>
            <button
              onClick={() => setFilter('FAIL')}
              className={`px-2.5 py-1 rounded ${filter === 'FAIL' ? 'bg-rose-950 text-rose-400 font-bold border border-rose-800' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Fail
            </button>
          </div>

          <button
            onClick={handleClearHistory}
            className="flex items-center gap-1 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700"
          >
            <Trash2 className="w-3.5 h-3.5 text-rose-400" />
            <span>Clear Logs</span>
          </button>
        </div>
      </div>

      {/* History Table */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-4">
        {filteredItems.length === 0 ? (
          <div className="py-10 text-center text-slate-500 font-mono">
            No test execution history recorded yet. Perform problem submissions or security tests to log runs.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-sans">
              <thead>
                <tr className="border-b border-slate-800 font-mono text-slate-400">
                  <th className="py-2.5 px-3">Time</th>
                  <th className="py-2.5 px-3">Test Name</th>
                  <th className="py-2.5 px-3">Endpoint</th>
                  <th className="py-2.5 px-3">Status Code</th>
                  <th className="py-2.5 px-3">Duration</th>
                  <th className="py-2.5 px-3">Result</th>
                  <th className="py-2.5 px-3">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/40">
                    <td className="py-3 px-3 text-slate-400 text-[11px] whitespace-nowrap">{item.timestamp}</td>
                    <td className="py-3 px-3 font-sans text-slate-200 font-medium">{item.testName}</td>
                    <td className="py-3 px-3 text-cyan-300 text-[11px]">{item.endpoint || '-'}</td>
                    <td className="py-3 px-3 text-slate-300">{item.statusCode || '-'}</td>
                    <td className="py-3 px-3 text-slate-400">{item.durationMs ? `${item.durationMs}ms` : '-'}</td>
                    <td className="py-3 px-3">
                      <TestResultBadge status={item.status} />
                    </td>
                    <td className="py-3 px-3 text-slate-400 text-[11px] max-w-xs truncate">{item.notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
