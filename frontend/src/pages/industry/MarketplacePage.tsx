import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { SolutionItem } from '../../types';
import { ShoppingBag, Search, Filter, HeartHandshake, CheckCircle2, ArrowRight } from 'lucide-react';
import { Modal } from '../../components/common/Modal';
import { DashboardSkeleton } from '../../components/common/Skeleton';

export const MarketplacePage: React.FC = () => {
  const [solutions, setSolutions] = useState<SolutionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [stageFilter, setStageFilter] = useState('ALL');

  // Express Interest Modal
  const [showInterestModal, setShowInterestModal] = useState(false);
  const [selectedSol, setSelectedSol] = useState<SolutionItem | null>(null);
  const [supportOffered, setSupportOffered] = useState<string[]>(['Hardware', 'Testing']);
  const [message, setMessage] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    api.getSolutions().then((res) => {
      setSolutions(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <DashboardSkeleton />;

  const filtered = stageFilter === 'ALL' ? solutions : solutions.filter((s) => s.developmentStage === stageFilter);

  const handleInterestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSol || !message.trim()) return;

    await api.expressInterest(
      selectedSol.solutionId,
      'IND-CLEANTECH-99',
      supportOffered,
      message,
      { supportDetails: supportOffered }
    );

    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setShowInterestModal(false);
    }, 2000);
  };

  return (
    <div className="space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Solution Opportunities Marketplace</h1>
        <p className="text-xs text-[#66736F] mt-1">
          Browse published university research solutions and contribute hardware, testing, mentorship, or funding.
        </p>
      </div>

      {/* Stage Filters */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {['ALL', 'IDEA', 'PROTOTYPE', 'PILOT', 'DEPLOYED'].map((stage) => (
          <button
            key={stage}
            onClick={() => setStageFilter(stage)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition ${
              stageFilter === stage
                ? 'bg-[#034F46] text-white shadow-sm font-bold'
                : 'bg-[#FFFDF5] text-[#66736F] border border-[#D8D8C8] hover:text-[#17332F]'
            }`}
          >
            {stage}
          </button>
        ))}
      </div>

      {/* Solutions Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filtered.map((sol) => (
          <div key={sol.solutionId} className="bg-[#FFFDF5] rounded-3xl p-6 space-y-4 border border-[#D8D8C8] shadow-sm flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-[#0F766E]">{sol.solutionId}</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#0F766E]/10 text-[#034F46] font-bold border border-[#0F766E]/20">
                  Stage: {sol.developmentStage}
                </span>
              </div>

              <h3 className="text-lg font-bold text-[#17332F]">{sol.title}</h3>
              <p className="text-xs text-[#66736F] leading-relaxed">{sol.description}</p>

              <div className="bg-[#F4F1E1] p-3 rounded-xl border border-[#D8D8C8] space-y-1 text-xs">
                <span className="text-[10px] text-[#66736F] uppercase font-semibold block">University Developer</span>
                <span className="font-bold text-[#17332F] block">{sol.universityName || 'BIT Mesra'}</span>
              </div>

              <div>
                <span className="text-[10px] text-[#66736F] uppercase font-semibold block mb-1.5">Support Needed</span>
                <div className="flex flex-wrap gap-1">
                  {sol.supportNeeded.map((sup) => (
                    <span key={sup} className="text-xs px-2 py-0.5 rounded bg-[#6A5ACD]/10 text-[#6A5ACD] border border-[#6A5ACD]/20">
                      {sup}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-[#D8D8C8] flex justify-end">
              <button
                onClick={() => {
                  setSelectedSol(sol);
                  setShowInterestModal(true);
                }}
                className="px-5 py-2.5 rounded-full text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md flex items-center gap-1.5"
              >
                <HeartHandshake className="w-4 h-4" /> Express Interest / Offer Support
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* EXPRESS INTEREST MODAL */}
      <Modal
        isOpen={showInterestModal}
        onClose={() => setShowInterestModal(false)}
        title="Express Interest & Offer Support"
        subtitle={selectedSol ? `Opportunity: ${selectedSol.title}` : ''}
      >
        {submitted ? (
          <div className="p-6 text-center space-y-2">
            <CheckCircle2 className="w-8 h-8 text-[#087F6B] mx-auto" />
            <h4 className="text-base font-bold text-[#17332F]">Interest Expressed Successfully!</h4>
            <p className="text-xs text-[#66736F]">University project leads will review your contribution offer.</p>
          </div>
        ) : (
          <form onSubmit={handleInterestSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-semibold text-[#17332F] mb-1">Organization Name</label>
              <input
                type="text"
                readOnly
                value="CleanTech Innovations Pvt Ltd"
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#F4F1E1] border border-[#D8D8C8] text-[#17332F] font-bold"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#17332F] mb-1 font-bold">Support Offered Types</label>
              <div className="grid grid-cols-2 gap-2">
                {['Hardware', 'Testing', 'Mentorship', 'Funding', 'Equipment', 'Deployment Support'].map((item) => (
                  <label key={item} className="flex items-center gap-2 p-2 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] cursor-pointer">
                    <input
                      type="checkbox"
                      checked={supportOffered.includes(item)}
                      onChange={(e) => {
                        if (e.target.checked) setSupportOffered([...supportOffered, item]);
                        else setSupportOffered(supportOffered.filter((s) => s !== item));
                      }}
                      className="rounded text-[#034F46] focus:ring-0"
                    />
                    <span>{item}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block font-semibold text-[#034F46] mb-1">Proposal & Contribution Message</label>
              <textarea
                rows={4}
                required
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Describe your organization's capability, equipment, or CSR contribution..."
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] placeholder-[#66736F] focus:outline-none focus:border-[#034F46]"
              />
            </div>

            <div className="pt-2 flex justify-end gap-3">
              <button type="button" onClick={() => setShowInterestModal(false)} className="px-4 py-2 rounded-xl bg-[#F7F5E8] text-[#66736F] border border-[#D8D8C8] hover:bg-[#E9DFFF]">
                Cancel
              </button>
              <button
                type="submit"
                disabled={!message.trim()}
                className="px-6 py-2 rounded-xl bg-[#034F46] text-white font-bold hover:bg-[#0F766E] transition disabled:opacity-50"
              >
                Submit Interest Proposal
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};
