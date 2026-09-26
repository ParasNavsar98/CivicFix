import React from 'react';
import { TestResultStatus } from '../types';
import { CheckCircle2, XCircle, AlertTriangle, MinusCircle, HelpCircle } from 'lucide-react';

interface TestBadgeProps {
  status: TestResultStatus;
}

export const TestResultBadge: React.FC<TestBadgeProps> = ({ status }) => {
  switch (status) {
    case 'PASS':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-700">
          <CheckCircle2 className="w-3.5 h-3.5" />
          PASS
        </span>
      );
    case 'FAIL':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-950 text-rose-400 border border-rose-700">
          <XCircle className="w-3.5 h-3.5" />
          FAIL
        </span>
      );
    case 'WARNING':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-950 text-amber-400 border border-amber-700">
          <AlertTriangle className="w-3.5 h-3.5" />
          WARNING
        </span>
      );
    case 'NOT_IMPLEMENTED':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-purple-950 text-purple-300 border border-purple-700">
          <HelpCircle className="w-3.5 h-3.5" />
          NOT IMPLEMENTED
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
          <MinusCircle className="w-3.5 h-3.5" />
          NOT RUN
        </span>
      );
  }
};
