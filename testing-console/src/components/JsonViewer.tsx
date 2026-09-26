import React, { useState } from 'react';
import { Check, Copy, ChevronDown, ChevronRight } from 'lucide-react';

interface JsonViewerProps {
  data: any;
  title?: string;
  defaultCollapsed?: boolean;
}

export const JsonViewer: React.FC<JsonViewerProps> = ({
  data,
  title = 'JSON Data',
  defaultCollapsed = false,
}) => {
  const [copied, setCopied] = useState(false);
  const [collapsed, setCollapsed] = useState(defaultCollapsed);

  const jsonString = typeof data === 'string'
    ? data
    : JSON.stringify(data, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900 text-slate-100 font-mono text-xs overflow-hidden my-2">
      <div className="flex items-center justify-between px-3 py-1.5 bg-slate-800/80 border-b border-slate-700">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center gap-1.5 text-slate-300 hover:text-white font-semibold"
        >
          {collapsed ? <ChevronRight className="w-3.5 h-3.5 text-slate-400" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-400" />}
          <span>{title}</span>
        </button>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-slate-400 hover:text-cyan-400 transition-colors px-2 py-0.5 rounded bg-slate-800"
          title="Copy raw JSON"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          <span className="text-[11px] font-sans">{copied ? 'Copied' : 'Copy JSON'}</span>
        </button>
      </div>

      {!collapsed && (
        <pre className="p-3 overflow-x-auto max-h-96 text-slate-300 font-mono leading-relaxed">
          {jsonString}
        </pre>
      )}
    </div>
  );
};
