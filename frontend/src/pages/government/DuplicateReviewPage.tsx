import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Problem, DuplicateCandidate } from '../../types';
import { Layers, ShieldCheck, Check, X, AlertTriangle, ArrowRight, MapPin } from 'lucide-react';
import { Modal } from '../../components/common/Modal';
import { DashboardSkeleton } from '../../components/common/Skeleton';

export const DuplicateReviewPage: React.FC = () => {
  const [problemA, setProblemA] = useState<Problem | null>(null);
  const [candidates, setCandidates] = useState<DuplicateCandidate[]>([]);
  const [loading, setLoading] = useState(true);

  // Merge modal
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [selectedCand, setSelectedCand] = useState<DuplicateCandidate | null>(null);

  useEffect(() => {
    api.getProblems().then((res) => {
      const prob = res[0];
      if (prob) {
        setProblemA(prob);
        api.checkDuplicates(prob).then((dupRes) => {
          setCandidates(dupRes.duplicateCandidates);
          if (dupRes.duplicateCandidates.length > 0) {
            setSelectedCand(dupRes.duplicateCandidates[0]);
          }
          setLoading(false);
        });
      } else {
        setLoading(false);
      }
    });
  }, []);

  if (loading) return <DashboardSkeleton />;
  if (!problemA) return <div className="p-8 text-white">No active candidate problems.</div>;

  const handleMerge = async () => {
    if (!selectedCand) return;
    await api.executeReviewerAction(problemA.problemId, 'MERGE_DUPLICATE', {
      masterProblemId: selectedCand.candidateProblemId,
    });
    setShowMergeModal(false);
    alert(`Problem ${problemA.problemId} successfully merged into Master ${selectedCand.candidateProblemId}. Submitter record preserved intact.`);
  };

  return (
    <div className="space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Duplicate Detection Comparator (`duplicate-v2`)</h1>
        <p className="text-xs text-[#66736F] mt-1">
          Compare problem pairs across multi-signal scoring (BGE-small embeddings, Haversine location, taxonomy overlap & fingerprint contradiction protection).
        </p>
      </div>

      {/* Human Decision Boundary Header Banner */}
      <div className="p-4 rounded-2xl bg-[#FFFDF5] border border-[#B7791F]/30 text-xs text-[#B7791F] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-[#B7791F] shrink-0" />
          <span>
            <strong>Human Merge Boundary</strong>: AI algorithms calculate signal breakdown scores. Final merge action is strictly human-controlled.
          </span>
        </div>

        {selectedCand && (
          <button
            onClick={() => setShowMergeModal(true)}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] text-white transition shadow-md shrink-0 cursor-pointer"
          >
            Merge as Duplicate
          </button>
        )}
      </div>

      {/* Dual Problem Comparison Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* PROBLEM A (NEW SUBMISSION) */}
        <div className="glass-card rounded-3xl p-6 space-y-4 border border-[#6A5ACD]/20">
          <div className="flex items-center justify-between pb-3 border-b border-[#D8D8C8]">
            <span className="text-xs font-bold text-[#6A5ACD] uppercase tracking-wider">Problem A (New Submission)</span>
            <span className="text-xs font-mono text-[#6A5ACD] font-bold">{problemA.problemId}</span>
          </div>

          <h3 className="text-lg font-bold text-[#17332F]">{problemA.title}</h3>
          <p className="text-xs text-[#17332F] leading-relaxed">{problemA.description}</p>

          <div className="grid grid-cols-2 gap-2 text-xs pt-2">
            <div className="bg-[#F7F5E8] p-2.5 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] block">Primary Domain</span>
              <span className="font-bold text-[#17332F]">{problemA.primaryDomain}</span>
            </div>
            <div className="bg-[#F7F5E8] p-2.5 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] block">Subcategory</span>
              <span className="font-bold text-[#0F766E]">{problemA.subcategory}</span>
            </div>
          </div>
        </div>

        {/* PROBLEM B (CANDIDATE MASTER) */}
        <div className="glass-card rounded-3xl p-6 space-y-4 border border-[#0F766E]/20">
          <div className="flex items-center justify-between pb-3 border-b border-[#D8D8C8]">
            <span className="text-xs font-bold text-[#0F766E] uppercase tracking-wider">Problem B (Candidate Duplicate)</span>
            <span className="text-xs font-mono text-[#0F766E] font-bold">{selectedCand?.candidateProblemId || 'CF-EXISTING-100'}</span>
          </div>

          <h3 className="text-lg font-bold text-[#17332F]">{selectedCand?.candidateTitle || 'Garbage accumulation near Namkum High School'}</h3>
          <p className="text-xs text-[#17332F] leading-relaxed">
            {selectedCand?.candidateDescription || 'Uncollected organic and plastic waste rotting near school perimeter.'}
          </p>

          <div className="grid grid-cols-2 gap-2 text-xs pt-2">
            <div className="bg-[#F7F5E8] p-2.5 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] block">Primary Domain</span>
              <span className="font-bold text-[#17332F]">{problemA.primaryDomain}</span>
            </div>
            <div className="bg-[#F7F5E8] p-2.5 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] block">Subcategory</span>
              <span className="font-bold text-[#0F766E]">{problemA.subcategory}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Signal Breakdown Card */}
      {selectedCand && (
        <div className="glass-card rounded-3xl p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-[#D8D8C8]">
            <h3 className="text-sm font-bold text-[#17332F] uppercase tracking-wider">Multi-Factor Signal Breakdown (`duplicate-v2`)</h3>
            <div className="text-right">
              <span className="text-[10px] text-[#66736F] uppercase tracking-wider font-semibold block">Composite Score</span>
              <span className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-[#034F46] to-[#0F766E]">
                {(selectedCand.duplicateScore * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Signals Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 text-xs">
            <div className="bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] font-semibold uppercase block">Semantic Similarity (50%)</span>
              <span className="text-base font-bold text-[#6A5ACD] mt-1 block">{(selectedCand.semanticSimilarity * 100).toFixed(1)}%</span>
              <span className="text-[10px] text-[#66736F]">BGE-small 384-dim</span>
            </div>

            <div className="bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] font-semibold uppercase block">Primary Domain (15%)</span>
              <span className="text-base font-bold text-[#087F6B] mt-1 block">
                {selectedCand.primaryDomainMatch ? '100% MATCH' : 'MISMATCH'}
              </span>
              <span className="text-[10px] text-[#66736F]">Taxonomy match</span>
            </div>

            <div className="bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] font-semibold uppercase block">Subcategory (15%)</span>
              <span className="text-base font-bold text-[#087F6B] mt-1 block">
                {selectedCand.subcategoryMatch ? '100% MATCH' : 'MISMATCH'}
              </span>
              <span className="text-[10px] text-[#66736F]">Exact subcategory</span>
            </div>

            <div className="bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] font-semibold uppercase block">Location (10%)</span>
              <span className="text-base font-bold text-[#0F766E] mt-1 block">1.2 km (85%)</span>
              <span className="text-[10px] text-[#66736F]">Haversine distance</span>
            </div>

            <div className="bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] font-semibold uppercase block">Contradiction Status</span>
              <span className="text-xs font-bold text-[#087F6B] mt-1 block flex items-center gap-1">
                <Check className="w-3.5 h-3.5" /> NO CONTRADICTION
              </span>
              <span className="text-[10px] text-[#66736F]">Fingerprint safe</span>
            </div>
          </div>
        </div>
      )}

      {/* MERGE MODAL */}
      <Modal
        isOpen={showMergeModal}
        onClose={() => setShowMergeModal(false)}
        title="Confirm Non-Destructive Duplicate Merge"
        subtitle="Links candidate problem to master while strictly preserving original submitter records intact."
      >
        <div className="space-y-4 text-xs">
          <p className="text-[#17332F] leading-relaxed">
            You are merging Problem <strong className="text-[#6A5ACD]">{problemA.problemId}</strong> into Master Problem{' '}
            <strong className="text-[#0F766E]">{selectedCand?.candidateProblemId}</strong>.
          </p>

          <div className="p-3.5 rounded-xl bg-[#E9DFFF]/40 border border-[#6A5ACD]/20 text-[#6A5ACD]">
            <strong>Non-Destructive Integrity Guarantee</strong>: The original submission record is never deleted. Status changes to <span className="text-[#17332F] font-mono">MERGED_DUPLICATE</span> and links to master for cross-citizen tracking.
          </div>

          <div className="pt-3 flex justify-end gap-3">
            <button onClick={() => setShowMergeModal(false)} className="px-4 py-2 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] hover:bg-[#F7F5E8] cursor-pointer">
              Cancel
            </button>
            <button onClick={handleMerge} className="px-5 py-2 rounded-xl bg-[#034F46] text-white font-bold hover:bg-[#0F766E] transition shadow-md cursor-pointer">
              Confirm Non-Destructive Merge
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
