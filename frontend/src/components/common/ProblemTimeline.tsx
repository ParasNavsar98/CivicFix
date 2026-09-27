import React from 'react';
import { WorkflowStage } from '../../types';
import { CheckCircle2, Circle, ArrowRight } from 'lucide-react';

interface ProblemTimelineProps {
  currentStage: WorkflowStage;
}

const STAGES: { key: WorkflowStage; label: string; desc: string }[] = [
  { key: 'CAPTURE', label: 'Capture', desc: 'Citizen Submission' },
  { key: 'UNDERSTAND', label: 'Understand', desc: 'AI Gemma 3 4B Analysis' },
  { key: 'VALIDATE', label: 'Validate', desc: 'Human Reviewer Check' },
  { key: 'ROUTE', label: 'Route', desc: 'Govt / Research Pathway' },
  { key: 'MATCH', label: 'Match', desc: '7-Factor University Matching' },
  { key: 'COLLABORATE', label: 'Collaborate', desc: 'Industry & Resource Support' },
  { key: 'IMPLEMENT', label: 'Implement', desc: 'Project Execution & Testing' },
  { key: 'MEASURE', label: 'Measure', desc: 'Impact Audit & Resolution' },
];

export const ProblemTimeline: React.FC<ProblemTimelineProps> = ({ currentStage }) => {
  const currentIndex = STAGES.findIndex((s) => s.key === currentStage);
  const activeIndex = currentIndex === -1 ? 2 : currentIndex;

  return (
    <div className="glass-card rounded-2xl p-6">
      <h4 className="text-xs font-semibold text-[#66736F] uppercase tracking-wider mb-6 flex items-center gap-2">
        <ArrowRight className="w-4 h-4 text-[#6A5ACD]" /> CivicFix Problem Lifecycle Progress
      </h4>

      {/* Desktop Horizontal Stepper */}
      <div className="hidden md:flex items-start justify-between relative">
        {/* Connecting Line */}
        <div className="absolute top-4 left-6 right-6 h-0.5 bg-[#D8D8C8] -z-0" />
        <div
          className="absolute top-4 left-6 h-0.5 bg-gradient-to-r from-[#034F46] via-[#0F766E] to-[#6A5ACD] transition-all duration-700 -z-0"
          style={{ width: `${(activeIndex / (STAGES.length - 1)) * 92}%` }}
        />

        {STAGES.map((stage, idx) => {
          const isCompleted = idx < activeIndex;
          const isCurrent = idx === activeIndex;

          return (
            <div key={stage.key} className="flex flex-col items-center text-center relative z-10 w-24">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                  isCompleted
                    ? 'bg-[#087F6B] text-white shadow-sm'
                    : isCurrent
                    ? 'bg-[#034F46] text-white ring-4 ring-[#034F46]/20 shadow-md animate-pulse'
                    : 'bg-[#F7F5E8] text-[#66736F] border border-[#D8D8C8]'
                }`}
              >
                {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : idx + 1}
              </div>
              <span className={`text-xs font-semibold mt-3.5 ${isCurrent ? 'text-[#17332F]' : isCompleted ? 'text-[#087F6B]' : 'text-[#66736F]'}`}>
                {stage.label}
              </span>
              <span className="text-[10px] text-[#66736F] mt-0.5 line-clamp-1">{stage.desc}</span>
            </div>
          );
        })}
      </div>

      {/* Mobile Vertical Stepper */}
      <div className="flex md:hidden flex-col gap-4 relative">
        {STAGES.map((stage, idx) => {
          const isCompleted = idx < activeIndex;
          const isCurrent = idx === activeIndex;

          return (
            <div key={stage.key} className="flex items-center gap-3">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                  isCompleted
                    ? 'bg-[#087F6B] text-white'
                    : isCurrent
                    ? 'bg-[#034F46] text-white ring-2 ring-[#0F766E]'
                    : 'bg-[#F7F5E8] text-[#66736F] border border-[#D8D8C8]'
                }`}
              >
                {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
              </div>
              <div>
                <span className={`text-xs font-semibold block ${isCurrent ? 'text-[#17332F]' : isCompleted ? 'text-[#087F6B]' : 'text-[#66736F]'}`}>
                  {stage.label}
                </span>
                <span className="text-[10px] text-[#66736F]">{stage.desc}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
