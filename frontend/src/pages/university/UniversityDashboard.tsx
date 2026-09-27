import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../services/api';
import { UniversityMatchResult } from '../../types';
import { MatchScoreCard } from '../../components/common/MatchScoreCard';
import { Award, BookOpen, Briefcase, CheckCircle, Clock, ArrowRight } from 'lucide-react';
import { DashboardSkeleton } from '../../components/common/Skeleton';

export const UniversityDashboard: React.FC = () => {
  const [matches, setMatches] = useState<UniversityMatchResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getMatchingForProblem('CF-2026-001').then((res) => {
      setMatches(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <DashboardSkeleton />;

  return (
    <div className="space-y-8 animate-in fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#17332F] tracking-tight">
            University Research & Capability Portal
          </h1>
          <p className="text-xs text-[#66736F] mt-1">Birla Institute of Technology (BIT Mesra) • Department of Environmental Science</p>
        </div>

        <Link
          to="/university/assignments"
          className="px-5 py-2.5 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] text-white transition shadow-md inline-flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <BookOpen className="w-4 h-4" /> View Pending Assignments (1)
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="glass-card rounded-2xl p-4 border border-[#6A5ACD]/20">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">Matched Problems</span>
          <span className="text-2xl font-black text-[#6A5ACD] mt-1 block">3</span>
        </div>
        <div className="glass-card rounded-2xl p-4 border border-[#B7791F]/20">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">Pending Queue</span>
          <span className="text-2xl font-black text-[#B7791F] mt-1 block">1</span>
        </div>
        <div className="glass-card rounded-2xl p-4 border border-[#087F6B]/20">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">Accepted</span>
          <span className="text-2xl font-black text-[#087F6B] mt-1 block">4</span>
        </div>
        <div className="glass-card rounded-2xl p-4 border border-[#0F766E]/20">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">Active Projects</span>
          <span className="text-2xl font-black text-[#0F766E] mt-1 block">2</span>
        </div>
        <div className="glass-card rounded-2xl p-4 border border-[#034F46]/20">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">Milestones Due</span>
          <span className="text-2xl font-black text-[#034F46] mt-1 block">3</span>
        </div>
        <div className="glass-card rounded-2xl p-4 border border-[#0F766E]/20">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">Completed</span>
          <span className="text-2xl font-black text-[#0F766E] mt-1 block">12</span>
        </div>
      </div>

      {/* Recommended Problem Matches Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-[#17332F] flex items-center gap-2">
            <Award className="w-5 h-5 text-[#6A5ACD]" /> Recommended Problem Matches (7-Factor Scorer)
          </h2>
          <Link to="/university/matches" className="text-xs text-[#034F46] font-semibold hover:underline">
            Browse All Matches →
          </Link>
        </div>

        {matches.map((match) => (
          <MatchScoreCard
            key={match.universityId}
            universityName={match.universityName}
            finalScore={match.finalScore}
            rank={match.rank}
            factorScores={match.factorScores}
            explanation={match.explanation}
          />
        ))}
      </div>
    </div>
  );
};
