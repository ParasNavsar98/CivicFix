import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../services/api';
import { Problem } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';
import { SeverityBadge } from '../../components/common/SeverityBadge';
import { ConfidenceBadge } from '../../components/common/ConfidenceBadge';
import { ShieldAlert, Search, Filter, ArrowRight, Eye } from 'lucide-react';
import { DashboardSkeleton } from '../../components/common/Skeleton';

export const ReviewQueuePage: React.FC = () => {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('ALL');

  useEffect(() => {
    api.getProblems().then((res) => {
      setProblems(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <DashboardSkeleton />;

  const filtered = severityFilter === 'ALL' ? problems : problems.filter((p) => p.severity === severityFilter);

  return (
    <div className="space-y-6 animate-in fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-[#17332F]">Human Review Queue</h1>
          <p className="text-xs text-[#66736F] mt-1">
            Review cases requiring human validation (confidence &lt; 0.85, duplicate candidates, or critical severity).
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {['ALL', 'CRITICAL', 'HIGH', 'MODERATE', 'LOW'].map((sev) => (
          <button
            key={sev}
            onClick={() => setSeverityFilter(sev)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition cursor-pointer ${
              severityFilter === sev
                ? 'bg-[#034F46] text-white shadow-xs font-bold'
                : 'bg-[#FFFDF5] text-[#66736F] border border-[#D8D8C8] hover:text-[#17332F]'
            }`}
          >
            {sev === 'ALL' ? 'All Severities' : sev}
          </button>
        ))}
      </div>

      {/* Review Queue Table */}
      <div className="glass-card rounded-3xl overflow-hidden border border-[#D8D8C8]">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F7F5E8] border-b border-[#D8D8C8] text-[#66736F] uppercase text-[10px] font-bold">
              <tr>
                <th className="p-4">Problem ID</th>
                <th className="p-4">Title & Domain</th>
                <th className="p-4">District</th>
                <th className="p-4">Confidence</th>
                <th className="p-4">Severity</th>
                <th className="p-4">Status</th>
                <th className="p-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#D8D8C8]">
              {filtered.map((prob) => (
                <tr key={prob.problemId} className="hover:bg-[#F7F5E8]/50 transition">
                  <td className="p-4 font-mono font-bold text-[#6A5ACD]">{prob.problemId}</td>
                  <td className="p-4 max-w-xs">
                    <span className="font-bold text-[#17332F] block truncate">{prob.title}</span>
                    <span className="text-[10px] text-[#66736F]">{prob.primaryDomain} • {prob.subcategory}</span>
                  </td>
                  <td className="p-4 text-[#17332F] font-medium">{prob.location.district}</td>
                  <td className="p-4">
                    <ConfidenceBadge confidence={prob.confidence || 0.88} />
                  </td>
                  <td className="p-4">
                    <SeverityBadge severity={prob.severity || 'MODERATE'} size="sm" />
                  </td>
                  <td className="p-4">
                    <StatusBadge status={prob.status} size="sm" />
                  </td>
                  <td className="p-4 text-right">
                    <Link
                      to={`/government/review/${prob.problemId}`}
                      className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#034F46] hover:bg-[#0F766E] text-white transition inline-flex items-center gap-1 shadow-xs"
                    >
                      <Eye className="w-3.5 h-3.5" /> Review
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
