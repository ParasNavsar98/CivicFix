import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../../services/api';
import { UniversityMatchResult } from '../../types';
import { MatchScoreCard } from '../../components/common/MatchScoreCard';
import { ArrowLeft, BookOpen } from 'lucide-react';
import { Skeleton } from '../../components/common/Skeleton';

export const MatchDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [match, setMatch] = useState<UniversityMatchResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getMatchingForProblem(id || 'CF-2026-001').then((res) => {
      if (res && res.length > 0) setMatch(res[0]);
      setLoading(false);
    });
  }, [id]);

  if (loading) return <Skeleton className="h-96 rounded-3xl" />;
  if (!match) return <div className="p-8 text-white">Match details not found.</div>;

  return (
    <div className="space-y-6 animate-in fade-in">
      <div className="flex items-center justify-between">
        <Link to="/university/dashboard" className="text-xs text-[#66736F] hover:text-[#17332F] transition flex items-center gap-1">
          <ArrowLeft className="w-4 h-4" /> Back to University Dashboard
        </Link>
        <span className="text-xs font-bold text-[#6A5ACD]">7-Factor Capability Match Analysis</span>
      </div>

      <MatchScoreCard
        universityName={match.universityName}
        finalScore={match.finalScore}
        rank={match.rank}
        factorScores={match.factorScores}
        explanation={match.explanation}
      />
    </div>
  );
};
