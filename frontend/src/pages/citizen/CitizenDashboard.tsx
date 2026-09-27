import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../services/auth';
import { api } from '../../services/api';
import { Problem } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';
import { SeverityBadge } from '../../components/common/SeverityBadge';
import { PlusCircle, FileText, Clock, CheckCircle2, MapPin, ArrowRight, Sparkles } from 'lucide-react';
import { DashboardSkeleton } from '../../components/common/Skeleton';

export const CitizenDashboard: React.FC = () => {
  const { user } = useAuth();
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProblems().then((res) => {
      setProblems(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <DashboardSkeleton />;

  const totalSubmitted = problems.length;
  const underReview = problems.filter((p) => p.status === 'Under Review' || p.status === 'Submitted').length;
  const inProgress = problems.filter((p) => p.status === 'University Assigned' || p.status === 'In Progress' || p.status === 'Routed Government').length;
  const resolved = problems.filter((p) => p.status === 'Resolved').length;

  return (
    <div className="space-y-8 animate-in fade-in">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#17332F] tracking-tight">
            Good morning, {user?.name || 'Citizen'}
          </h1>
          <p className="text-xs text-[#66736F] mt-1">Here's what's happening with your community problems.</p>
        </div>

        <Link
          to="/citizen/report"
          className="px-5 py-2.5 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] text-white shadow-md transition inline-flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <PlusCircle className="w-4 h-4" /> Report New Problem
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-card rounded-2xl p-4">
          <div className="flex items-center justify-between text-[#66736F]">
            <span className="text-xs font-semibold uppercase tracking-wider">Submitted</span>
            <FileText className="w-4 h-4 text-[#6A5ACD]" />
          </div>
          <div className="text-2xl font-black text-[#17332F] mt-2">{totalSubmitted}</div>
        </div>

        <div className="glass-card rounded-2xl p-4">
          <div className="flex items-center justify-between text-[#66736F]">
            <span className="text-xs font-semibold uppercase tracking-wider">Under Review</span>
            <Clock className="w-4 h-4 text-[#B7791F]" />
          </div>
          <div className="text-2xl font-black text-[#B7791F] mt-2">{underReview}</div>
        </div>

        <div className="glass-card rounded-2xl p-4">
          <div className="flex items-center justify-between text-[#66736F]">
            <span className="text-xs font-semibold uppercase tracking-wider">In Progress</span>
            <Sparkles className="w-4 h-4 text-[#0F766E]" />
          </div>
          <div className="text-2xl font-black text-[#0F766E] mt-2">{inProgress}</div>
        </div>

        <div className="glass-card rounded-2xl p-4">
          <div className="flex items-center justify-between text-[#66736F]">
            <span className="text-xs font-semibold uppercase tracking-wider">Resolved</span>
            <CheckCircle2 className="w-4 h-4 text-[#087F6B]" />
          </div>
          <div className="text-2xl font-black text-[#087F6B] mt-2">{resolved}</div>
        </div>
      </div>

      {/* Recent Problems Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-[#17332F]">Recent Community Problems</h2>
          <Link to="/citizen/problems" className="text-xs text-[#034F46] hover:text-[#0F766E] font-semibold flex items-center gap-1">
            View All ({problems.length}) <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="space-y-3">
          {problems.map((prob) => (
            <Link
              key={prob.problemId}
              to={`/citizen/problems/${prob.problemId}`}
              className="glass-card rounded-2xl p-5 block hover:border-[#0F766E] transition group"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-[#6A5ACD]">{prob.problemId}</span>
                    <SeverityBadge severity={prob.severity || 'MODERATE'} size="sm" />
                    <StatusBadge status={prob.status} size="sm" />
                  </div>
                  <h3 className="text-base font-bold text-[#17332F] group-hover:text-[#034F46] transition">{prob.title}</h3>
                  <p className="text-xs text-[#66736F] line-clamp-1">{prob.description}</p>
                </div>

                <div className="flex items-center gap-4 text-xs text-[#66736F] shrink-0">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-[#66736F]" /> {prob.location.district}
                  </span>
                  <span className="text-[#034F46] font-semibold group-hover:translate-x-1 transition">
                    Details →
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};
