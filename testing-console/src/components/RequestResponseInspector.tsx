import React, { useState } from 'react';
import { HTTPInspectorData } from '../types';
import { JsonViewer } from './JsonViewer';
import { Clock, Globe, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';

interface Props {
  inspector?: HTTPInspectorData | null;
  title?: string;
}

export const RequestResponseInspector: React.FC<Props> = ({ inspector, title = 'HTTP Request / Response Inspector' }) => {
  const [activeTab, setActiveTab] = useState<'response' | 'request' | 'headers'>('response');

  if (!inspector) return null;

  const isSuccess = inspector.statusCode && inspector.statusCode >= 200 && inspector.statusCode < 300;

  return (
    <div className="border border-slate-700 bg-slate-900/90 rounded-lg overflow-hidden my-3 shadow-md">
      {/* Top Inspector Header */}
      <div className="flex flex-wrap items-center justify-between px-3 py-2 bg-slate-800 border-b border-slate-700 gap-2">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 rounded text-xs font-bold font-mono ${
            inspector.method === 'POST' ? 'bg-blue-900/80 text-blue-300 border border-blue-700' :
            inspector.method === 'GET' ? 'bg-emerald-900/80 text-emerald-300 border border-emerald-700' :
            'bg-amber-900/80 text-amber-300 border border-amber-700'
          }`}>
            {inspector.method}
          </span>
          <span className="font-mono text-xs text-slate-300 truncate max-w-md" title={inspector.url}>
            {inspector.url}
          </span>
        </div>

        <div className="flex items-center gap-3 text-xs">
          {inspector.statusCode !== undefined && (
            <span className={`flex items-center gap-1 font-mono font-bold px-2 py-0.5 rounded ${
              isSuccess ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'
            }`}>
              {isSuccess ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
              HTTP {inspector.statusCode === 0 ? 'FAIL' : inspector.statusCode}
            </span>
          )}

          {inspector.durationMs !== undefined && (
            <span className="flex items-center gap-1 text-slate-400 font-mono">
              <Clock className="w-3 h-3 text-cyan-400" />
              {inspector.durationMs} ms
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 bg-slate-900 text-xs px-2 pt-1 gap-1">
        <button
          onClick={() => setActiveTab('response')}
          className={`px-3 py-1.5 font-medium rounded-t transition-colors ${
            activeTab === 'response' ? 'bg-slate-800 text-cyan-400 border-t-2 border-cyan-400 font-semibold' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Response Body
        </button>
        <button
          onClick={() => setActiveTab('request')}
          className={`px-3 py-1.5 font-medium rounded-t transition-colors ${
            activeTab === 'request' ? 'bg-slate-800 text-cyan-400 border-t-2 border-cyan-400 font-semibold' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Request Body
        </button>
        <button
          onClick={() => setActiveTab('headers')}
          className={`px-3 py-1.5 font-medium rounded-t transition-colors ${
            activeTab === 'headers' ? 'bg-slate-800 text-cyan-400 border-t-2 border-cyan-400 font-semibold' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Request Headers
        </button>
      </div>

      {/* Tab Content */}
      <div className="p-2">
        {activeTab === 'response' && (
          <div>
            {inspector.error && (
              <div className="mb-2 p-2.5 rounded bg-rose-950/70 border border-rose-800 text-rose-300 text-xs flex items-start gap-2 font-mono">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold">Execution Error</div>
                  <div>{inspector.error}</div>
                </div>
              </div>
            )}
            <JsonViewer data={inspector.responseBody || (inspector.error ? { error: inspector.error } : { message: 'Empty Response' })} title="Response JSON" />
          </div>
        )}

        {activeTab === 'request' && (
          <JsonViewer data={inspector.requestBody || { message: 'No Request Body (GET/Empty)' }} title="Request Payload JSON" />
        )}

        {activeTab === 'headers' && (
          <JsonViewer data={inspector.headers || {}} title="HTTP Headers" />
        )}
      </div>
    </div>
  );
};
