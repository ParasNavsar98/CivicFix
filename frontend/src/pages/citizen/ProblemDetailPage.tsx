import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../../services/api';
import { Problem } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';
import { SeverityBadge } from '../../components/common/SeverityBadge';
import { AIInsightCard } from '../../components/common/AIInsightCard';
import { ProblemTimeline } from '../../components/common/ProblemTimeline';
import { MapPin, Calendar, User, ArrowLeft, Layers, Building2, BookOpen } from 'lucide-react';
import { Skeleton } from '../../components/common/Skeleton';

export const ProblemDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      api.getProblemById(id).then((res) => {
        setProblem(res || null);
        setLoading(false);
      });
    }
  }, [id]);

  if (loading) return <Skeleton className="h-96 rounded-3xl" />;
  if (!problem) {
    return (
      <div className="glass-card rounded-3xl p-8 text-center space-y-4">
        <h3 className="text-xl font-bold text-[#17332F]">Problem Not Found</h3>
        <p className="text-xs text-[#66736F]">The problem ID {id} does not exist or has been archived.</p>
        <Link to="/citizen/problems" className="px-4 py-2 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] text-white">
          Back to Problems List
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <Link to="/citizen/problems" className="text-xs text-[#66736F] hover:text-[#17332F] transition flex items-center gap-1">
          <ArrowLeft className="w-4 h-4" /> Back to My Problems
        </Link>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold text-[#6A5ACD]">{problem.problemId}</span>
          <StatusBadge status={problem.status} />
        </div>
      </div>

      {/* Main Title & Overview Card */}
      <div className="glass-card rounded-3xl p-6 sm:p-8 space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <SeverityBadge severity={problem.severity || 'MODERATE'} />
          <span className="text-xs px-2.5 py-1 rounded-full bg-[#E9DFFF] text-[#6A5ACD] border border-[#6A5ACD]/20 font-semibold">
            {problem.primaryDomain}
          </span>
          {problem.subcategory && (
            <span className="text-xs px-2.5 py-1 rounded-full bg-[#0F766E]/10 text-[#0F766E] border border-[#0F766E]/20 font-semibold">
              {problem.subcategory}
            </span>
          )}
        </div>

        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#17332F] tracking-tight">{problem.title}</h1>
        <p className="text-xs sm:text-sm text-[#17332F] leading-relaxed">{problem.description}</p>

        <div className="pt-4 border-t border-[#D8D8C8] grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-[#66736F]">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-[#6A5ACD]" />
            <span>{problem.location.address || `${problem.location.district}, ${problem.location.state}`}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-[#0F766E]" />
            <span>Submitted {new Date(problem.submittedAt).toLocaleDateString()}</span>
          </div>
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-[#087F6B]" />
            <span>Submitter: {problem.submitterName || 'Citizen'}</span>
          </div>
        </div>
      </div>

      {/* 8-Stage Workflow Timeline */}
      <ProblemTimeline currentStage={problem.stage} />

      {/* AI Classification Insights */}
      {problem.aiClassification && (
        <AIInsightCard classification={problem.aiClassification} />
      )}
    </div>
  );
};
