import React from 'react';

interface StatusBadgeProps {
  status?: string | null;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  if (!status) {
    return <span className="text-slate-500 font-mono text-xs">-</span>;
  }

  const s = status.toUpperCase();

  let colors = 'bg-slate-800 text-slate-300 border-slate-700';

  if (s === 'SUBMITTED') {
    colors = 'bg-blue-950 text-blue-300 border-blue-700';
  } else if (s === 'AI_PROCESSING') {
    colors = 'bg-purple-950 text-purple-300 border-purple-700 animate-pulse';
  } else if (s === 'REVIEW_REQUIRED') {
    colors = 'bg-amber-950 text-amber-300 border-amber-600 font-bold';
  } else if (s === 'VALIDATED') {
    colors = 'bg-emerald-950 text-emerald-300 border-emerald-700';
  } else if (s.startsWith('ROUTED_')) {
    colors = 'bg-cyan-950 text-cyan-300 border-cyan-700';
  } else if (s === 'PENDING_MATCH') {
    colors = 'bg-indigo-950 text-indigo-300 border-indigo-700';
  } else if (s === 'MERGED_DUPLICATE') {
    colors = 'bg-slate-900 text-slate-400 border-slate-600 line-through';
  } else if (s === 'REJECTED') {
    colors = 'bg-rose-950 text-rose-300 border-rose-700';
  } else if (s === 'PENDING_CLARIFICATION') {
    colors = 'bg-yellow-950 text-yellow-300 border-yellow-700';
  }

  return (
    <span className={`inline-block px-2.5 py-0.5 rounded text-xs font-mono font-semibold border ${colors}`}>
      {status}
    </span>
  );
};
