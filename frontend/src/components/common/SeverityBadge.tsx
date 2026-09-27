import React from 'react';
import { SeverityLevel } from '../../types';
import { AlertCircle, AlertOctagon, Info, ShieldAlert } from 'lucide-react';

interface SeverityBadgeProps {
  severity: SeverityLevel;
  size?: 'sm' | 'md';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, size = 'md' }) => {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-semibold';

  const config: Record<SeverityLevel, { bg: string; text: string; border: string; icon: React.ReactNode }> = {
    CRITICAL: {
      bg: 'bg-[#B83A3A]/10',
      text: 'text-[#B83A3A]',
      border: 'border-[#B83A3A]/20',
      icon: <AlertOctagon className="w-3.5 h-3.5 mr-1" />,
    },
    HIGH: {
      bg: 'bg-[#B83A3A]/10',
      text: 'text-[#B83A3A]',
      border: 'border-[#B83A3A]/20',
      icon: <ShieldAlert className="w-3.5 h-3.5 mr-1" />,
    },
    MODERATE: {
      bg: 'bg-[#B7791F]/10',
      text: 'text-[#B7791F]',
      border: 'border-[#B7791F]/20',
      icon: <AlertCircle className="w-3.5 h-3.5 mr-1" />,
    },
    LOW: {
      bg: 'bg-[#0F766E]/10',
      text: 'text-[#0F766E]',
      border: 'border-[#0F766E]/20',
      icon: <Info className="w-3.5 h-3.5 mr-1" />,
    },
    NONE: {
      bg: 'bg-[#66736F]/10',
      text: 'text-[#66736F]',
      border: 'border-[#D8D8C8]',
      icon: <Info className="w-3.5 h-3.5 mr-1" />,
    },
    UNKNOWN: {
      bg: 'bg-[#66736F]/10',
      text: 'text-[#66736F]',
      border: 'border-[#D8D8C8]',
      icon: <Info className="w-3.5 h-3.5 mr-1" />,
    },
  };

  const item = config[severity] || config.MODERATE;

  return (
    <span className={`inline-flex items-center rounded-full border ${item.bg} ${item.text} ${item.border} ${sizeClasses}`}>
      {item.icon}
      <span>{severity}</span>
    </span>
  );
};
