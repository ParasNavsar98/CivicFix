import React from 'react';
import { ClassificationResult } from '../../types';
import { Sparkles, ShieldCheck, Check } from 'lucide-react';
import { ConfidenceBadge } from './ConfidenceBadge';

interface AIInsightCardProps {
  classification: ClassificationResult;
  onAccept?: () => void;
  onCorrect?: () => void;
  showActions?: boolean;
}

export const AIInsightCard: React.FC<AIInsightCardProps> = ({
  classification,
  onAccept,
  onCorrect,
  showActions = false,
}) => {
  return (
    <div className="glass-card rounded-2xl p-6 border border-[#6A5ACD]/30 relative overflow-hidden bg-gradient-to-b from-[#E9DFFF]/40 via-[#FFFDF5] to-[#FFFDF5]">
      {/* Top Header & AI Label */}
      <div className="flex items-center justify-between pb-4 border-b border-[#D8D8C8]">
        <div className="flex items-center gap-2">
          <span className="p-2 rounded-lg bg-[#6A5ACD]/10 text-[#6A5ACD] border border-[#6A5ACD]/20">
            <Sparkles className="w-4 h-4 animate-pulse" />
          </span>
          <div>
            <h4 className="text-sm font-bold text-[#17332F] flex items-center gap-2">
              AI-Assisted Understanding
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#E9DFFF] text-[#6A5ACD] border border-[#6A5ACD]/20">
                Gemma 3 4B
              </span>
            </h4>
            <p className="text-xs text-[#66736F]">Structured analysis derived from citizen text input</p>
          </div>
        </div>

        <ConfidenceBadge confidence={classification.confidence} />
      </div>

      {/* Main Grid Findings */}
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-[#F7F5E8] p-3.5 rounded-xl border border-[#D8D8C8]">
          <div className="text-[11px] font-bold text-[#66736F] uppercase tracking-wider">Primary Domain</div>
          <div className="text-base font-extrabold text-[#034F46] mt-1">{classification.primaryDomain}</div>
        </div>

        <div className="bg-[#F7F5E8] p-3.5 rounded-xl border border-[#D8D8C8]">
          <div className="text-[11px] font-bold text-[#66736F] uppercase tracking-wider">Subcategory</div>
          <div className="text-base font-extrabold text-[#0F766E] mt-1">{classification.subcategory}</div>
        </div>

        <div className="bg-[#F7F5E8] p-3.5 rounded-xl border border-[#D8D8C8]">
          <div className="text-[11px] font-bold text-[#66736F] uppercase tracking-wider">Secondary Domains</div>
          <div className="flex flex-wrap gap-1 mt-1">
            {classification.secondaryDomains && classification.secondaryDomains.length > 0 ? (
              classification.secondaryDomains.map((d) => (
                <span key={d} className="text-xs px-2 py-0.5 rounded-md bg-[#E9DFFF] text-[#6A5ACD] border border-[#6A5ACD]/20 font-semibold">
                  {d}
                </span>
              ))
            ) : (
              <span className="text-xs text-[#66736F]">None detected</span>
            )}
          </div>
        </div>
      </div>

      {/* Reasoning & Evidence */}
      {classification.reasoning && (
        <div className="mt-4 bg-[#F7F5E8] p-3.5 rounded-xl border border-[#D8D8C8]">
          <div className="text-[11px] font-bold text-[#66736F] uppercase tracking-wider mb-1">AI Reasoning</div>
          <p className="text-xs text-[#17332F] leading-relaxed">{classification.reasoning}</p>
        </div>
      )}

      {/* Required Expertise & Resources */}
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
        {classification.requiredExpertise && classification.requiredExpertise.length > 0 && (
          <div className="bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
            <div className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider mb-1.5">Required Expertise</div>
            <div className="flex flex-wrap gap-1">
              {classification.requiredExpertise.map((exp) => (
                <span key={exp} className="text-xs px-2 py-0.5 rounded bg-[#034F46]/10 text-[#034F46] border border-[#034F46]/20 font-semibold">
                  {exp}
                </span>
              ))}
            </div>
          </div>
        )}

        {classification.requiredResources && classification.requiredResources.length > 0 && (
          <div className="bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
            <div className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider mb-1.5">Required Resources</div>
            <div className="flex flex-wrap gap-1">
              {classification.requiredResources.map((res) => (
                <span key={res} className="text-xs px-2 py-0.5 rounded bg-[#087F6B]/10 text-[#087F6B] border border-[#087F6B]/20 font-semibold">
                  {res}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Human Decision Boundary Footer */}
      <div className="mt-5 pt-4 border-t border-[#D8D8C8] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-[#F7F5E8] p-3.5 rounded-xl border border-[#D8D8C8]">
        <div className="flex items-center gap-2 text-xs text-[#B7791F]">
          <ShieldCheck className="w-4 h-4 shrink-0 text-[#B7791F]" />
          <span>
            <strong className="text-[#17332F]">Human Decision Boundary</strong>: AI recommendations assist review. Final consequential actions require human validation.
          </span>
        </div>

        {showActions && (
          <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
            {onCorrect && (
              <button
                onClick={onCorrect}
                className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-[#F7F5E8] hover:bg-[#E9DFFF] text-[#17332F] border border-[#D8D8C8] transition"
              >
                Correct Category
              </button>
            )}
            {onAccept && (
              <button
                onClick={onAccept}
                className="px-4 py-1.5 rounded-xl text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition flex items-center gap-1 shadow-md"
              >
                <Check className="w-3.5 h-3.5" /> Accept AI Finding
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
