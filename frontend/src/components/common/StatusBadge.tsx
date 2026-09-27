import React from 'react';
import { ProblemStatus } from '../../types';
import { CheckCircle2, Clock, AlertTriangle, ArrowRightCircle, Sparkles, Building2, BookOpen, Layers } from 'lucide-react';

interface StatusBadgeProps {
  status: ProblemStatus;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : size === 'lg' ? 'px-3.5 py-1 text-sm font-medium' : 'px-2.5 py-1 text-xs font-medium';

  const config: Record<ProblemStatus, { bg: string; text: string; border: string; icon: React.ReactNode }> = {
    Submitted: {
      bg: 'bg-[#6A5ACD]/10',
      text: 'text-[#6A5ACD]',
      border: 'border-[#6A5ACD]/20',
      icon: <Clock className="w-3.5 h-3.5 mr-1" />,
    },
    'AI Processing': {
      bg: 'bg-[#E9DFFF]',
      text: 'text-[#6A5ACD]',
      border: 'border-[#6A5ACD]/30',
      icon: <Sparkles className="w-3.5 h-3.5 mr-1 animate-pulse" />,
    },
    'Under Review': {
      bg: 'bg-[#B7791F]/10',
      text: 'text-[#B7791F]',
      border: 'border-[#B7791F]/20',
      icon: <AlertTriangle className="w-3.5 h-3.5 mr-1" />,
    },
    Validated: {
      bg: 'bg-[#087F6B]/10',
      text: 'text-[#087F6B]',
      border: 'border-[#087F6B]/20',
      icon: <CheckCircle2 className="w-3.5 h-3.5 mr-1" />,
    },
    'Routed Government': {
      bg: 'bg-[#034F46]/10',
      text: 'text-[#034F46]',
      border: 'border-[#034F46]/20',
      icon: <Building2 className="w-3.5 h-3.5 mr-1" />,
    },
    'Pending Match': {
      bg: 'bg-[#0F766E]/10',
      text: 'text-[#0F766E]',
      border: 'border-[#0F766E]/20',
      icon: <BookOpen className="w-3.5 h-3.5 mr-1" />,
    },
    'University Assigned': {
      bg: 'bg-[#E9DFFF]',
      text: 'text-[#6A5ACD]',
      border: 'border-[#6A5ACD]/30',
      icon: <ArrowRightCircle className="w-3.5 h-3.5 mr-1" />,
    },
    'In Progress': {
      bg: 'bg-[#0F766E]/15',
      text: 'text-[#034F46]',
      border: 'border-[#034F46]/20',
      icon: <Clock className="w-3.5 h-3.5 mr-1 animate-spin" />,
    },
    'Merged Duplicate': {
      bg: 'bg-[#66736F]/10',
      text: 'text-[#66736F]',
      border: 'border-[#D8D8C8]',
      icon: <Layers className="w-3.5 h-3.5 mr-1" />,
    },
    Resolved: {
      bg: 'bg-[#087F6B]/15',
      text: 'text-[#087F6B]',
      border: 'border-[#087F6B]/30',
      icon: <CheckCircle2 className="w-3.5 h-3.5 mr-1" />,
    },
    Rejected: {
      bg: 'bg-[#B83A3A]/10',
      text: 'text-[#B83A3A]',
      border: 'border-[#B83A3A]/20',
      icon: <AlertTriangle className="w-3.5 h-3.5 mr-1" />,
    },
  };

  const item = config[status] || config.Submitted;

  return (
    <span className={`inline-flex items-center rounded-full border font-semibold ${item.bg} ${item.text} ${item.border} ${sizeClasses}`}>
      {item.icon}
      <span>{status}</span>
    </span>
  );
};
