import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../services/api';
import { Problem } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';
import { SeverityBadge } from '../../components/common/SeverityBadge';
import { ConfidenceBadge } from '../../components/common/ConfidenceBadge';
import {
  ShieldAlert,
  Layers,
  Briefcase,
  CheckSquare,
  AlertOctagon,
  Clock,
  ArrowRight,
  BarChart2,
  Building2,
} from 'lucide-react';
import { DashboardSkeleton } from '../../components/common/Skeleton';

export const GovernmentDashboard: React.FC = () => {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProblems().then((res) => {
      setProblems(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <DashboardSkeleton />;

  const pendingReviews = problems.filter((p) => p.reviewRequired || p.confidence! < 0.85).length;
  const duplicateCandidates = problems.filter((p) => p.status === 'Under Review' || p.reviewReason?.includes('duplicate')).length + 1;
  const activeCases = problems.filter((p) => p.status === 'Routed Government' || p.status === 'In Progress').length;
  const verificationPending = problems.filter((p) => p.severity === 'CRITICAL' || p.severity === 'HIGH').length;
  const overdueCases = 1;
  const escalations = 1;

  return (
    <div className="space-y-8 animate-in fade-in">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#17332F] tracking-tight">
            Government & Review Operations Dashboard
          </h1>
          <p className="text-xs text-[#66736F] mt-1">Human-in-the-Loop validation, duplicate evaluation & department case dispatch.</p>
        </div>

        <Link
          to="/government/review"
          className="px-5 py-2.5 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] text-white transition shadow-md inline-flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <ShieldAlert className="w-4 h-4" /> Open Review Queue ({pendingReviews})
        </Link>
      </div>

      {/* 6 KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="glass-card rounded-2xl p-4 border border-[#B7791F]/30">
          <div className="flex items-center justify-between text-[#66736F]">
            <span className="text-[10px] font-bold uppercase tracking-wider">Pending Reviews</span>
            <ShieldAlert className="w-4 h-4 text-[#B7791F]" />
          </div>
          <div className="text-2xl font-black text-[#B7791F] mt-2">{pendingReviews}</div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-[#0F766E]/30">
          <div className="flex items-center justify-between text-[#66736F]">
            <span className="text-[10px] font-bold uppercase tracking-wider">Duplicates</span>
            <Layers className="w-4 h-4 text-[#0F766E]" />
          </div>
          <div className="text-2xl font-black text-[#0F766E] mt-2">{duplicateCandidates}</div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-[#6A5ACD]/30">
          <div className="flex items-center justify-between text-[#66736F]">
            <span className="text-[10px] font-bold uppercase tracking-wider">Active Cases</span>
            <Briefcase className="w-4 h-4 text-[#6A5ACD]" />
          </div>
          <div className="text-2xl font-black text-[#6A5ACD] mt-2">{activeCases}</div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-[#034F46]/30">
          <div className="flex items-center justify-between text-[#66736F]">
            <span className="text-[10px] font-bold uppercase tracking-wider">Verification</span>
            <CheckSquare className="w-4 h-4 text-[#034F46]" />
          </div>
          <div className="text-2xl font-black text-[#034F46] mt-2">{verificationPending}</div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-[#B7791F]/30">
          <div className="flex items-center justify-between text-[#66736F]">
            <span className="text-[10px] font-bold uppercase tracking-wider">Overdue SLA</span>
            <Clock className="w-4 h-4 text-[#B7791F]" />
          </div>
          <div className="text-2xl font-black text-[#B7791F] mt-2">{overdueCases}</div>
        </div>

        <div className="glass-card rounded-2xl p-4 border border-[#B83A3A]/30">
          <div className="flex items-center justify-between text-[#66736F]">
            <span className="text-[10px] font-bold uppercase tracking-wider">Escalations</span>
            <AlertOctagon className="w-4 h-4 text-[#B83A3A]" />
          </div>
          <div className="text-2xl font-black text-[#B83A3A] mt-2">{escalations}</div>
        </div>
      </div>

      {/* Analytics Summary Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Problems by Domain */}
        <div className="glass-card rounded-3xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-[#17332F] uppercase tracking-wider flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-[#6A5ACD]" /> Domain Volume Distribution
          </h3>

          <div className="space-y-3">
            {[
              { domain: 'Sanitation', count: 12, percent: 35, color: 'bg-[#6A5ACD]' },
              { domain: 'Environment', count: 9, percent: 26, color: 'bg-[#0F766E]' },
              { domain: 'Urban Infrastructure', count: 8, percent: 23, color: 'bg-[#034F46]' },
              { domain: 'Energy', count: 5, percent: 16, color: 'bg-[#B7791F]' },
            ].map((d) => (
              <div key={d.domain} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-[#17332F]">{d.domain}</span>
                  <span className="text-[#66736F]">{d.count} cases ({d.percent}%)</span>
                </div>
                <div className="w-full bg-[#F7F5E8] h-2 rounded-full overflow-hidden">
                  <div className={`h-full ${d.color}`} style={{ width: `${d.percent}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Priority Action Queue */}
        <div className="glass-card rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-[#17332F] uppercase tracking-wider flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-[#B7791F]" /> Action Required Queue
            </h3>
            <Link to="/government/review" className="text-xs text-[#034F46] hover:text-[#0F766E] font-semibold">
              View Queue →
            </Link>
          </div>

          <div className="space-y-3 text-xs">
            {problems.slice(0, 3).map((p) => (
              <Link
                key={p.problemId}
                to={`/government/review/${p.problemId}`}
                className="p-3 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] block hover:border-[#0F766E] transition"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-[#6A5ACD]">{p.problemId}</span>
                  <ConfidenceBadge confidence={p.confidence || 0.88} showLabel={false} />
                </div>
                <h4 className="font-bold text-[#17332F] mt-1 line-clamp-1">{p.title}</h4>
                <div className="mt-2 flex items-center gap-2 text-[10px] text-[#66736F]">
                  <SeverityBadge severity={p.severity || 'MODERATE'} size="sm" />
                  <span>District: {p.location.district}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
