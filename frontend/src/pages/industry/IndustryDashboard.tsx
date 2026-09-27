import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../services/api';
import { SolutionItem } from '../../types';
import { Briefcase, ShoppingBag, HeartHandshake, Handshake, ArrowRight, Building, MapPin } from 'lucide-react';
import { DashboardSkeleton } from '../../components/common/Skeleton';

export const IndustryDashboard: React.FC = () => {
  const [solutions, setSolutions] = useState<SolutionItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSolutions().then((res) => {
      setSolutions(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <DashboardSkeleton />;

  return (
    <div className="space-y-8 animate-in fade-in">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#17332F] tracking-tight">
            Industry & CSR Partner Portal
          </h1>
          <p className="text-xs text-[#66736F] mt-1">CleanTech Innovations Pvt Ltd • Corporate Social Responsibility & Innovation</p>
        </div>

        <Link
          to="/industry/marketplace"
          className="px-5 py-2.5 rounded-full text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md inline-flex items-center gap-2 self-start sm:self-auto"
        >
          <ShoppingBag className="w-4 h-4" /> Browse Marketplace ({solutions.length})
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-[#FFFDF5] rounded-2xl p-4 border border-[#D8D8C8] shadow-sm">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">Opportunities</span>
          <span className="text-2xl font-black text-[#034F46] mt-1 block">{solutions.length}</span>
        </div>
        <div className="bg-[#FFFDF5] rounded-2xl p-4 border border-[#D8D8C8] shadow-sm">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">Resource Requests</span>
          <span className="text-2xl font-black text-[#6A5ACD] mt-1 block">4</span>
        </div>
        <div className="bg-[#FFFDF5] rounded-2xl p-4 border border-[#D8D8C8] shadow-sm">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">My Interests</span>
          <span className="text-2xl font-black text-[#B7791F] mt-1 block">1</span>
        </div>
        <div className="bg-[#FFFDF5] rounded-2xl p-4 border border-[#D8D8C8] shadow-sm">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">Active Collaborations</span>
          <span className="text-2xl font-black text-[#087F6B] mt-1 block">1</span>
        </div>
      </div>

      {/* Recently Published Solutions */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-[#17332F] flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-[#0F766E]" /> Featured University Solutions
          </h2>
          <Link to="/industry/marketplace" className="text-xs text-[#0F766E] font-semibold hover:underline">
            View All →
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {solutions.map((sol) => (
            <div key={sol.solutionId} className="bg-[#FFFDF5] rounded-2xl p-5 border border-[#D8D8C8] shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-[#0F766E]">{sol.solutionId}</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#0F766E]/10 text-[#034F46] font-bold border border-[#0F766E]/20">
                  {sol.developmentStage}
                </span>
              </div>

              <h3 className="text-base font-bold text-[#17332F]">{sol.title}</h3>
              <p className="text-xs text-[#66736F] line-clamp-2">{sol.description}</p>

              <div className="pt-2 flex items-center justify-between text-xs text-[#66736F] border-t border-[#D8D8C8]">
                <span>University: <strong className="text-[#17332F]">{sol.universityName || 'BIT Mesra'}</strong></span>
                <Link
                  to="/industry/marketplace"
                  className="text-xs font-bold text-[#034F46] hover:text-[#0F766E] flex items-center gap-1"
                >
                  Offer Support <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
