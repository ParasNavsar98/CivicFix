import React, { useEffect, useState } from 'react';
import { backendApi } from '../api/backend';
import { classificationApi } from '../api/classification';
import { duplicateApi } from '../api/duplicate';
import { ollamaApi } from '../api/ollama';
import { Problem, ReviewerQueueItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { NavTab } from '../components/Sidebar';
import {
  Activity,
  Server,
  Cpu,
  Layers,
  Database,
  ArrowRight,
  Inbox,
  Workflow,
  CheckCircle2,
  AlertTriangle,
  PlayCircle,
  FileText,
} from 'lucide-react';

interface Props {
  onNavigate: (tab: NavTab) => void;
}

export const DashboardView: React.FC<Props> = ({ onNavigate }) => {
  const [bHealth, setBHealth] = useState<string>('Checking...');
  const [cHealth, setCHealth] = useState<string>('Checking...');
  const [dHealth, setDHealth] = useState<string>('Checking...');
  const [oHealth, setOHealth] = useState<string>('Checking...');

  const [queueItems, setQueueItems] = useState<ReviewerQueueItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const [b, c, d, o, q] = await Promise.all([
        backendApi.getHealth(),
        classificationApi.getHealth(),
        duplicateApi.getHealth(),
        ollamaApi.getHealth(),
        backendApi.getReviewerQueue('reviewer'),
      ]);

      setBHealth(b.data?.status === 'ok' ? 'ONLINE' : 'OFFLINE');
      setCHealth(c.data?.status === 'healthy' ? 'ONLINE' : 'OFFLINE');
      setDHealth(d.data?.status === 'ok' || d.data?.status === 'healthy' ? 'ONLINE' : 'OFFLINE');
      setOHealth(o.data?.models ? 'ONLINE' : 'OFFLINE');

      if (q.data?.data?.queue) {
        setQueueItems(q.data.data.queue);
      }
      setLoading(false);
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-lg flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            CivicFix Integration Dashboard
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Real-time observability dashboard for testing the integrated CivicFix backend state machine,
            FastAPI microservices, Ollama LLM, and SentenceTransformers duplicate engine.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onNavigate('problem-test')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md transition-colors"
          >
            <PlayCircle className="w-4 h-4" />
            <span>Test Real Problem</span>
          </button>
          <button
            onClick={() => onNavigate('e2e-pipeline')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-md transition-colors"
          >
            <Workflow className="w-4 h-4" />
            <span>Launch E2E Session</span>
          </button>
        </div>
      </div>

      {/* 4 Service Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Main Backend</div>
            <div className="text-lg font-bold font-mono text-slate-100 mt-0.5">{bHealth}</div>
            <div className="text-[11px] text-slate-500 font-mono mt-1">Port 8002 • FastAPI</div>
          </div>
          <div className={`p-3 rounded-xl ${bHealth === 'ONLINE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'}`}>
            <Server className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">AI Classification</div>
            <div className="text-lg font-bold font-mono text-slate-100 mt-0.5">{cHealth}</div>
            <div className="text-[11px] text-slate-500 font-mono mt-1">Port 8000 • Gemma 3 4B</div>
          </div>
          <div className={`p-3 rounded-xl ${cHealth === 'ONLINE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'}`}>
            <Cpu className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Duplicate Detection</div>
            <div className="text-lg font-bold font-mono text-slate-100 mt-0.5">{dHealth}</div>
            <div className="text-[11px] text-slate-500 font-mono mt-1">Port 8001 • BGE-small</div>
          </div>
          <div className={`p-3 rounded-xl ${dHealth === 'ONLINE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'}`}>
            <Layers className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Ollama Inference</div>
            <div className="text-lg font-bold font-mono text-slate-100 mt-0.5">{oHealth}</div>
            <div className="text-[11px] text-slate-500 font-mono mt-1">Port 11434 • LLM Engine</div>
          </div>
          <div className={`p-3 rounded-xl ${oHealth === 'ONLINE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'}`}>
            <Database className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Reviewer Queue Summary & Core Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Pending Review Queue Preview */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Inbox className="w-4 h-4 text-amber-400" />
              <span>Reviewer Queue Overview</span>
              <span className="px-2 py-0.5 rounded-full bg-amber-950 text-amber-300 border border-amber-800 text-xs font-mono">
                {queueItems.length} Flagged
              </span>
            </h3>
            <button
              onClick={() => onNavigate('reviewer-queue')}
              className="text-xs text-cyan-400 hover:underline flex items-center gap-1 font-medium"
            >
              <span>View Queue</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {loading ? (
            <div className="text-xs text-slate-400 py-6 text-center animate-pulse">
              Loading reviewer queue data...
            </div>
          ) : queueItems.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-500">
              <CheckCircle2 className="w-8 h-8 text-slate-700 mx-auto mb-2" />
              <div>No problems currently pending in reviewer queue.</div>
              <div className="text-[11px] text-slate-600 mt-1">Submit a test problem with low confidence or duplicate wording to trigger review.</div>
            </div>
          ) : (
            <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
              {queueItems.map((item) => (
                <div key={item.problem.problemId} className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/80 flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <div className="font-semibold text-slate-200 text-xs flex items-center gap-2">
                      <span>{item.problem.title}</span>
                      <span className="text-[10px] font-mono text-slate-400 font-normal">({item.problem.problemId})</span>
                    </div>
                    <div className="text-[11px] text-amber-400/90 mt-1 flex items-center gap-1 font-mono">
                      <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
                      <span>{item.problem.reviewReasons?.join(', ') || 'Requires review'}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={item.problem.status} />
                    <button
                      onClick={() => onNavigate('reviewer-actions')}
                      className="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-medium"
                    >
                      Review
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Quick Action Cards */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-3">
            Quick Testing Navigation
          </h3>

          <button
            onClick={() => onNavigate('classification-lab')}
            className="w-full text-left p-3 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/80 transition-colors group"
          >
            <div className="font-semibold text-xs text-slate-200 group-hover:text-cyan-400 flex items-center justify-between">
              <span>Classification Lab</span>
              <Cpu className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Test taxonomy, confidence & severity formatting directly.</div>
          </button>

          <button
            onClick={() => onNavigate('duplicate-lab')}
            className="w-full text-left p-3 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/80 transition-colors group"
          >
            <div className="font-semibold text-xs text-slate-200 group-hover:text-purple-400 flex items-center justify-between">
              <span>Duplicate Detection Lab</span>
              <Layers className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Compare Problem A vs Problem B semantic similarity scores.</div>
          </button>

          <button
            onClick={() => onNavigate('security')}
            className="w-full text-left p-3 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/80 transition-colors group"
          >
            <div className="font-semibold text-xs text-slate-200 group-hover:text-emerald-400 flex items-center justify-between">
              <span>Security & RBAC Matrix</span>
              <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Test header-based authorization for citizens vs reviewers.</div>
          </button>
        </div>
      </div>
    </div>
  );
};
