import React from 'react';
import { FactorScores } from '../../types';
import { Award, CheckCircle, MapPin, Users, Building, Briefcase, History } from 'lucide-react';

interface MatchScoreCardProps {
  universityName: string;
  finalScore: number;
  rank?: number;
  factorScores: FactorScores;
  explanation?: string;
}

export const MatchScoreCard: React.FC<MatchScoreCardProps> = ({
  universityName,
  finalScore,
  rank,
  factorScores,
  explanation,
}) => {
  const factors = [
    {
      key: 'expertise',
      label: 'Expertise Match',
      weight: '35%',
      score: factorScores.expertise,
      icon: <Award className="w-4 h-4 text-[#034F46]" />,
      color: 'bg-[#034F46]',
    },
    {
      key: 'faculty',
      label: 'Faculty Coverage',
      weight: '20%',
      score: factorScores.faculty,
      icon: <Users className="w-4 h-4 text-[#0F766E]" />,
      color: 'bg-[#0F766E]',
    },
    {
      key: 'infrastructure',
      label: 'Infrastructure Match',
      weight: '15%',
      score: factorScores.infrastructure,
      icon: <Building className="w-4 h-4 text-[#6A5ACD]" />,
      color: 'bg-[#6A5ACD]',
    },
    {
      key: 'pastProjects',
      label: 'Relevant Past Projects',
      weight: '10%',
      score: factorScores.pastProjects,
      icon: <History className="w-4 h-4 text-[#087F6B]" />,
      color: 'bg-[#087F6B]',
    },
    {
      key: 'geography',
      label: 'Geographic Proximity',
      weight: '10%',
      score: factorScores.geography,
      icon: <MapPin className="w-4 h-4 text-[#B7791F]" />,
      color: 'bg-[#B7791F]',
    },
    {
      key: 'capacity',
      label: 'Current Capacity',
      weight: '5%',
      score: factorScores.capacity,
      icon: <CheckCircle className="w-4 h-4 text-[#0F766E]" />,
      color: 'bg-[#0F766E]',
    },
    {
      key: 'industry',
      label: 'Industry Ecosystem',
      weight: '5%',
      score: factorScores.industry,
      icon: <Briefcase className="w-4 h-4 text-[#6A5ACD]" />,
      color: 'bg-[#6A5ACD]',
    },
  ];

  return (
    <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-[#D8D8C8]">
        <div>
          {rank && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#E9DFFF] text-[#6A5ACD] border border-[#6A5ACD]/30 mb-2">
              Rank #{rank} Candidate
            </span>
          )}
          <h3 className="text-xl font-bold text-[#17332F] tracking-tight">{universityName}</h3>
          {explanation && <p className="text-xs text-[#66736F] mt-1 line-clamp-2">{explanation}</p>}
        </div>

        {/* Overall Match Score Badge */}
        <div className="flex items-center gap-3 bg-[#F7F5E8] border border-[#D8D8C8] px-4 py-2.5 rounded-xl self-start sm:self-auto">
          <div className="text-right">
            <div className="text-[10px] text-[#66736F] uppercase tracking-wider font-semibold">Match Score</div>
            <div className="text-2xl font-black text-[#034F46]">
              {finalScore.toFixed(1)} <span className="text-sm font-normal text-[#66736F]">/ 100</span>
            </div>
          </div>
        </div>
      </div>

      {/* 7-Factor Progress Bars */}
      <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {factors.map((f) => {
          const scorePercent = Math.round(f.score * 100);
          return (
            <div key={f.key} className="bg-[#F7F5E8]/60 border border-[#D8D8C8] p-3.5 rounded-xl">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="flex items-center gap-2 font-semibold text-[#17332F]">
                  {f.icon}
                  {f.label}
                </span>
                <span className="text-[#66736F]">
                  <span className="text-[#17332F] font-bold">{scorePercent}%</span>
                  <span className="text-[10px] text-[#66736F] ml-1">({f.weight})</span>
                </span>
              </div>
              <div className="w-full bg-[#D8D8C8]/50 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full ${f.color} transition-all duration-500 ease-out`}
                  style={{ width: `${scorePercent}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
