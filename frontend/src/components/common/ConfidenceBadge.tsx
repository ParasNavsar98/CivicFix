import React from 'react';
import { Sparkles, AlertCircle, ShieldCheck } from 'lucide-react';

interface ConfidenceBadgeProps {
  confidence: number;
  showLabel?: boolean;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ confidence, showLabel = true }) => {
  const percent = Math.round(confidence * 100);

  if (confidence >= 0.85) {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-[#087F6B]/10 text-[#087F6B] border border-[#087F6B]/20">
        <ShieldCheck className="w-3.5 h-3.5 mr-1" />
        <span>{percent}%</span>
        {showLabel && <span className="ml-1 text-[10px] text-[#087F6B]">(High Confidence)</span>}
      </span>
    );
  }

  if (confidence >= 0.6) {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-[#B7791F]/10 text-[#B7791F] border border-[#B7791F]/20">
        <Sparkles className="w-3.5 h-3.5 mr-1" />
        <span>{percent}%</span>
        {showLabel && <span className="ml-1 text-[10px] text-[#B7791F]">(Needs Review)</span>}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-[#B83A3A]/10 text-[#B83A3A] border border-[#B83A3A]/20">
      <AlertCircle className="w-3.5 h-3.5 mr-1" />
      <span>{percent}%</span>
      {showLabel && <span className="ml-1 text-[10px] text-[#B83A3A]">(Low Confidence)</span>}
    </span>
  );
};
