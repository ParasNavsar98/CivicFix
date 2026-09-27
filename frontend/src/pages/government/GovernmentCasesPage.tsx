import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Problem } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';
import { SeverityBadge } from '../../components/common/SeverityBadge';
import { Briefcase, Building2, UserCheck, ShieldAlert, ArrowRight } from 'lucide-react';
import { DashboardSkeleton } from '../../components/common/Skeleton';

export const GovernmentCasesPage: React.FC = () => {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProblems().then((res) => {
      setProblems(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <DashboardSkeleton />;

  return (
    <div className="space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Government Case Management</h1>
        <p className="text-xs text-[#66736F] mt-1">Manage validated cases routed to public works, water, and environmental departments.</p>
      </div>

      <div className="glass-card rounded-3xl overflow-hidden border border-[#D8D8C8]">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F7F5E8] border-b border-[#D8D8C8] text-[#66736F] uppercase text-[10px] font-bold">
              <tr>
                <th className="p-4">Case ID</th>
                <th className="p-4">Title & Domain</th>
                <th className="p-4">Assigned Dept</th>
                <th className="p-4">Assigned Officer</th>
                <th className="p-4">Severity</th>
                <th className="p-4">Status</th>
                <th className="p-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#D8D8C8]">
              {problems.map((prob) => (
                <tr key={prob.problemId} className="hover:bg-[#F7F5E8]/50 transition">
                  <td className="p-4 font-mono font-bold text-[#6A5ACD]">CASE-{prob.problemId}</td>
                  <td className="p-4 max-w-xs">
                    <span className="font-bold text-[#17332F] block truncate">{prob.title}</span>
                    <span className="text-[10px] text-[#66736F]">{prob.primaryDomain}</span>
                  </td>
                  <td className="p-4 text-[#17332F] font-medium">{prob.assignedDepartment || 'Urban Development (PWD)'}</td>
                  <td className="p-4 text-[#17332F] font-medium">{prob.assignedOfficer || 'Er. R. K. Shrivastava'}</td>
                  <td className="p-4">
                    <SeverityBadge severity={prob.severity || 'MODERATE'} size="sm" />
                  </td>
                  <td className="p-4">
                    <StatusBadge status={prob.status} size="sm" />
                  </td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => alert(`Case CASE-${prob.problemId} officer assignment updated.`)}
                      className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#034F46] hover:bg-[#0F766E] text-white transition shadow-xs cursor-pointer"
                    >
                      Manage Officer
                    </button>
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
