import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../services/api';
import { Problem } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';
import { SeverityBadge } from '../../components/common/SeverityBadge';
import { Search, Filter, PlusCircle, MapPin, ArrowRight } from 'lucide-react';
import { DashboardSkeleton } from '../../components/common/Skeleton';

export const CitizenProblemsPage: React.FC = () => {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);
  const [domainFilter, setDomainFilter] = useState<string>('ALL');

  useEffect(() => {
    api.getProblems().then((res) => {
      setProblems(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <DashboardSkeleton />;

  const filtered = domainFilter === 'ALL' ? problems : problems.filter((p) => p.primaryDomain === domainFilter);

  return (
    <div className="space-y-6 animate-in fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-[#17332F]">My Community Problems</h1>
          <p className="text-xs text-[#66736F] mt-1">Track status and lifecycle progress for your submitted issues</p>
        </div>

        <Link
          to="/citizen/report"
          className="px-5 py-2.5 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] text-white shadow-md transition flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <PlusCircle className="w-4 h-4" /> Report Problem
        </Link>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {['ALL', 'Sanitation', 'Environment', 'Urban Infrastructure', 'Energy', 'Water Resources'].map((dom) => (
          <button
            key={dom}
            onClick={() => setDomainFilter(dom)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition cursor-pointer ${
              domainFilter === dom
                ? 'bg-[#034F46] text-white shadow-xs'
                : 'bg-[#FFFDF5] text-[#66736F] border border-[#D8D8C8] hover:text-[#17332F]'
            }`}
          >
            {dom}
          </button>
        ))}
      </div>

      {/* Problems List */}
      <div className="space-y-3">
        {filtered.map((prob) => (
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
                  Track →
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};
